from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_NETGENDIR = "/usr/share/netgen"
DEFAULT_NETGEN_LIBDIR = "/usr/lib/x86_64-linux-gnu/netgen"
DEFAULT_MAGIC_RCFALLBACKS = [
    "/usr/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc",
    "/usr/local/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc",
    "/usr/share/open_pdks/sky130A/libs.tech/magic/sky130A.magicrc",
    "/usr/local/share/open_pdks/sky130A/libs.tech/magic/sky130A.magicrc",
    "/opt/pdk/share/pdk/sky130A/libs.tech/magic/sky130A.magicrc",
    "/opt/open_pdks/sky130A/libs.tech/magic/sky130A.magicrc",
]
DEFAULT_NETGEN_SETUP_FALLBACKS = [
    "/usr/share/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl",
    "/usr/local/share/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl",
    "/usr/share/open_pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl",
    "/usr/local/share/open_pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl",
    "/opt/pdk/share/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl",
    "/opt/open_pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl",
]


def detect_signoff_tools() -> dict:
    magic_path = shutil.which("magic")
    netgen_path = shutil.which("netgen")
    magic_probe = _probe_magic_headless(magic_path)
    netgen_probe = _probe_netgen_batch(netgen_path)
    notes = []
    for label, probe in [("magic", magic_probe), ("netgen", netgen_probe)]:
        if probe["available"] and probe["usable"]:
            notes.append(f"{label} available and usable in headless/batch mode")
        elif probe["available"]:
            notes.append(f"{label} installed but unusable: {probe['reason']}")
        else:
            notes.append(f"{label} unavailable")
    return {
        "magic_available": magic_probe["available"],
        "netgen_available": netgen_probe["available"],
        "magic_usable": magic_probe["usable"],
        "netgen_usable": netgen_probe["usable"],
        "magic_path": magic_path,
        "netgen_path": netgen_path,
        "magic_probe": magic_probe,
        "netgen_probe": netgen_probe,
        "notes": "; ".join(notes),
    }


def run_drc_check(gds_path: Path, tech_lef: Path, design_name: str, work_dir: Path) -> dict:
    result = _empty_signoff_result()
    result["tool"] = "magic"
    result["design_name"] = design_name
    result["gds_path"] = gds_path.as_posix()
    result["tech_lef"] = tech_lef.as_posix() if tech_lef else None

    tools = detect_signoff_tools()
    result["signoff_tool_availability"] = _tool_availability(tools)
    report_path = work_dir / "magic_drc.rpt"
    script_path = work_dir / "magic_drc.tcl"
    result["signoff_reports"] = [report_path.as_posix()]
    result["signoff_artifacts"] = [script_path.as_posix(), report_path.as_posix()]

    missing = [path.as_posix() for path in [gds_path, tech_lef] if path is None or not path.exists()]
    if missing:
        result.update({"drc_status": "missing_input", "notes": [f"missing required DRC inputs: {', '.join(missing)}"]})
        return result

    if not tools.get("magic_available"):
        result.update({"drc_status": "unsupported", "notes": ["magic not found in PATH"]})
        return result
    if not tools.get("magic_usable"):
        result.update({"drc_status": "unsupported", "notes": [f"magic installed but not headless-usable: {tools.get('magic_probe', {}).get('reason', 'probe failed')}"]})
        return result

    magic_rc = _find_magic_rcfile(tech_lef)
    result["magic_rcfile_used"] = magic_rc.as_posix() if magic_rc else None
    if magic_rc is None:
        result.update({"drc_status": "partial", "notes": [f"could not find a Magic rcfile near {tech_lef.as_posix()}"]})
        return result

    work_dir.mkdir(parents=True, exist_ok=True)
    script_body = "\n".join(
        [
            "crashbackups stop",
            "drc off",
            f'gds read "{gds_path.as_posix()}"',
            f'load "{design_name}"',
            "select top cell",
            "drc on",
            "drc check",
            "drc catchup",
            f'set fout [open "{report_path.as_posix()}" "w"]',
            'set violations [drc listall why]',
            'puts $fout "MAGIC_DRC_BEGIN"',
            'foreach item $violations { puts $fout $item }',
            'puts $fout "MAGIC_DRC_END"',
            "close $fout",
            "quit -noprompt",
            "",
        ]
    )
    script_path.write_text(script_body, encoding="utf-8")

    command = [str(tools["magic_path"]), "-dnull", "-noconsole", "-rcfile", str(magic_rc)]
    proc = subprocess.run(command, input=script_body, capture_output=True, text=True, cwd=work_dir)
    parsed = parse_magic_drc_report(report_path)
    status = "pass"
    if proc.returncode != 0:
        status = "tool_error"
    elif parsed["drc_violation_count"] > 0:
        status = "fail"
    elif not report_path.exists():
        status = "partial"
    result.update(
        {
            "drc_status": status,
            "drc_violation_count": parsed["drc_violation_count"],
            "drc_violations": parsed.get("violations", []),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "command": " ".join(command),
            "notes": parsed.get("notes", []),
        }
    )
    if proc.returncode != 0:
        result["notes"].append("magic DRC command failed")
    return result


def run_lvs_check(layout_netlist: Path, schematic_netlist: Path, work_dir: Path) -> dict:
    result = _empty_signoff_result()
    result["tool"] = "netgen"
    result["layout_netlist"] = layout_netlist.as_posix()
    result["schematic_netlist"] = schematic_netlist.as_posix()

    tools = detect_signoff_tools()
    result["signoff_tool_availability"] = _tool_availability(tools)
    env = _build_netgen_env()
    result["netgen_env_used"] = {
        "NETGENDIR": env.get("NETGENDIR"),
        "LD_LIBRARY_PATH": env.get("LD_LIBRARY_PATH"),
        "OMPI_MCA_plm": env.get("OMPI_MCA_plm"),
        "OMPI_MCA_btl": env.get("OMPI_MCA_btl"),
    }
    report_path = work_dir / "netgen_lvs.rpt"
    script_path = work_dir / "netgen_lvs.tcl"
    setup_path = _find_netgen_setup(layout_netlist, schematic_netlist)
    result["signoff_reports"] = [report_path.as_posix()]
    result["signoff_artifacts"] = [script_path.as_posix(), report_path.as_posix()] + ([setup_path.as_posix()] if setup_path else [])

    missing = [path.as_posix() for path in [layout_netlist, schematic_netlist] if path is None or not path.exists()]
    if missing:
        result.update({"lvs_status": "missing_input", "notes": [f"missing required LVS inputs: {', '.join(missing)}"]})
        return result

    if not tools.get("netgen_available"):
        result.update({"lvs_status": "unsupported", "notes": ["netgen not found in PATH"]})
        return result
    if setup_path is None:
        result.update({"lvs_status": "partial", "notes": ["could not find a Netgen LVS setup file"]})
        return result

    work_dir.mkdir(parents=True, exist_ok=True)
    layout_top = _infer_top_from_netlist(layout_netlist)
    schematic_top = _infer_top_from_netlist(schematic_netlist)
    script_body = "\n".join(
        [
            f'lvs {{{layout_netlist.as_posix()} {layout_top}}} {{{schematic_netlist.as_posix()} {schematic_top}}} {setup_path.as_posix()} {report_path.as_posix()}',
            "quit",
            "",
        ]
    )
    script_path.write_text(script_body, encoding="utf-8")

    retry_attempts = 0
    command = [str(tools["netgen_path"]), "-batch", str(script_path)]
    proc = subprocess.run(command, capture_output=True, text=True, cwd=work_dir, env=env)
    if _needs_netgen_retry(proc):
        retry_attempts = 1
        env = _build_netgen_env(force_retry=True)
        result["netgen_env_used"] = {
            "NETGENDIR": env.get("NETGENDIR"),
            "LD_LIBRARY_PATH": env.get("LD_LIBRARY_PATH"),
            "OMPI_MCA_plm": env.get("OMPI_MCA_plm"),
            "OMPI_MCA_btl": env.get("OMPI_MCA_btl"),
        }
        proc = subprocess.run(command, capture_output=True, text=True, cwd=work_dir, env=env)

    parsed = parse_netgen_lvs_report(report_path)
    output_text = "\n".join(part for part in [proc.stdout, proc.stderr] if part)
    lvs_ok = parsed.get("success") or _netgen_output_indicates_success(output_text)
    status = "pass"
    if proc.returncode != 0:
        status = "unsupported" if _needs_netgen_retry(proc) or _netgen_binary_is_not_lvs(proc) else "tool_error"
    elif parsed["lvs_mismatch_count"] > 0:
        status = "fail"
    elif not lvs_ok and not report_path.exists():
        status = "partial"

    result.update(
        {
            "lvs_status": status,
            "lvs_mismatch_count": parsed["lvs_mismatch_count"],
            "lvs_mismatches": parsed.get("mismatches", []),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "command": " ".join(command),
            "retry_attempts": {"netgen": retry_attempts},
            "notes": parsed.get("notes", []),
        }
    )
    if proc.returncode != 0 and not result["notes"]:
        result["notes"].append("netgen LVS command failed")
    if proc.returncode != 0 and _netgen_binary_is_not_lvs(proc):
        result["notes"].append("installed netgen binary appears to be the mesh generator, not Netgen-LVS")
    return result


def parse_magic_drc_report(path: Path) -> dict:
    if not path.exists():
        return {"drc_violation_count": 0, "violations": [], "notes": ["Magic DRC report was not generated"]}
    text = path.read_text(encoding="utf-8", errors="ignore")
    violations = []
    capture = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "MAGIC_DRC_BEGIN":
            capture = True
            continue
        if stripped == "MAGIC_DRC_END":
            break
        if capture and stripped:
            violations.append(stripped)
    return {
        "drc_violation_count": len(violations),
        "violations": violations,
        "notes": [] if violations or text.strip() else ["Magic DRC report was empty"],
    }


def parse_netgen_lvs_report(path: Path) -> dict:
    if not path.exists():
        return {"lvs_mismatch_count": 0, "mismatches": [], "notes": ["Netgen LVS report was not generated"], "success": False}
    text = path.read_text(encoding="utf-8", errors="ignore")
    mismatches = []
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if any(token in lowered for token in ["property errors", "netlists do not match", "mismatch", "unmatched", "devices differ"]):
            mismatches.append(stripped)
    success = _netgen_output_indicates_success(text)
    notes = [] if mismatches or text.strip() else ["Netgen LVS report was empty"]
    return {
        "lvs_mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "notes": notes,
        "success": success,
    }


def summarize_signoff_results(results: dict) -> dict:
    drc = dict(results.get("drc", {})) if isinstance(results.get("drc"), dict) else {}
    lvs = dict(results.get("lvs", {})) if isinstance(results.get("lvs"), dict) else {}
    notes = []
    notes.extend(_as_list(drc.get("notes")))
    notes.extend(_as_list(lvs.get("notes")))
    reports = {
        "drc_report_paths": _as_list(drc.get("signoff_reports")),
        "lvs_report_paths": _as_list(lvs.get("signoff_reports")),
    }
    artifacts = list(dict.fromkeys(_as_list(drc.get("signoff_artifacts")) + _as_list(lvs.get("signoff_artifacts"))))
    availability = results.get("signoff_tool_availability") if isinstance(results.get("signoff_tool_availability"), dict) else {}
    drc_status = str(drc.get("drc_status", "not_run"))
    lvs_status = str(lvs.get("lvs_status", "not_run"))
    classification = _classify_signoff_failure(
        drc_status=drc_status,
        lvs_status=lvs_status,
        drc_count=int(drc.get("drc_violation_count", 0) or 0),
        lvs_count=int(lvs.get("lvs_mismatch_count", 0) or 0),
        availability=availability,
    )
    if drc_status == "fail" or lvs_status == "fail":
        overall = "fail"
    elif drc_status in {"unsupported", "partial"} or lvs_status in {"unsupported", "partial"}:
        overall = "partial"
    elif drc_status == "pass" and lvs_status == "pass":
        overall = "pass"
    else:
        overall = "not_run"
    return {
        "status": overall,
        "drc_status": drc_status,
        "lvs_status": lvs_status,
        "drc_violation_count": int(drc.get("drc_violation_count", 0) or 0),
        "lvs_mismatch_count": int(lvs.get("lvs_mismatch_count", 0) or 0),
        "signoff_tool_availability": availability,
        "signoff_reports": reports,
        "signoff_artifacts": artifacts,
        "magic_rcfile_used": drc.get("magic_rcfile_used"),
        "netgen_env_used": lvs.get("netgen_env_used", {}),
        "retry_attempts": {"netgen": int(_nested_get(lvs, "retry_attempts", "netgen") or 0)},
        "failure_kind": classification["failure_kind"],
        "metric_kind": classification["metric_kind"],
        "action_family_hint": classification["action_family_hint"],
        "ordered_bottlenecks": classification["ordered_bottlenecks"],
        "notes": list(dict.fromkeys(item for item in notes if item)),
    }


def _empty_signoff_result() -> dict:
    return {
        "command": None,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "drc_status": "not_run",
        "lvs_status": "not_run",
        "drc_violation_count": 0,
        "lvs_mismatch_count": 0,
        "signoff_tool_availability": {},
        "signoff_reports": [],
        "signoff_artifacts": [],
        "magic_rcfile_used": None,
        "netgen_env_used": {},
        "retry_attempts": {"netgen": 0},
        "notes": [],
    }


def _tool_availability(tools: dict) -> dict:
    return {
        "magic": bool(tools.get("magic_available")),
        "netgen": bool(tools.get("netgen_available")),
        "magic_usable": bool(tools.get("magic_usable")),
        "netgen_usable": bool(tools.get("netgen_usable")),
        "magic_path": tools.get("magic_path"),
        "netgen_path": tools.get("netgen_path"),
    }


def _probe_magic_headless(magic_path: str | None) -> dict:
    if magic_path is None:
        return {"available": False, "usable": False, "reason": "not found in PATH"}
    try:
        proc = subprocess.run([magic_path, "-dnull", "-noconsole"], input="quit -noprompt\n", capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": True, "usable": False, "reason": str(exc)}
    usable = proc.returncode == 0
    reason = "ok" if usable else (proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}")
    return {"available": True, "usable": usable, "reason": reason}


def _probe_netgen_batch(netgen_path: str | None) -> dict:
    if netgen_path is None:
        return {"available": False, "usable": False, "reason": "not found in PATH"}
    with tempfile.TemporaryDirectory(prefix="spec2rtl_netgen_probe_") as temp_dir:
        script_path = Path(temp_dir) / "probe.tcl"
        script_path.write_text("quit\n", encoding="utf-8")
        env = _build_netgen_env()
        try:
            proc = subprocess.run([netgen_path, "-batch", str(script_path)], capture_output=True, text=True, timeout=15, env=env)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"available": True, "usable": False, "reason": str(exc)}
    usable = proc.returncode == 0
    if not usable and _netgen_binary_is_not_lvs(proc):
        reason = "binary in PATH is not Netgen-LVS"
    else:
        reason = "ok" if usable else (proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}")
    return {"available": True, "usable": usable, "reason": reason}


def _find_magic_rcfile(tech_lef: Path) -> Path | None:
    candidates: list[Path] = []
    flow_root = _detect_flow_root()
    if flow_root is not None:
        platform_dir = flow_root / "flow" / "platforms" / "sky130hd"
        candidates.extend(_glob_existing(platform_dir, "*.magicrc"))
        candidates.extend([platform_dir / "sky130A.magicrc", platform_dir / "magicrc"])
    if tech_lef is not None:
        for parent in [tech_lef.parent, *tech_lef.parents]:
            candidates.extend(_glob_existing(parent, "*.magicrc"))
            candidates.extend([parent / "sky130A.magicrc", parent / "magicrc"])
            if parent.name == "lef":
                candidates.extend(_glob_existing(parent.parent, "*.magicrc"))
                magic_dir = parent.parent / "magic"
                candidates.extend(_glob_existing(magic_dir, "*.magicrc"))
                candidates.extend([magic_dir / "sky130A.magicrc", magic_dir / "magicrc"])
    env_rc = os.environ.get("MAGIC_RCFILE")
    if env_rc:
        candidates.append(Path(env_rc))
    candidates.extend(Path(path) for path in DEFAULT_MAGIC_RCFALLBACKS)
    for candidate in _dedupe_paths(candidates):
        if candidate.is_file():
            return candidate
    return None


def _find_netgen_setup(layout_netlist: Path, schematic_netlist: Path) -> Path | None:
    candidates: list[Path] = []
    search_roots = list(dict.fromkeys([layout_netlist.parent, schematic_netlist.parent, *layout_netlist.parents[:4], *schematic_netlist.parents[:4]]))
    for root in search_roots:
        for pattern in ["*setup*.tcl", "*Setup*.tcl", "*lvs*.tcl", "*netgen*.tcl"]:
            candidates.extend(_glob_existing(root, pattern))
    pdk_root = os.environ.get("PDK_ROOT")
    if pdk_root:
        candidates.append(Path(pdk_root) / "sky130A" / "libs.tech" / "netgen" / "sky130A_setup.tcl")
    env_setup = os.environ.get("NETGEN_SETUP")
    if env_setup:
        candidates.append(Path(env_setup))
    candidates.extend(Path(path) for path in DEFAULT_NETGEN_SETUP_FALLBACKS)
    for candidate in _dedupe_paths(candidates):
        if candidate.is_file():
            return candidate
    return None


def _infer_top_from_netlist(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"\bmodule\s+([A-Za-z_][A-Za-z0-9_$]*)", text)
    if match:
        return match.group(1)
    return path.stem


def _build_netgen_env(force_retry: bool = False) -> dict[str, str]:
    env = os.environ.copy()
    env["NETGENDIR"] = _first_existing_string([env.get("NETGENDIR"), DEFAULT_NETGENDIR]) or DEFAULT_NETGENDIR
    ld_library_path = env.get("LD_LIBRARY_PATH", "")
    prefix = DEFAULT_NETGEN_LIBDIR
    env["LD_LIBRARY_PATH"] = f"{prefix}:{ld_library_path}" if ld_library_path else prefix
    env["OMPI_MCA_plm"] = "isolated"
    env["OMPI_MCA_btl"] = "self"
    if force_retry:
        env["OMPI_MCA_ess"] = "singleton"
        env["PMIX_MCA_ptl"] = "^usock,tcp"
        env["PMIX_SYSTEM_TMPDIR"] = "/tmp"
    return env


def _netgen_output_indicates_success(text: str) -> bool:
    lowered = text.lower()
    return "lvs ok" in lowered or "circuits match" in lowered


def _needs_netgen_retry(proc: subprocess.CompletedProcess[str]) -> bool:
    text = "\n".join(part for part in [proc.stdout, proc.stderr] if part)
    lowered = text.lower()
    return "libgui.so" in lowered or "netgendir" in lowered


def _netgen_binary_is_not_lvs(proc: subprocess.CompletedProcess[str]) -> bool:
    text = "\n".join(part for part in [proc.stdout, proc.stderr] if part).lower()
    return "automatic 3d tetrahedral mesh generator" in text or "mpi_init failed" in text or "orte_init failed" in text


def _detect_flow_root() -> Path | None:
    for env_name in ["OPENROAD_FLOW_ROOT", "OPENROAD_FLOW_DIR"]:
        value = os.environ.get(env_name)
        if value:
            candidate = Path(value).expanduser()
            if (candidate / "flow" / "platforms").exists():
                return candidate
            if candidate.name == "flow" and (candidate / "platforms").exists():
                return candidate.parent
    cwd = Path.cwd()
    for candidate in [cwd / "OpenROAD-flow-scripts", cwd.parent / "OpenROAD-flow-scripts", cwd / "openroad-flow-scripts", cwd.parent / "openroad-flow-scripts"]:
        if (candidate / "flow" / "platforms").exists():
            return candidate
    return None


def _glob_existing(root: Path, pattern: str) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.glob(pattern) if path.is_file())


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    ordered: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = path.as_posix()
        if key not in seen:
            seen.add(key)
            ordered.append(path)
    return ordered


def _first_existing_string(candidates: list[str | None]) -> str | None:
    for candidate in candidates:
        if candidate:
            return candidate
    return None


def _nested_get(mapping: dict, *keys: str) -> object:
    current: object = mapping
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if value in {None, ""}:
        return []
    return [str(value)]


def _classify_signoff_failure(
    drc_status: str,
    lvs_status: str,
    drc_count: int,
    lvs_count: int,
    availability: dict,
) -> dict:
    del drc_count, lvs_count
    if drc_status == "fail" and lvs_status == "fail":
        return {
            "failure_kind": "mixed",
            "metric_kind": "routability",
            "action_family_hint": "routability",
            "ordered_bottlenecks": ["drc", "lvs"],
        }
    if drc_status == "fail":
        return {
            "failure_kind": "drc / routability / placement",
            "metric_kind": "routability",
            "action_family_hint": "routability",
            "ordered_bottlenecks": ["drc"],
        }
    if lvs_status == "fail":
        return {
            "failure_kind": "lvs / netlist-correctness / collateral",
            "metric_kind": "correctness",
            "action_family_hint": "correctness",
            "ordered_bottlenecks": ["lvs"],
        }
    if drc_status in {"unsupported", "partial"} or lvs_status in {"unsupported", "partial"}:
        unavailable = []
        if not availability.get("magic_usable", availability.get("magic", False)):
            unavailable.append("magic")
        if not availability.get("netgen_usable", availability.get("netgen", False)):
            unavailable.append("netgen")
        return {
            "failure_kind": "unsupported",
            "metric_kind": "unknown",
            "action_family_hint": "none",
            "ordered_bottlenecks": unavailable,
        }
    return {
        "failure_kind": "clean",
        "metric_kind": "unknown",
        "action_family_hint": "none",
        "ordered_bottlenecks": [],
    }
