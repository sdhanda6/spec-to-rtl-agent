from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from spec2rtl.collateral import CollateralBundle, DEFAULT_CLOCK_PERIOD_NS
from spec2rtl.qor import extract_qor_metrics, extract_synth_metrics
from spec2rtl.signoff import detect_signoff_tools, run_drc_check, run_lvs_check, summarize_signoff_results


OpenROADRunResult = dict
ROOT = Path(__file__).resolve().parents[1]


def classify_openroad_failure(stdout: str, stderr: str, returncode: int | None, target: str) -> str | None:
    text = "\n".join(part for part in [stdout, stderr] if part).lower()
    if returncode in {None, 0}:
        return None
    infra_tokens = [
        "read-only file system",
        "cannot write",
        "permission denied",
        "operation not permitted",
    ]
    if any(token in text for token in infra_tokens):
        return "infrastructure"
    if target == "synth":
        return "tool_error"
    return "logical"


def _extract_openroad_failure_reason(stdout: str, stderr: str, returncode: int | None) -> str | None:
    if returncode in {None, 0}:
        return None
    text = "\n".join(part for part in [stdout, stderr] if part)
    candidates = []
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if not stripped or "warning" in lowered:
            continue
        if any(token in lowered for token in ["error", "fatal", "failed", "cannot", "permission denied"]):
            candidates.append(stripped)
    if candidates:
        return candidates[-1]
    return f"OpenROAD exited with return code {returncode}"


def _validate_synthesized_netlist(netlist_path: Path | str | None, expected_top: str | None) -> dict:
    if isinstance(netlist_path, str):
        netlist_path = Path(netlist_path)
    check = {
        "valid": False,
        "reason": "synthesized netlist was not found",
        "path": netlist_path.as_posix() if isinstance(netlist_path, Path) else None,
        "expected_top": expected_top,
        "module_found": False,
        "module_count": 0,
        "mapped_cell_count": 0,
        "assign_count": 0,
        "always_count": 0,
        "statement_count": 0,
        "line_count": 0,
        "size_bytes": 0,
    }
    if not isinstance(netlist_path, Path) or not netlist_path.exists():
        return check
    try:
        text = netlist_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        check["reason"] = f"could not read synthesized netlist: {exc}"
        return check

    stripped_text = text.strip()
    check["line_count"] = len(text.splitlines())
    check["size_bytes"] = netlist_path.stat().st_size
    if not stripped_text:
        check["reason"] = "synthesized netlist is empty"
        return check

    clean_text = _strip_verilog_comments(text)
    module_bodies = _verilog_module_bodies(clean_text)
    check["module_count"] = len(module_bodies)
    if not module_bodies:
        check["reason"] = "synthesized netlist contains no modules"
        return check

    normalized_top = _normalize_verilog_identifier(expected_top) if expected_top else None
    if normalized_top:
        body = module_bodies.get(normalized_top)
        if body is None:
            check["reason"] = f"synthesized netlist does not contain expected top module {expected_top}"
            return check
    else:
        normalized_top, body = next(iter(module_bodies.items()))

    check["module_found"] = True
    cell_instances = _mapped_cell_instances(body)
    assign_count = len(re.findall(r"^\s*assign\b", body, flags=re.MULTILINE))
    always_count = len(re.findall(r"^\s*always\b", body, flags=re.MULTILINE))
    statement_count = len(cell_instances) + assign_count + always_count
    check["mapped_cell_count"] = len(cell_instances)
    check["assign_count"] = assign_count
    check["always_count"] = always_count
    check["statement_count"] = statement_count

    if statement_count == 0:
        check["reason"] = f"synthesized top module {normalized_top} contains no logic statements"
        return check
    if not cell_instances:
        check["reason"] = f"synthesized top module {normalized_top} contains no mapped cell instances"
        return check

    check["valid"] = True
    check["reason"] = None
    return check


def _strip_verilog_comments(text: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", without_block_comments)


def _verilog_module_bodies(text: str) -> dict[str, str]:
    modules: dict[str, str] = {}
    pattern = re.compile(r"\bmodule\s+(?P<name>\\\S+|[A-Za-z_][A-Za-z0-9_$]*)", flags=re.MULTILINE)
    matches = list(pattern.finditer(text))
    for match in matches:
        module_name = _normalize_verilog_identifier(match.group("name"))
        end = text.find("endmodule", match.end())
        if end == -1:
            body = text[match.end() :]
        else:
            body = text[match.end() : end]
        modules[module_name] = body
    return modules


def _normalize_verilog_identifier(name: str | None) -> str | None:
    if name is None:
        return None
    cleaned = name.strip()
    if cleaned.startswith("\\"):
        cleaned = cleaned[1:].split()[0]
    return cleaned


def _mapped_cell_instances(module_body: str) -> list[tuple[str, str]]:
    instance_pattern = re.compile(
        r"^\s*(?P<cell>\\?\$?[A-Za-z_][A-Za-z0-9_$]*(?:__[A-Za-z0-9_$]+)?)\s+"
        r"(?P<instance>\\?[A-Za-z_][A-Za-z0-9_$]*|_[A-Za-z0-9_$]+_?)\s*\(",
        flags=re.MULTILINE,
    )
    keywords = {"assign", "always", "begin", "case", "else", "for", "function", "if", "initial", "task"}
    instances: list[tuple[str, str]] = []
    for match in instance_pattern.finditer(module_body):
        cell = _normalize_verilog_identifier(match.group("cell")) or ""
        if cell.lower() in keywords:
            continue
        instances.append((cell, _normalize_verilog_identifier(match.group("instance")) or ""))
    return instances


def detect_openroad_environment() -> dict:
    cwd = Path.cwd()
    flow_root = _detect_flow_root(cwd)
    flow_dir = _flow_make_dir(flow_root) if flow_root else None
    env = {
        "openroad_bin": shutil.which("openroad"),
        "yosys_bin": shutil.which("yosys"),
        "make_bin": shutil.which("make"),
        "flow_root": flow_root,
        "flow_dir": flow_dir,
        "env_vars": {
            "OPENROAD_FLOW_ROOT": os.environ.get("OPENROAD_FLOW_ROOT"),
            "OPENROAD_FLOW_DIR": os.environ.get("OPENROAD_FLOW_DIR"),
            "PDK_ROOT": os.environ.get("PDK_ROOT"),
        },
        "messages": [],
    }
    if env["openroad_bin"] is None:
        env["messages"].append("openroad not found in PATH")
    if env["yosys_bin"] is None:
        env["messages"].append("yosys not found in PATH")
    if env["make_bin"] is None:
        env["messages"].append("make not found in PATH")
    if flow_root is None or flow_dir is None:
        env["messages"].append("OpenROAD-flow-scripts root not found; set OPENROAD_FLOW_ROOT or OPENROAD_FLOW_DIR")
    if not env["env_vars"]["PDK_ROOT"]:
        env["messages"].append("PDK_ROOT is not set")
    return env


def run_openroad_stage(flow_root: Path, design_config: Path, target: str) -> dict:
    env = detect_openroad_environment()
    env["flow_root"] = _normalize_flow_root(flow_root)
    env["flow_dir"] = _flow_make_dir(env["flow_root"])
    platform, design_name = _read_design_identity(design_config)
    platform_name = platform or "sky130hd"
    design = design_name or design_config.stem
    config_vars = _read_config_vars(design_config)
    _ensure_design_config_sdc(design_config)

    if env["flow_dir"] is None or env["make_bin"] is None:
        stage_tracking = _physical_stage_tracking({}, "not_supported", target)
        netlist_check = {
            "valid": False,
            "reason": "; ".join(env.get("messages", [])) or "OpenROAD environment is incomplete",
            "path": None,
            "expected_top": design_name,
        }
        return {
            "attempted": False,
            "passed": False,
            "succeeded": False,
            "status": "not_supported",
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "target": target,
            "platform": platform,
            "design_name": design_name,
            "report_paths": {},
            "artifact_paths": {},
            "artifacts": [],
            "netlist_check": netlist_check,
            "stage_tracking": stage_tracking,
            "physical_stages": stage_tracking["stages"],
            "qor_metrics": {},
            "qor_extraction_error": None,
            "failure_reason": "; ".join(env.get("messages", [])) or "OpenROAD environment is incomplete",
            "partial_results_available": False,
            "environment": env,
            "signoff": {
                "status": "not_run",
                "notes": ["OpenROAD environment is incomplete"],
            },
            "message": "; ".join(env.get("messages", [])),
        }

    command = [
        str(env["make_bin"]),
        "-C",
        str(env["flow_dir"]),
        f"DESIGN_CONFIG={design_config.as_posix()}",
        target,
    ]
    work_root, work_dirs = _prepare_orfs_work_root(design)
    proc_env = os.environ.copy()
    proc_env["FLOW_HOME"] = str(env["flow_dir"])
    proc_env["WORK_HOME"] = str(work_root)
    proc_env["RESULTS_DIR"] = str(work_dirs["results"])
    proc_env["REPORTS_DIR"] = str(work_dirs["reports"])
    proc_env["LOG_DIR"] = str(work_dirs["logs"])
    proc_env.setdefault("QT_QPA_PLATFORM", "offscreen")
    activity_file = _prepare_activity_file_for_openroad(
        design=design,
        platform=platform_name,
        config_vars=config_vars,
        design_config=design_config,
        work_dirs=work_dirs,
    )
    if activity_file is not None:
        proc_env["ACTIVITY_FILE"] = str(activity_file)
    proc_env["REPORT_POWER"] = _clean_config_value(config_vars.get("REPORT_POWER")) or ("1" if target != "synth" else "0")
    activity_scope = _clean_config_value(config_vars.get("ACTIVITY_SCOPE")) or f"tb_{design}/dut"
    proc_env["ACTIVITY_SCOPE"] = _expand_make_vars(
        activity_scope,
        {
            "DESIGN_NAME": design,
            "TOP_MODULE": design,
            "PLATFORM": platform_name,
        },
    )
    proc = subprocess.run(command, capture_output=True, text=True, env=proc_env)
    artifact_root = _copy_orfs_outputs_to_build(design, work_root)
    report_paths = discover_qor_artifacts(artifact_root, platform_name, design, platform_flow_root=env["flow_root"])
    artifacts = _flatten_artifacts(report_paths)
    netlist_check = _validate_synthesized_netlist(report_paths.get("synthesized_netlist"), design)
    flow_succeeded = proc.returncode == 0
    netlist_succeeded = bool(netlist_check.get("valid"))
    effective_success = flow_succeeded and netlist_succeeded
    stage_tracking = _physical_stage_tracking(report_paths, "pass" if effective_success else "fail", target)
    qor_metrics = {}
    qor_extraction_error = None
    if platform and design_name:
        qor_metrics, qor_extraction_error = _extract_available_qor_metrics(artifact_root, platform_name, design, target)
    signoff = {"status": "not_run", "notes": ["signoff disabled or not applicable"]}
    if effective_success and target != "synth" and os.environ.get("SPEC2RTL_RUN_SIGNOFF") == "1":
        signoff = _run_signoff(report_paths, design_config, design)
    failure_kind = classify_openroad_failure(proc.stdout, proc.stderr, proc.returncode, target)
    failure_reason = _extract_openroad_failure_reason(proc.stdout, proc.stderr, proc.returncode)
    if not netlist_succeeded and flow_succeeded:
        failure_kind = "logical"
        failure_reason = str(netlist_check.get("reason") or "synthesized netlist failed validation")
    elif not netlist_succeeded and not failure_reason:
        failure_reason = str(netlist_check.get("reason") or "synthesized netlist failed validation")
    return {
        "attempted": True,
        "passed": effective_success,
        "succeeded": effective_success,
        "status": "pass" if effective_success else "fail",
        "failure_kind": failure_kind,
        "failure_reason": failure_reason,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "target": target,
        "platform": platform,
        "design_name": design_name,
        "synthesized_netlist_path": report_paths.get("synthesized_netlist"),
        "synth_stats_path": next((path for path in report_paths.get("reports", []) if path.name == "synth_stat.txt"), None),
        "report_paths": report_paths,
        "artifact_paths": report_paths,
        "artifacts": artifacts,
        "netlist_check": netlist_check,
        "stage_tracking": stage_tracking,
        "physical_stages": stage_tracking["stages"],
        "artifact_root": artifact_root,
        "artifact_collection": "current_run",
        "activity_file": activity_file,
        "qor_metrics": qor_metrics,
        "qor_extraction_error": qor_extraction_error,
        "partial_results_available": bool(artifacts),
        "environment": env,
        "signoff": signoff,
        "message": (proc.stdout + ("\n" + proc.stderr if proc.stderr else "")).strip(),
    }


def discover_qor_artifacts(flow_root: Path, platform: str, design_name: str, platform_flow_root: Path | None = None) -> dict:
    flow_dir = _artifact_output_dir(flow_root)
    grouped = {
        "reports": [],
        "results": [],
        "logs": [],
        "other": [],
        "final_gds": None,
        "final_def": None,
        "final_netlist": None,
        "synthesized_netlist": None,
        "layout_netlist": None,
        "tech_lef": None,
        "merged_lef": None,
        "schematic_netlist": None,
    }
    if flow_dir is None:
        return grouped

    for label in ["reports", "results", "logs"]:
        base = flow_dir / label / platform / design_name / "base"
        if base.exists():
            grouped[label] = sorted(path for path in base.rglob("*") if path.is_file())

    result_dir = flow_dir / "results" / platform / design_name / "base"
    platform_base = _flow_make_dir(_normalize_flow_root(platform_flow_root or flow_root))
    platform_dir = (platform_base or flow_dir) / "platforms" / platform
    grouped["final_gds"] = _first_existing([result_dir / "6_final.gds", result_dir / "6_1_merged.gds"])
    grouped["final_def"] = _first_existing([result_dir / "6_final.def", result_dir / "5_route.def"])
    grouped["final_netlist"] = _first_existing([result_dir / "6_final.v", result_dir / "5_route.v", result_dir / "4_cts.v"])
    grouped["synthesized_netlist"] = _first_existing([result_dir / "1_2_yosys.v", result_dir / "1_synth.v", result_dir / "1_synth.vg"])
    grouped["layout_netlist"] = grouped["final_netlist"]
    lef_dir = platform_dir / "lef"
    tech_candidates = [
        lef_dir / f"{platform}.tlef",
        lef_dir / f"{platform}_tech.lef",
    ]
    merged_candidates = [
        lef_dir / f"{platform}_merged.lef",
        lef_dir / f"{platform}.lef",
    ]
    if lef_dir.exists():
        tech_candidates.extend(sorted(lef_dir.glob("*.tlef")))
        merged_candidates.extend(sorted(lef_dir.glob("*merged.lef")))
        merged_candidates.extend(sorted(lef_dir.glob("*.lef")))
    grouped["tech_lef"] = _first_existing(tech_candidates)
    grouped["merged_lef"] = _first_existing(merged_candidates)
    return grouped


def _physical_stage_tracking(report_paths: dict, overall_status: str, target: str) -> dict:
    order = ["floorplan", "power_planning", "placement", "cts", "routing", "sta", "finish"]
    if target == "synth":
        stages = {
            stage: {"status": "not_run", "evidence_paths": [], "message": "stage is outside synthesis-only target"}
            for stage in order
        }
        return {"order": order, "stages": stages, "target": target}
    if overall_status == "not_supported":
        stages = {
            stage: {"status": "not_supported", "evidence_paths": [], "message": "OpenROAD flow is not supported in this environment"}
            for stage in order
        }
        return {"order": order, "stages": stages, "target": target}

    patterns = {
        "floorplan": ["2_1_floorplan", "2_2_floorplan_macro", "2_3_floorplan_tapcell", "2_floorplan"],
        "power_planning": ["2_4_floorplan_pdn", "pdn"],
        "placement": ["3_1_place", "3_2_place", "3_3_place", "3_4_place", "3_5_place", "3_place", "global_place", "detailed_place"],
        "cts": ["4_1_cts", "4_cts", "cts_"],
        "routing": ["5_1_grt", "5_2_route", "5_3_fillcell", "5_route", "global_route", "route.guide", "routing"],
        "sta": ["6_report", "6_finish", "qor_summary", "worst_path", "final_clocks"],
        "finish": ["6_final", "6_1_merged", "6_1_fill", "final_"],
    }
    stages: dict[str, dict[str, object]] = {}
    first_missing_seen = False
    for stage in order:
        evidence = _stage_evidence(report_paths, patterns[stage])
        if evidence:
            status = "pass"
        elif overall_status == "pass":
            status = "fail"
        elif first_missing_seen:
            status = "not_run"
        else:
            status = "fail"
            first_missing_seen = True
        stages[stage] = {
            "status": status,
            "evidence_paths": [path.as_posix() for path in evidence],
            "message": "stage evidence found" if evidence else "stage evidence not found",
        }
    return {"order": order, "stages": stages, "target": target}


def _stage_evidence(report_paths: dict, name_patterns: list[str]) -> list[Path]:
    candidates: list[Path] = []
    for value in report_paths.values():
        if isinstance(value, list):
            candidates.extend(path for path in value if isinstance(path, Path))
        elif isinstance(value, Path):
            candidates.append(value)
    evidence = []
    for path in candidates:
        path_text = path.as_posix().lower()
        name_text = path.name.lower()
        if any(pattern.lower() in name_text or pattern.lower() in path_text for pattern in name_patterns):
            evidence.append(path)
    ordered: list[Path] = []
    seen: set[str] = set()
    for path in evidence:
        key = path.as_posix()
        if key not in seen:
            ordered.append(path)
            seen.add(key)
    return ordered


def run_openroad_flow(root: Path, bundle: CollateralBundle, env: dict, mode: str, attempt: int = 1) -> dict:
    log_dir = root / "build" / "flow" / bundle.top / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"openroad_{mode}_attempt_{attempt}.log"
    flow_root = env.get("flow_root")
    _ensure_design_config_sdc(
        bundle.config_mk,
        preferred_clock_port=bundle.clock_port,
        preferred_clock_period=bundle.clock_period_ns,
    )
    if flow_root is None:
        stage_tracking = _physical_stage_tracking({}, "not_supported", "finish")
        netlist_check = {
            "valid": False,
            "reason": "; ".join(env.get("messages", [])) or "OpenROAD flow root was not detected",
            "path": None,
            "expected_top": bundle.top,
        }
        result = {
            "attempted": False,
            "passed": False,
            "succeeded": False,
            "status": "not_supported",
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "target": "finish",
            "requested_mode": mode,
            "platform": bundle.platform,
            "design_name": bundle.top,
            "report_paths": {},
            "artifact_paths": {},
            "artifacts": [],
            "netlist_check": netlist_check,
            "stage_tracking": stage_tracking,
            "physical_stages": stage_tracking["stages"],
            "qor_metrics": {},
            "failure_reason": "; ".join(env.get("messages", [])) or "OpenROAD flow root was not detected",
            "partial_results_available": False,
            "environment": env,
            "signoff": {"status": "not_run", "notes": ["OpenROAD flow root was not detected"]},
            "message": "; ".join(env.get("messages", [])),
        }
        result["log_path"] = None
        result["log_paths"] = []
        return result

    result = run_openroad_stage(flow_root, bundle.config_mk, "finish")
    combined = (result.get("stdout", "") + ("\n" + result.get("stderr", "") if result.get("stderr") else "")).strip()
    log_path.write_text(combined + ("\n" if combined else ""), encoding="utf-8")
    result["requested_mode"] = mode
    result["log_path"] = log_path
    result["log_paths"] = [log_path]
    return result


def _ensure_design_config_sdc(
    design_config: Path,
    preferred_clock_port: str | None = None,
    preferred_clock_period: str | None = None,
) -> Path | None:
    config_vars = _read_config_vars(design_config)
    sdc_raw = config_vars.get("SDC_FILE")
    if not sdc_raw:
        return None

    sdc_path = _resolve_config_path(sdc_raw, design_config.parent)
    existing_text = ""
    if sdc_path.exists():
        existing_text = sdc_path.read_text(encoding="utf-8", errors="ignore")
        if "create_clock" in existing_text:
            return sdc_path

    clock_period = _clean_config_value(preferred_clock_period) or _clean_config_value(config_vars.get("CLOCK_PERIOD")) or DEFAULT_CLOCK_PERIOD_NS
    clock_port = _clean_config_value(preferred_clock_port) or _clean_config_value(config_vars.get("CLOCK_PORT"))
    if not clock_port:
        clock_port = _infer_clock_port_from_verilog(config_vars.get("VERILOG_FILES", ""), design_config.parent)

    sdc_path.parent.mkdir(parents=True, exist_ok=True)
    sdc_path.write_text(_render_clocked_sdc(clock_port, clock_period, existing_text), encoding="utf-8")
    return sdc_path


def _extract_available_qor_metrics(
    artifact_root: Path,
    platform: str,
    design: str,
    target: str,
) -> tuple[dict, str | None]:
    try:
        if target == "synth":
            return extract_synth_metrics(artifact_root, platform, design), None
        return extract_qor_metrics(artifact_root, platform, design), None
    except Exception as exc:
        return {}, str(exc)


def _read_config_vars(config_path: Path) -> dict[str, str]:
    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    vars_map: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("export "):
            continue
        if ":=" in stripped:
            lhs, rhs = stripped.split(":=", 1)
        elif "?=" in stripped:
            lhs, rhs = stripped.split("?=", 1)
        elif "=" in stripped:
            lhs, rhs = stripped.split("=", 1)
        else:
            continue
        name = lhs.replace("export", "", 1).strip()
        vars_map[name] = rhs.strip()
    return vars_map


def _prepare_activity_file_for_openroad(
    design: str,
    platform: str,
    config_vars: dict[str, str],
    design_config: Path,
    work_dirs: dict[str, Path],
) -> Path | None:
    raw_activity = _clean_config_value(config_vars.get("ACTIVITY_FILE"))
    if raw_activity is None:
        return None
    flow_variant = _clean_config_value(config_vars.get("FLOW_VARIANT")) or "base"
    design_nickname = _clean_config_value(config_vars.get("DESIGN_NICKNAME")) or design
    orfs_results_dir = work_dirs["results"] / platform / design_nickname / flow_variant
    expanded = _expand_make_vars(
        raw_activity,
        {
            "RESULTS_DIR": orfs_results_dir.as_posix(),
            "DESIGN_DIR": design_config.parent.as_posix(),
            "DESIGN_NAME": design,
            "TOP_MODULE": design,
            "PLATFORM": platform,
        },
    )
    activity_file = _resolve_config_path(expanded, design_config.parent)
    source = _find_existing_activity_source(design, activity_file, design_config)
    if source is not None:
        activity_file.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != activity_file.resolve():
            shutil.copyfile(source, activity_file)
    return activity_file


def _find_existing_activity_source(design: str, activity_file: Path, design_config: Path) -> Path | None:
    candidates = [
        ROOT / "build" / "flow" / design / "waves.vcd",
        design_config.parent.parent / "waves.vcd",
        activity_file,
        ROOT / "waves.vcd",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _expand_make_vars(text: str, values: dict[str, str]) -> str:
    expanded = text
    for name, value in values.items():
        expanded = expanded.replace(f"$({name})", value)
        expanded = expanded.replace(f"${{{name}}}", value)
        expanded = expanded.replace(f"${name}", value)
    return expanded


def _infer_clock_port_from_verilog(verilog_files: str, base_dir: Path) -> str | None:
    candidates: list[str] = []
    for token in verilog_files.split():
        rtl_path = _resolve_config_path(token, base_dir)
        if not rtl_path.exists() or not rtl_path.is_file():
            continue
        candidates.extend(_input_ports_from_verilog(rtl_path))
    for name in candidates:
        if name.lower() in {"clk", "clock"}:
            return name
    return candidates[0] if candidates else None


def _input_ports_from_verilog(rtl_path: Path) -> list[str]:
    try:
        text = rtl_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    pattern = re.compile(
        r"\binput\b\s+(?:(?:wire|reg|logic|signed|unsigned)\s+)*(?:\[[^\]]+\]\s*)?(?P<name>[A-Za-z_][A-Za-z0-9_$]*)"
    )
    ports: list[str] = []
    for match in pattern.finditer(text):
        name = match.group("name")
        if name not in ports:
            ports.append(name)
    return ports


def _render_clocked_sdc(clock_port: str | None, clock_period: str, existing_text: str) -> str:
    lines = ["# Auto-generated timing constraints"]
    if clock_port:
        lines.append(f"create_clock -period {clock_period} [get_ports {_sdc_port_ref(clock_port)}]")
    else:
        lines.append(f"create_clock -period {clock_period} spec2rtl_virtual_clk")
    for line in existing_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "# Auto-generated timing constraints":
            continue
        if "No clock was inferred" in stripped:
            continue
        lines.append(line)
    lines.append("")
    return "\n".join(lines)


def _resolve_config_path(raw_path: str, base_dir: Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else base_dir / path


def _clean_config_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _sdc_port_ref(port_name: str) -> str:
    if any(char in port_name for char in "[]{} "):
        return "{" + port_name.replace("}", "\\}") + "}"
    return port_name


def _orfs_work_root(design: str) -> Path:
    return ROOT / f"build/orfs_work_{design}"


def _prepare_orfs_work_root(design: str) -> tuple[Path, dict[str, Path]]:
    work_root = _orfs_work_root(design)
    work_root.mkdir(parents=True, exist_ok=True)
    work_dirs = {
        "results": work_root / "results",
        "reports": work_root / "reports",
        "logs": work_root / "logs",
    }
    for path in work_dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return work_root, work_dirs


def _copy_orfs_outputs_to_build(design_name: str, work_root: Path) -> Path:
    snapshot_root = ROOT / "build" / "flow" / design_name
    snapshot_root.mkdir(parents=True, exist_ok=True)
    for label in ["results", "reports", "logs"]:
        source = work_root / label
        target = snapshot_root / label
        if source.exists():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            target.mkdir(parents=True, exist_ok=True)
    return snapshot_root


def _artifact_output_dir(flow_root: Path | None) -> Path | None:
    if flow_root is None:
        return None
    root = flow_root.expanduser()
    normalized = _normalize_flow_root(root)
    flow_dir = _flow_make_dir(normalized)
    if flow_dir is not None:
        return flow_dir
    if any((root / label).exists() for label in ["reports", "results", "logs"]):
        return root
    return None


def _run_signoff(report_paths: dict, design_config: Path, design_name: str) -> dict:
    tools = detect_signoff_tools()
    signoff_dir = design_config.parent.parent / "signoff"
    signoff_dir.mkdir(parents=True, exist_ok=True)
    drc = run_drc_check(
        gds_path=report_paths.get("final_gds") or Path("missing.gds"),
        tech_lef=report_paths.get("tech_lef") or Path("missing.tlef"),
        design_name=design_name,
        work_dir=signoff_dir / "drc",
    )
    schematic_netlist = _discover_schematic_netlist(design_config)
    if schematic_netlist is not None:
        report_paths["schematic_netlist"] = schematic_netlist
    lvs = run_lvs_check(
        layout_netlist=report_paths.get("layout_netlist") or Path("missing_layout_netlist.v"),
        schematic_netlist=report_paths.get("schematic_netlist") or schematic_netlist or Path("missing_schematic_netlist.v"),
        work_dir=signoff_dir / "lvs",
    )
    summary = summarize_signoff_results(
        {
            "drc": drc,
            "lvs": lvs,
            "signoff_tool_availability": {
                "magic": bool(tools.get("magic_available")),
                "netgen": bool(tools.get("netgen_available")),
                "magic_usable": bool(tools.get("magic_usable")),
                "netgen_usable": bool(tools.get("netgen_usable")),
                "magic_path": tools.get("magic_path"),
                "netgen_path": tools.get("netgen_path"),
            },
        }
    )
    summary["enabled"] = True
    summary["drc"] = drc
    summary["lvs"] = lvs
    return summary


def _detect_flow_root(root: Path) -> Path | None:
    for env_name in ["OPENROAD_FLOW_ROOT", "OPENROAD_FLOW_DIR"]:
        value = os.environ.get(env_name)
        if value:
            normalized = _normalize_flow_root(Path(value))
            if normalized:
                return normalized
    for candidate in [
        root / "OpenROAD-flow-scripts",
        root.parent / "OpenROAD-flow-scripts",
        root / "openroad-flow-scripts",
        root.parent / "openroad-flow-scripts",
        root / "flow",
    ]:
        normalized = _normalize_flow_root(candidate)
        if normalized:
            return normalized
    return None


def _normalize_flow_root(path: Path | None) -> Path | None:
    if path is None:
        return None
    resolved = path.expanduser()
    if not resolved.exists():
        return None
    if resolved.name == "flow" and (resolved / "Makefile").exists():
        return resolved.parent if (resolved.parent / "flow").exists() else resolved
    if (resolved / "flow" / "Makefile").exists():
        return resolved
    return None


def _flow_make_dir(flow_root: Path | None) -> Path | None:
    if flow_root is None:
        return None
    if flow_root.name == "flow" and (flow_root / "Makefile").exists():
        return flow_root
    candidate = flow_root / "flow"
    return candidate if (candidate / "Makefile").exists() else None


def _read_design_identity(config_path: Path) -> tuple[str | None, str | None]:
    platform = None
    design_name = None
    try:
        lines = config_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("export "):
            continue
        if ":=" in stripped:
            lhs, rhs = stripped.split(":=", 1)
        elif "?=" in stripped:
            lhs, rhs = stripped.split("?=", 1)
        elif "=" in stripped:
            lhs, rhs = stripped.split("=", 1)
        else:
            continue
        name = lhs.replace("export", "", 1).strip()
        value = rhs.strip()
        if name == "PLATFORM":
            platform = value
        elif name == "DESIGN_NAME":
            design_name = value
    return platform, design_name


def _flatten_artifacts(grouped: dict) -> list[Path]:
    paths: list[Path] = []
    for values in grouped.values():
        if isinstance(values, list):
            paths.extend(path for path in values if isinstance(path, Path))
        elif isinstance(values, Path):
            paths.append(values)
    ordered: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = path.as_posix()
        if key not in seen:
            seen.add(key)
            ordered.append(path)
    return ordered


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _discover_schematic_netlist(design_config: Path) -> Path | None:
    try:
        lines = design_config.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("export VERILOG_FILES"):
            continue
        if ":=" not in stripped:
            continue
        _, rhs = stripped.split(":=", 1)
        candidate = Path(rhs.strip().split()[0])
        if candidate.exists():
            return candidate
    return None
