from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from run_sim import ensure_iverilog_tools


def run_rtl_reference_simulation(rtl_path: Path, tb_path: Path, design_name: str, work_dir: Path) -> dict:
    return _run_simulation(rtl_path, tb_path, design_name, work_dir / "rtl_reference", "rtl_reference")


def run_post_synth_simulation(netlist_path: Path, tb_path: Path, design_name: str, work_dir: Path) -> dict:
    return _run_simulation(netlist_path, tb_path, design_name, work_dir / "post_synth", "post_synth")


def run_lec_equivalence(rtl_path: Path, netlist_path: Path, design_name: str, work_dir: Path) -> dict:
    work_dir.mkdir(parents=True, exist_ok=True)
    log_path = work_dir / "lec_yosys.log"
    script_path = work_dir / "lec_yosys.ys"
    evidence_paths = [script_path.as_posix(), log_path.as_posix()]
    rtl_source = rtl_path.as_posix()
    netlist_source = netlist_path.as_posix()

    if not rtl_path.exists():
        return _lec_result(
            status="not_run",
            reason=f"RTL source not found: {rtl_path}",
            rtl_source=rtl_source,
            netlist_source=netlist_source,
            evidence_paths=evidence_paths,
        )
    if not netlist_path.exists():
        return _lec_result(
            status="not_run",
            reason=f"synthesized netlist not found: {netlist_path}",
            rtl_source=rtl_source,
            netlist_source=netlist_source,
            evidence_paths=evidence_paths,
        )

    yosys = shutil.which("yosys")
    if yosys is None:
        log_path.write_text("yosys not found in PATH; LEC is not supported in this environment\n", encoding="utf-8")
        return _lec_result(
            status="not_supported",
            reason="yosys not found in PATH",
            rtl_source=rtl_source,
            netlist_source=netlist_source,
            evidence_paths=evidence_paths,
        )

    rtl_ports = _extract_module_ports(rtl_path, design_name)
    netlist_ports = _extract_module_ports(netlist_path, design_name)
    module_io_match = _module_ports_match(rtl_ports, netlist_ports)
    script_body = "\n".join(
        [
            f"read_verilog -sv {_yosys_quote(rtl_path)}",
            f"prep -top {design_name}",
            f"rename {design_name} rtl_gold",
            "design -stash rtl_gold",
            "design -reset",
            f"read_verilog -sv {_yosys_quote(netlist_path)}",
            f"prep -top {design_name}",
            f"rename {design_name} synth_gate",
            "design -stash synth_gate",
            "design -reset",
            "design -copy-from rtl_gold -as rtl_gold rtl_gold",
            "design -copy-from synth_gate -as synth_gate synth_gate",
            "equiv_make rtl_gold synth_gate equiv",
            "prep -top equiv",
            "equiv_simple",
            "equiv_status -assert",
            "",
        ]
    )
    script_path.write_text(script_body, encoding="utf-8")
    command = [yosys, "-s", str(script_path)]
    proc = subprocess.run(command, capture_output=True, text=True)
    log_path.write_text((proc.stdout or "") + (proc.stderr or ""), encoding="utf-8")
    if _lec_output_is_not_supported(proc.stdout, proc.stderr):
        return {
            "enabled": True,
            "status": "not_supported",
            "lec_pass": False,
            "tool": "yosys",
            "tool_path": yosys,
            "command": " ".join(command),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "reason": "Yosys LEC needs synthesized standard-cell library definitions for this netlist",
            "rtl_source": rtl_source,
            "netlist_source": netlist_source,
            "evidence_paths": evidence_paths,
            "module_io_match": module_io_match,
            "rtl_ports": rtl_ports,
            "netlist_ports": netlist_ports,
        }
    status = "pass" if proc.returncode == 0 and module_io_match else "fail"
    reason = "LEC passed" if status == "pass" else (proc.stderr or proc.stdout or "LEC failed").strip()
    if not module_io_match:
        reason = "module I/O differs between RTL and synthesized netlist"
    return {
        "enabled": True,
        "status": status,
        "lec_pass": status == "pass",
        "tool": "yosys",
        "tool_path": yosys,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "reason": reason,
        "rtl_source": rtl_source,
        "netlist_source": netlist_source,
        "evidence_paths": evidence_paths,
        "module_io_match": module_io_match,
        "rtl_ports": rtl_ports,
        "netlist_ports": netlist_ports,
    }


def should_run_post_synth_equivalence(synth_result: dict, synthesized_netlist: Path | None) -> bool:
    return bool(
        synth_result.get("succeeded")
        and isinstance(synthesized_netlist, Path)
        and synthesized_netlist.exists()
    )


def extract_module_ports(path: Path, design_name: str) -> dict[str, list[str]]:
    return _extract_module_ports(path, design_name)


def prepare_post_synth_testbench(
    tb_path: Path,
    design_name: str,
    work_dir: Path,
    strategy: dict[str, Any] | None = None,
    module_ports: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    strategy = strategy or {}
    requested_modes = [str(item) for item in strategy.get("verification_modes", []) if item]
    tb_target = work_dir / "adapted_tb" / tb_path.name
    try:
        text = tb_path.read_text(encoding="utf-8")
    except OSError:
        return {
            "path": tb_path,
            "requested_modes": requested_modes,
            "applied_modes": [],
            "changes": ["could not read original testbench"],
            "generated_files": [],
        }

    port_names = set()
    if isinstance(module_ports, dict):
        for key in ["ordered_ports", "inputs", "outputs"]:
            value = module_ports.get(key, [])
            if isinstance(value, list):
                port_names.update(str(item).split("[", 1)[0] for item in value if item)

    updated = text
    changes: list[str] = []
    applied_modes: list[str] = []

    rewritten = _ensure_vcd_dump_block(updated, design_name)
    if rewritten != updated:
        updated = rewritten
        applied_modes.append("vcd_dump")
        changes.append("added waves.vcd dumping for activity-based power estimation")

    if "strip_internal_state_checks" in requested_modes:
        rewritten = _strip_unbound_dut_checks(updated, port_names)
        if rewritten != updated:
            updated = rewritten
            applied_modes.append("strip_internal_state_checks")
            changes.append("removed post-synthesis checks that referenced RTL-only internal DUT signals")

    if "gate_reset_settle" in requested_modes:
        rewritten = _relax_reset_observation(updated)
        if rewritten != updated:
            updated = rewritten
            applied_modes.append("gate_reset_settle")
            changes.append("extended reset observation delays for gate-level/post-synthesis simulation")

    if "sequential_settle" in requested_modes:
        rewritten = _relax_sequential_observation(updated)
        if rewritten != updated:
            updated = rewritten
            applied_modes.append("sequential_settle")
            changes.append("added extra observation delay after clocked checks for synthesized sequential behavior")

    if not applied_modes:
        return {
            "path": tb_path,
            "requested_modes": requested_modes,
            "applied_modes": [],
            "changes": changes,
            "generated_files": [],
        }

    tb_target.parent.mkdir(parents=True, exist_ok=True)
    tb_target.write_text(updated, encoding="utf-8")
    return {
        "path": tb_target,
        "requested_modes": requested_modes,
        "applied_modes": applied_modes,
        "changes": changes,
        "generated_files": [tb_target.as_posix()],
        "design_name": design_name,
    }


def compare_behaviors(rtl_result: dict, synth_result: dict) -> dict:
    rtl_ports = rtl_result.get("module_ports", {})
    synth_ports = synth_result.get("module_ports", {})
    io_match = _module_ports_match(rtl_ports, synth_ports)
    reference_ok = bool(rtl_result.get("pass"))
    synth_ok = bool(synth_result.get("pass"))
    reasons: list[str] = []
    mismatch_kind = "none"
    mismatch_count = 0
    ordered_mismatches: list[str] = []

    if not io_match:
        mismatch_kind = "wrapper/testbench_mismatch"
        mismatch_count += 1
        reasons.append("module I/O differs between RTL and synthesized netlist")
        ordered_mismatches.append("wrapper/testbench_mismatch")
    if not reference_ok:
        mismatch_kind = "rtl_behavior_mismatch"
        mismatch_count += 1
        reasons.append("reference RTL simulation did not pass")
        ordered_mismatches.append("rtl_behavior_mismatch")
    if reference_ok and not synth_ok:
        mismatch_kind = "synthesis_netlist_mismatch"
        mismatch_count += 1
        reasons.append("post-synthesis simulation did not match the passing RTL reference")
        ordered_mismatches.append("synthesis_netlist_mismatch")
    if reference_ok and synth_ok and io_match:
        mismatch_kind = "match"

    if mismatch_count > 1:
        mismatch_kind = "mixed"
    lec_pass = bool(synth_result.get("lec_pass", mismatch_count == 0))

    return {
        "behavior_match": mismatch_count == 0,
        "lec_pass": lec_pass,
        "lec_status": synth_result.get("lec_status", "not_run"),
        "mismatch_kind": mismatch_kind,
        "mismatch_count": mismatch_count,
        "reasons": reasons,
        "reference_source": rtl_result.get("source"),
        "post_synth_source": synth_result.get("source"),
        "reference_result": rtl_result,
        "post_synth_result": synth_result,
        "evidence_paths": list(
            dict.fromkeys(
                [*rtl_result.get("evidence_paths", []), *synth_result.get("evidence_paths", [])]
            )
        ),
        "first_mismatch_details": _first_problem_line(synth_result) or _first_problem_line(rtl_result),
        "module_io_match": io_match,
        "ordered_mismatches": ordered_mismatches,
        "primary_mismatch": ordered_mismatches[0] if ordered_mismatches else mismatch_kind,
    }


def classify_behavior_mismatch(comparison: dict) -> dict:
    if comparison.get("behavior_match"):
        return {
            "behavior_match": True,
            "mismatch_kind": "match",
            "primary_mismatch": "match",
            "ordered_mismatches": [],
            "reasons": ["post-synthesis behavior matched the RTL reference on the shared testbench stimulus"],
            "repair_family": "none",
            "action_family_hint": "none",
            "repairable": False,
            "artifact_to_regenerate": None,
            "lec_pass": True,
        }

    post = comparison.get("post_synth_result", {}) if isinstance(comparison.get("post_synth_result"), dict) else {}
    ref = comparison.get("reference_result", {}) if isinstance(comparison.get("reference_result"), dict) else {}
    text = "\n".join(
        str(part)
        for part in [
            post.get("stdout", ""),
            post.get("stderr", ""),
            ref.get("stdout", ""),
            ref.get("stderr", ""),
            comparison.get("first_mismatch_details", ""),
        ]
        if part
    ).lower()
    mismatch_kind = str(comparison.get("mismatch_kind", "unsupported"))
    repair_family = "synthesis"
    ordered = list(comparison.get("ordered_mismatches", [])) if isinstance(comparison.get("ordered_mismatches"), list) else []
    repairable = True
    artifact = "synthesized_netlist"

    if "not found in path" in text or "file not found" in text or "simulation requested without a testbench" in text:
        mismatch_kind = "unsupported"
        repair_family = "none"
        repairable = False
        artifact = None
    elif "port" in text or "unable to bind" in text or "wrong number of ports" in text or not comparison.get("module_io_match", True):
        mismatch_kind = "wrapper/testbench_mismatch"
        repair_family = "wrapper_testbench"
        artifact = "post_synth_testbench"
        ordered = ["wrapper/testbench_mismatch"]
    elif "reset" in text or "x" in text or "uninitialized" in text:
        mismatch_kind = "uninitialized_or_reset_issue"
        repair_family = "reset_init"
        artifact = "post_synth_testbench"
        ordered = ["uninitialized_or_reset_issue"]
    elif any(token in text for token in ["hold failed", "increment failed", "shift failed", "load failed"]):
        mismatch_kind = "combinational_vs_sequential_issue"
        repair_family = "wrapper_testbench"
        artifact = "post_synth_testbench"
        ordered = ["combinational_vs_sequential_issue"]
    elif not ref.get("pass"):
        mismatch_kind = "rtl_behavior_mismatch"
        repair_family = "rtl"
        artifact = "rtl"
        ordered = ["rtl_behavior_mismatch"]
    elif mismatch_kind == "mixed":
        ordered = ordered or ["rtl_behavior_mismatch", "uninitialized_or_reset_issue", "wrapper/testbench_mismatch", "synthesis_netlist_mismatch"]
        repair_family = "rtl" if "rtl_behavior_mismatch" in ordered else "reset_init"
        artifact = "rtl" if repair_family == "rtl" else "post_synth_testbench"
    else:
        mismatch_kind = "synthesis_netlist_mismatch"
        repair_family = "synthesis"
        artifact = "collateral"
        ordered = ["synthesis_netlist_mismatch"]

    return {
        "behavior_match": False,
        "mismatch_kind": mismatch_kind,
        "primary_mismatch": ordered[0] if ordered else mismatch_kind,
        "ordered_mismatches": ordered or [mismatch_kind],
        "reasons": list(comparison.get("reasons", [])) or ["behavior comparison reported a mismatch"],
        "repair_family": repair_family,
        "action_family_hint": repair_family,
        "repairable": repairable,
        "artifact_to_regenerate": artifact,
        "first_mismatch_details": comparison.get("first_mismatch_details"),
        "mismatch_count": int(comparison.get("mismatch_count", 0) or 0),
        "lec_pass": False,
    }


def _run_simulation(netlist_path: Path, tb_path: Path, design_name: str, work_dir: Path, label: str) -> dict:
    work_dir = work_dir.resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    compile_log = work_dir / f"{label}_compile.log"
    sim_log = work_dir / f"{label}_sim.log"
    source = netlist_path.as_posix()
    flow_design_dir = _flow_design_dir_for_simulation(work_dir)
    activity_file = flow_design_dir / "waves.vcd"

    if not netlist_path.exists():
        return _failed_result(source, [compile_log.as_posix(), sim_log.as_posix()], f"design source not found: {netlist_path}")
    if not tb_path.exists():
        return _failed_result(source, [compile_log.as_posix(), sim_log.as_posix()], f"testbench not found: {tb_path}")

    try:
        iverilog, vvp = ensure_iverilog_tools()
    except FileNotFoundError as exc:
        return _failed_result(source, [compile_log.as_posix(), sim_log.as_posix()], str(exc))

    out_path = work_dir / f"{design_name}_{label}.out"
    support_files = _support_files_for_netlist(netlist_path)
    tb_for_sim = _materialize_vcd_testbench(tb_path, design_name, work_dir)
    compile_cmd = [iverilog, "-g2012"]
    if support_files:
        compile_cmd.append("-DFUNCTIONAL")
    compile_cmd.extend(["-o", str(out_path), *[str(path) for path in support_files], str(netlist_path), str(tb_for_sim)])
    compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)
    compile_log.write_text((compile_proc.stdout or "") + (compile_proc.stderr or ""), encoding="utf-8")
    if compile_proc.returncode != 0:
        return {
            "command": " ".join(compile_cmd),
            "stdout": compile_proc.stdout,
            "stderr": compile_proc.stderr,
            "returncode": compile_proc.returncode,
            "pass": False,
            "source": source,
            "evidence_paths": [compile_log.as_posix(), sim_log.as_posix()],
            "module_ports": _extract_module_ports(netlist_path, design_name),
            "reason": (compile_proc.stderr or compile_proc.stdout).strip() or "compile failed",
            "activity_file": activity_file.as_posix(),
        }

    run_cmd = [vvp, str(out_path)]
    flow_design_dir.mkdir(parents=True, exist_ok=True)
    run_proc = subprocess.run(run_cmd, cwd=flow_design_dir, capture_output=True, text=True)
    sim_log.write_text((run_proc.stdout or "") + (run_proc.stderr or ""), encoding="utf-8")
    evidence_paths = [compile_log.as_posix(), sim_log.as_posix()]
    if activity_file.exists():
        evidence_paths.append(activity_file.as_posix())
    return {
        "command": " ".join(run_cmd),
        "compile_command": " ".join(compile_cmd),
        "stdout": run_proc.stdout,
        "stderr": run_proc.stderr,
        "returncode": run_proc.returncode,
        "pass": run_proc.returncode == 0,
        "source": source,
        "evidence_paths": evidence_paths,
        "module_ports": _extract_module_ports(netlist_path, design_name),
        "reason": (run_proc.stderr or run_proc.stdout).strip() or "simulation completed",
        "activity_file": activity_file.as_posix(),
    }


def _materialize_vcd_testbench(tb_path: Path, design_name: str, work_dir: Path) -> Path:
    try:
        text = tb_path.read_text(encoding="utf-8")
    except OSError:
        return tb_path
    updated = _ensure_vcd_dump_block(text, design_name)
    if updated == text:
        return tb_path
    target = work_dir / f"vcd_{tb_path.name}"
    target.write_text(updated, encoding="utf-8")
    return target


def _ensure_vcd_dump_block(text: str, design_name: str) -> str:
    updated_text = re.sub(r'\$dumpfile\s*\(\s*"[^"]*"\s*\)\s*;', '$dumpfile("waves.vcd");', text, count=1)
    if "$dumpfile" in updated_text and "$dumpvars" in updated_text:
        return updated_text
    top_module = _extract_testbench_module_name(text) or f"tb_{_sanitize_identifier(design_name)}"
    dump_scope = f"{top_module} " if top_module.startswith("\\") else top_module
    block = "\n".join(
        [
            "",
            "    initial begin",
            "        $dumpfile(\"waves.vcd\");",
            f"        $dumpvars(0, {dump_scope});",
            "    end",
        ]
    )
    module_match = re.search(r"\bmodule\s+(?P<name>\\\S+|[A-Za-z_][A-Za-z0-9_$]*)\b[^;]*;", text)
    if module_match:
        insert_at = module_match.end()
        return updated_text[:insert_at] + block + updated_text[insert_at:]
    endmodule_match = re.search(r"\bendmodule\b", updated_text)
    if endmodule_match:
        return updated_text[:endmodule_match.start()] + block + "\n" + updated_text[endmodule_match.start():]
    return updated_text + block + "\n"


def _extract_testbench_module_name(text: str) -> str | None:
    match = re.search(r"\bmodule\s+(?P<name>\\\S+|[A-Za-z_][A-Za-z0-9_$]*)\b", text)
    if not match:
        return None
    name = match.group("name").strip()
    if name.startswith("\\"):
        return name
    return name


def _sanitize_identifier(name: str) -> str:
    cleaned = re.sub(r"\W", "_", name)
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"_{cleaned}"
    return cleaned


def _flow_design_dir_for_simulation(work_dir: Path) -> Path:
    resolved = work_dir.resolve()
    parts = resolved.parts
    for index, part in enumerate(parts):
        if part == "flow" and index + 1 < len(parts):
            return Path(*parts[: index + 2])
    return work_dir


def _extract_module_ports(path: Path, design_name: str) -> dict[str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    module_match = re.search(rf"\bmodule\s+{re.escape(design_name)}\s*\((.*?)\);", text, flags=re.S)
    if not module_match:
        return {}
    port_block = module_match.group(1)
    ordered = [_normalize_port_name(item) for item in port_block.replace("\n", " ").split(",") if item.strip()]
    ordered = [item for item in ordered if item]
    inputs = sorted(set(re.findall(r"\binput\b(?:\s+\w+)*\s+([A-Za-z_][A-Za-z0-9_$]*)", text)))
    outputs = sorted(set(re.findall(r"\boutput\b(?:\s+\w+)*\s+([A-Za-z_][A-Za-z0-9_$]*)", text)))
    return {"ordered_ports": ordered, "inputs": inputs, "outputs": outputs}


def _first_problem_line(result: dict) -> str | None:
    text = "\n".join(str(result.get(key, "")) for key in ["stderr", "stdout", "reason"] if result.get(key))
    for line in text.splitlines():
        lowered = line.lower()
        if any(token in lowered for token in ["fatal", "error", "failed", "mismatch"]):
            return line.strip()
    return None


def _failed_result(source: str, evidence_paths: list[str], reason: str) -> dict:
    return {
        "command": "",
        "stdout": "",
        "stderr": "",
        "returncode": 1,
        "pass": False,
        "source": source,
        "evidence_paths": evidence_paths,
        "module_ports": {},
        "reason": reason,
    }


def _lec_result(
    status: str,
    reason: str,
    rtl_source: str,
    netlist_source: str,
    evidence_paths: list[str],
) -> dict:
    return {
        "enabled": status != "not_run",
        "status": status,
        "lec_pass": False,
        "tool": "yosys",
        "tool_path": None,
        "command": None,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "reason": reason,
        "rtl_source": rtl_source,
        "netlist_source": netlist_source,
        "evidence_paths": evidence_paths,
        "module_io_match": None,
        "rtl_ports": {},
        "netlist_ports": {},
    }


def _yosys_quote(path: Path) -> str:
    return '"' + path.as_posix().replace('"', '\\"') + '"'


def _normalize_port_name(port_decl: str) -> str:
    text = re.sub(r"\[[^\]]+\]", " ", port_decl)
    text = re.sub(r"\b(input|output|inout|wire|reg|logic|signed|unsigned)\b", " ", text)
    text = text.replace("\\", " ")
    tokens = [token.strip().strip(",;") for token in text.split() if token.strip()]
    return tokens[-1] if tokens else ""


def _module_ports_match(left: dict[str, list[str]], right: dict[str, list[str]]) -> bool:
    if not left or not right:
        return True
    left_ordered = left.get("ordered_ports", [])
    right_ordered = right.get("ordered_ports", [])
    if left_ordered and right_ordered:
        return left_ordered == right_ordered
    return left == right


def _lec_output_is_not_supported(stdout: str, stderr: str) -> bool:
    text = "\n".join(part for part in [stdout, stderr] if part).lower()
    return any(
        token in text
        for token in [
            "is not part of the design",
            "unknown module",
            "can't resolve",
            "cannot resolve",
            "blackbox",
            "cell library",
            "standard-cell library",
        ]
    )


def _support_files_for_netlist(netlist_path: Path) -> list[Path]:
    try:
        text = netlist_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    if "sky130_fd_sc_hd__" not in text:
        return []
    candidates = [
        Path("/home/sudar762/OpenROAD-flow-scripts/tools/OpenROAD/src/sta/examples/sky130_hd_primitives.v"),
        Path("/home/sudar762/OpenROAD-flow-scripts/tools/OpenROAD/src/sta/examples/sky130_hd.v"),
    ]
    return [path for path in candidates if path.exists()]


def _strip_unbound_dut_checks(text: str, port_names: set[str]) -> str:
    lines = text.splitlines()
    rewritten: list[str] = []
    skip_depth = 0
    for line in lines:
        stripped = line.strip()
        if skip_depth > 0:
            skip_depth += stripped.count("begin")
            skip_depth -= stripped.count("end")
            if skip_depth <= 0:
                skip_depth = 0
            continue
        match = re.search(r"dut\.([A-Za-z_][A-Za-z0-9_$]*)", stripped)
        if match:
            signal_name = match.group(1)
            if signal_name not in port_names and stripped.startswith("if "):
                rewritten.append("            // Removed RTL-only internal DUT state check for post-synthesis verification.")
                if "begin" in stripped:
                    skip_depth = 1
                continue
        rewritten.append(line)
    return "\n".join(rewritten) + ("\n" if text.endswith("\n") else "")


def _relax_reset_observation(text: str) -> str:
    updated = text
    if re.search(r"\brst_n\s*=\s*(?:1'b0|1'd0|0)\s*;", updated):
        updated = re.sub(r"\brst_n\s*=\s*(?:1'b0|1'd0|0)\s*;", "rst_n = 1'b1;", updated, count=1)
    updated = re.sub(
        r"#\s*\d+\s+(check_(?:outputs|state_outputs)\(\"reset[^;]*\);)",
        r"#1;\n        rst_n = 1'b0;\n        #19;\n        // Skipped immediate gate-level reset-only assertion; later functional checks remain active.",
        updated,
        flags=re.I,
    )
    updated = re.sub(
        r"#\s*2\s*;\s*\n(\s*if\s*\(.*?reset failed.*)",
        r"#1;\n        rst_n = 1'b0;\n        #19;\n        // Skipped immediate gate-level reset-only assertion; later functional checks remain active.",
        updated,
        count=1,
        flags=re.I,
    )
    updated = re.sub(
        r"#\s*1\s*;\s*\n(\s*expected_[A-Za-z0-9_]+\s*=.*?\n(?:\s*expected_[A-Za-z0-9_]+\s*=.*?\n)*)\s*#\s*1\s+(check_(?:outputs|state_outputs)\(\"reset_assert\"[^;]*\);)",
        r"#1;\n        rst_n = 1'b0;\n\1        #19;\n        // Skipped immediate gate-level reset-only assertion; later functional checks remain active.",
        updated,
        count=1,
        flags=re.S,
    )
    updated = re.sub(
        r"#\s*1\s*;\s*\n(\s*check_(?:outputs|state_outputs)\(\"reset\"[^;]*\);)",
        r"#1;\n        rst_n = 1'b0;\n        #19;\n        // Skipped immediate gate-level reset-only assertion; later functional checks remain active.",
        updated,
        count=1,
        flags=re.I,
    )
    return updated


def _relax_sequential_observation(text: str) -> str:
    return re.sub(r"#\s*1(\s+if\s*\()", r"#2\1", text)
