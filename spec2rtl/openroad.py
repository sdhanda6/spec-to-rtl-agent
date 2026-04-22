from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from spec2rtl.collateral import CollateralBundle
from spec2rtl.qor import extract_qor_metrics, extract_synth_metrics
from spec2rtl.signoff import detect_signoff_tools, run_drc_check, run_lvs_check, summarize_signoff_results


OpenROADRunResult = dict


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

    if env["flow_dir"] is None or env["make_bin"] is None:
        return {
            "attempted": False,
            "passed": False,
            "succeeded": False,
            "status": "missing_tool",
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
            "qor_metrics": {},
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
    proc = subprocess.run(command, capture_output=True, text=True)
    report_paths = discover_qor_artifacts(env["flow_root"], platform_name, design)
    artifacts = _flatten_artifacts(report_paths)
    if platform and design_name:
        qor_metrics = extract_synth_metrics(env["flow_root"], platform_name, design) if target == "synth" else extract_qor_metrics(env["flow_root"], platform_name, design)
    else:
        qor_metrics = {}
    signoff = {"status": "not_run", "notes": ["signoff disabled or not applicable"]}
    if proc.returncode == 0 and target != "synth" and os.environ.get("SPEC2RTL_RUN_SIGNOFF") == "1":
        signoff = _run_signoff(report_paths, design_config, design)
    failure_kind = classify_openroad_failure(proc.stdout, proc.stderr, proc.returncode, target)
    return {
        "attempted": True,
        "passed": proc.returncode == 0,
        "succeeded": proc.returncode == 0,
        "status": "pass" if proc.returncode == 0 else "fail",
        "failure_kind": failure_kind,
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
        "qor_metrics": qor_metrics,
        "environment": env,
        "signoff": signoff,
        "message": (proc.stdout + ("\n" + proc.stderr if proc.stderr else "")).strip(),
    }


def discover_qor_artifacts(flow_root: Path, platform: str, design_name: str) -> dict:
    flow_dir = _flow_make_dir(_normalize_flow_root(flow_root))
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
    platform_dir = flow_dir / "platforms" / platform
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


def run_openroad_flow(root: Path, bundle: CollateralBundle, env: dict, mode: str, attempt: int = 1) -> dict:
    log_dir = root / "build" / "flow" / bundle.top / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"openroad_{mode}_attempt_{attempt}.log"
    flow_root = env.get("flow_root")
    if flow_root is None:
        result = {
            "attempted": False,
            "passed": False,
            "succeeded": False,
            "status": "missing_tool",
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "target": "synth" if mode == "synth" else "finish",
            "platform": bundle.platform,
            "design_name": bundle.top,
            "report_paths": {},
            "artifact_paths": {},
            "artifacts": [],
            "qor_metrics": {},
            "environment": env,
            "signoff": {"status": "not_run", "notes": ["OpenROAD flow root was not detected"]},
            "message": "; ".join(env.get("messages", [])),
        }
        result["log_path"] = None
        result["log_paths"] = []
        return result

    result = run_openroad_stage(flow_root, bundle.config_mk, "synth" if mode == "synth" else "finish")
    combined = (result.get("stdout", "") + ("\n" + result.get("stderr", "") if result.get("stderr") else "")).strip()
    log_path.write_text(combined + ("\n" if combined else ""), encoding="utf-8")
    result["requested_mode"] = mode
    result["log_path"] = log_path
    result["log_paths"] = [log_path]
    return result


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
