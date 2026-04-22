from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys
from pathlib import Path
from typing import Any

from agent import (
    build_report,
    candidate_summary,
    ensure_writable,
    output_path,
    report_path as rtl_report_path,
    run_repair_loop,
    testbench_path,
    write_artifacts,
    write_yaml_report,
)
from spec2rtl.collateral import CollateralBundle, generate_collateral
from spec2rtl.equivalence import (
    should_run_post_synth_equivalence,
    classify_behavior_mismatch,
    compare_behaviors,
    extract_module_ports,
    prepare_post_synth_testbench,
    run_post_synth_simulation,
    run_rtl_reference_simulation,
)
from spec2rtl.flow_repair import (
    DEFAULT_ML_HISTORY_PATH,
    FlowIssue,
    QOR_KNOB_REGISTRY,
    apply_post_synth_strategy,
    apply_signoff_strategy,
    analyze_openroad_failure,
    apply_qor_strategy,
    attempt_collateral_repair,
    classify_post_synth_mismatch,
    classify_signoff_bottleneck,
    generate_qor_candidates,
    load_ml_history,
    rank_qor_candidates,
    suggest_post_synth_repairs,
    suggest_signoff_repairs,
    suggest_qor_knobs,
    update_ml_history,
    validate_collateral,
)
from spec2rtl.lowering import lower_document_to_ir
from spec2rtl.openroad import (
    OpenROADRunResult,
    classify_openroad_failure,
    detect_openroad_environment,
    detect_signoff_tools,
    run_openroad_flow,
    run_openroad_stage,
)
from spec2rtl.qor import (
    classify_synth_bottleneck,
    classify_qor_bottleneck,
    collect_qor_summary,
    merge_signoff_with_qor,
    score_qor,
    score_synth,
)
from spec2rtl.spec_ingest import load_spec_source
from spec2rtl.synth_opt import (
    DEFAULT_SYNTH_HISTORY_PATH,
    apply_synth_strategy,
    generate_synth_candidates,
    load_synth_history,
    rank_synth_candidates,
    select_synth_candidates_for_round,
    synth_candidate_to_config,
    update_synth_history,
)


ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "build"
REPORT_DIR = BUILD_DIR / "reports"
PIPELINE_DIR = BUILD_DIR / "pipeline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Spec-to-Tapeout automation pipeline")
    parser.add_argument("--spec", type=Path, default=ROOT / "spec.yaml", help="Path to a YAML or text spec")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated outputs")
    parser.add_argument("--max-passes", type=int, default=3, help="Maximum RTL repair iterations")
    parser.add_argument("--max-flow-passes", type=int, default=2, help="Maximum downstream collateral/flow repair iterations")
    parser.add_argument("--mode", choices=["rtl", "synth", "openroad", "full"], default="full")
    parser.add_argument("--inject-fault", type=str, default=None, help="Inject an RTL bug on the first agent pass")
    parser.add_argument(
        "--inject-flow-fault",
        choices=["bad_filelist", "missing_sdc", "wrong_top"],
        default=None,
        help="Inject a downstream collateral fault to demonstrate flow-stage diagnosis and repair",
    )
    parser.add_argument("--optimize-qor", action="store_true", help="Iteratively retune OpenROAD collateral based on QoR reports")
    parser.add_argument("--optimize-synth", action="store_true", help="Iteratively retune synthesis before P&R")
    parser.add_argument("--ml-tune", action="store_true", help="Use lightweight learned ranking over QoR candidates")
    parser.add_argument("--synth-max-iters", type=int, default=3, help="Maximum synthesis optimization attempts including baseline")
    parser.add_argument("--synth-min-attempts", type=int, default=3, help="Minimum synthesis attempts to explore when targets are not yet met")
    parser.add_argument("--synth-target-area", type=float, default=None, help="Target synthesized logical area in um^2 during synthesis optimization")
    parser.add_argument("--synth-target-power", type=float, default=None, help="Target estimated synth power in mW during synthesis optimization")
    parser.add_argument("--synth-target-cell-count", type=int, default=None, help="Target synthesized cell count during synthesis optimization")
    parser.add_argument("--qor-max-iters", type=int, default=3, help="Maximum OpenROAD QoR attempts including the baseline run")
    parser.add_argument("--min-qor-attempts", type=int, default=3, help="Minimum QoR attempts to explore when targets are not yet met")
    parser.add_argument("--persist-ml-history", action="store_true", help="Persist QoR attempt history to build/ml_history.json for future ranking")
    parser.add_argument("--run-signoff", action="store_true", help="Run DRC/LVS signoff after successful OpenROAD finish")
    parser.add_argument("--max-signoff-iters", type=int, default=2, help="Maximum extra signoff-driven retry rounds")
    parser.add_argument("--signoff-only", action="store_true", help="Skip QoR tuning and only run signoff feedback retries after baseline OpenROAD")
    parser.add_argument("--verify-post-synth", action="store_true", help="Run a post-synthesis behavior check against the synthesized netlist")
    parser.add_argument("--max-post-synth-iters", type=int, default=3, help="Maximum post-synthesis behavior-check retries")
    parser.add_argument("--post-synth-allow-fail", action="store_true", help="Do not fail the overall pipeline if post-synthesis behavior still mismatches")
    parser.add_argument("--post-synth-only", action="store_true", help="Stop after post-synthesis behavior verification")
    parser.add_argument("--drc-allow-fail", action="store_true", help="Do not fail the overall pipeline if DRC remains failing")
    parser.add_argument("--lvs-allow-fail", action="store_true", help="Do not fail the overall pipeline if LVS remains failing")
    parser.add_argument("--qor-target-wns", type=float, default=0.0, help="Target setup worst negative slack in ns")
    parser.add_argument("--qor-target-tns", type=float, default=0.0, help="Target setup total negative slack in ns")
    parser.add_argument("--qor-target-setup-violations", type=int, default=0, help="Target maximum setup violation count")
    parser.add_argument("--qor-target-hold-violations", type=int, default=0, help="Target maximum hold violation count")
    parser.add_argument("--qor-target-logical-area", type=float, default=None, help="Target synthesized/logical area in um^2")
    parser.add_argument("--qor-target-physical-area", type=float, default=None, help="Target physical/layout area in um^2")
    parser.add_argument("--qor-target-area", type=float, default=None, help="Target area in um^2 when a single area budget is preferred")
    parser.add_argument("--qor-target-power", type=float, default=None, help="Target total power in mW")
    parser.add_argument("--qor-target-routability", type=float, default=None, help="Target congestion overflow or routability score threshold")
    parser.add_argument("--qor-target-congestion", type=float, default=None, help="Target congestion overflow")
    parser.add_argument("--strict-exit", action="store_true", help="Return non-zero unless the final classification is pass")
    return parser.parse_args()


def resolve_spec(spec: Path) -> Path:
    return spec if spec.is_absolute() else ROOT / spec


def infer_top(spec_path: Path) -> str:
    parsed = load_spec_source(spec_path)
    if not parsed.candidates:
        return spec_path.stem
    module = parsed.candidates[0].document.get("module", {})
    if isinstance(module, dict) and module.get("name"):
        return str(module["name"])
    return spec_path.stem


def pipeline_report_path(top: str) -> Path:
    return REPORT_DIR / f"{top}_pipeline_report.yaml"


def _ensure_text(value: Any) -> str:
    return "" if value is None else str(value)


def _path_from_report(relative_or_abs: str | None) -> Path | None:
    if not relative_or_abs:
        return None
    path = Path(str(relative_or_abs))
    return path if path.is_absolute() else ROOT / path


def _write_stage_log(path: Path, header: str, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = body.strip()
    path.write_text(f"## {header}\n{text}\n" if text else f"## {header}\n", encoding="utf-8")
    return path


def _materialize_rtl_logs(top: str, report: dict[str, Any]) -> tuple[Path | None, Path | None]:
    logs_dir = PIPELINE_DIR / top / "logs"
    compile_log_path: Path | None = None
    simulation_log_path: Path | None = None
    attempts = report.get("repair_loop", {}).get("attempts", []) if isinstance(report.get("repair_loop"), dict) else []
    if isinstance(attempts, list) and attempts:
        last = attempts[-1] if isinstance(attempts[-1], dict) else {}
        compile_body = "\n".join(
            [
                f"command: {_ensure_text(last.get('compile_command'))}",
                f"status: {_ensure_text(last.get('compile_status'))}",
                _ensure_text(last.get("compile_stdout")),
                _ensure_text(last.get("compile_stderr")),
            ]
        ).strip()
        simulation_body = "\n".join(
            [
                f"command: {_ensure_text(last.get('simulation_command'))}",
                f"status: {_ensure_text(last.get('simulation_status'))}",
                _ensure_text(last.get("simulation_stdout")),
                _ensure_text(last.get("simulation_stderr")),
            ]
        ).strip()
        compile_log_path = _write_stage_log(logs_dir / "compile.log", "Compile", compile_body)
        if simulation_body:
            simulation_log_path = _write_stage_log(logs_dir / "simulation.log", "Simulation", simulation_body)
    return compile_log_path, simulation_log_path


def _select_candidate(spec_path: Path, selected_candidate_id: str | None) -> tuple[dict[str, Any], Any]:
    parsed = load_spec_source(spec_path)
    if not parsed.candidates:
        raise RuntimeError("No semantic candidates could be extracted from the specification.")
    candidate = next((item for item in parsed.candidates if item.candidate_id == selected_candidate_id), parsed.candidates[0])
    return parsed.normalized_source or candidate.document, candidate


def _relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _run_agent_stage(spec_path: Path, overwrite: bool, max_passes: int, inject_fault: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        parse_result = load_spec_source(spec_path)
        if not parse_result.candidates:
            raise RuntimeError("No semantic candidates could be extracted from the specification.")

        candidate_results: list[tuple[Any, dict[str, Any], dict[str, Any]]] = []
        for candidate in parse_result.candidates:
            ir = lower_document_to_ir(candidate.document)
            candidate_result = run_repair_loop(ir, "sim", max(1, max_passes), candidate.candidate_id, inject_fault)
            summary = candidate_summary(candidate, candidate_result)
            candidate_results.append((candidate, candidate_result, summary))

        candidate_results.sort(key=lambda item: item[2]["score"], reverse=True)
        selected_candidate, selected_result, selected_summary = candidate_results[0]
        selected_ir = selected_result["ir"]
        selected_tb_artifact = selected_result["tb_artifact"]
        compile_result = selected_result["compile_result"]
        sim_result = selected_result["sim_result"]
        attempt_records = selected_result["attempts"]

        rtl_path = output_path(selected_ir.name, None)
        tb_path = testbench_path(selected_ir.name)
        ensure_writable(rtl_path, overwrite)
        if selected_tb_artifact.text:
            ensure_writable(tb_path, overwrite)
        write_artifacts(rtl_path, tb_path if selected_tb_artifact.text else None, selected_result["rtl_text"], selected_tb_artifact)

        report = build_report(
            spec_path=spec_path,
            parse_result=parse_result,
            candidate=selected_candidate,
            ir=selected_ir,
            rtl_path=rtl_path,
            tb_path=tb_path if selected_tb_artifact.text and tb_path.exists() else None,
            injected_fault=inject_fault,
            max_attempts=max(1, max_passes),
            requested_mode="sim",
            compile_result=compile_result,
            sim_result=sim_result,
            evidence=selected_tb_artifact.evidence,
            attempts=attempt_records,
            candidate_summaries=[item[2] for item in candidate_results],
            final_classification=selected_summary["classification"],
        )
        out_report = rtl_report_path(selected_ir.name)
        write_yaml_report(out_report, report)

    return report, {
        "stdout": stdout_buffer.getvalue(),
        "stderr": stderr_buffer.getvalue(),
        "report_path": out_report,
    }


def _issue_summary(issues: list[FlowIssue]) -> list[dict[str, str]]:
    return [{"code": issue.code, "message": issue.message, "severity": issue.severity} for issue in issues]


def _collect_artifacts(bundle: CollateralBundle, openroad_result: OpenROADRunResult | None) -> list[str]:
    artifacts = [_relative(path) for path in bundle.generated_files]
    if openroad_result:
        artifacts.extend(_relative(path) for path in openroad_result.get("artifacts", []))
        if openroad_result.get("log_path"):
            artifacts.append(_relative(openroad_result.get("log_path")))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in artifacts:
        if item and item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def _collect_openroad_artifact_groups(openroad_result: OpenROADRunResult | None) -> dict[str, list[str]]:
    grouped = {
        "reports": [],
        "results": [],
        "logs": [],
        "other": [],
    }
    if not openroad_result:
        return grouped
    for path in openroad_result.get("artifacts", []):
        rel = _relative(path)
        if not rel:
            continue
        if "/reports/" in rel:
            grouped["reports"].append(rel)
        elif "/results/" in rel:
            grouped["results"].append(rel)
        elif "/logs/" in rel:
            grouped["logs"].append(rel)
        else:
            grouped["other"].append(rel)
    for key, values in grouped.items():
        grouped[key] = list(dict.fromkeys(values))
    return grouped


def _load_config_mk(path: Path) -> dict[str, Any]:
    vars_map: dict[str, str] = {}
    order: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {"vars": vars_map, "order": order}
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
        vars_map[name] = rhs.strip()
        order.append(name)
    return {"vars": vars_map, "order": order}


def _write_config_mk(path: Path, config: dict[str, Any]) -> Path:
    vars_map = config.get("vars", {})
    order = config.get("order", [])
    ordered_names = [name for name in order if isinstance(name, str) and name in vars_map]
    for name in vars_map:
        if name not in ordered_names:
            ordered_names.append(name)
    lines = [f"export {name} := {vars_map[name]}" for name in ordered_names]
    lines.extend(["", "# Auto-generated QoR tuning config.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _build_qor_targets(args: argparse.Namespace) -> dict[str, Any]:
    logical_area_target = args.qor_target_logical_area if args.qor_target_logical_area is not None else args.qor_target_area
    physical_area_target = args.qor_target_physical_area if args.qor_target_physical_area is not None else args.qor_target_area
    congestion_target = args.qor_target_congestion if args.qor_target_congestion is not None else args.qor_target_routability
    return {
        "wns": args.qor_target_wns,
        "tns": args.qor_target_tns,
        "setup_violations": args.qor_target_setup_violations,
        "hold_violations": args.qor_target_hold_violations,
        "logical_area": logical_area_target,
        "physical_area": physical_area_target,
        "area": args.qor_target_area,
        "power": args.qor_target_power,
        "routability": congestion_target,
        "congestion": congestion_target,
    }


def _build_synth_targets(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "logical_area": args.synth_target_area,
        "area": args.synth_target_area,
        "power": args.synth_target_power,
        "cell_count": args.synth_target_cell_count,
        "wns": args.qor_target_wns,
    }


def _synth_targets_met(metrics: dict[str, Any], targets: dict[str, Any], behavior_match: bool) -> bool:
    if not behavior_match:
        return False
    area = metrics.get("area", {}) if isinstance(metrics.get("area"), dict) else {}
    power = metrics.get("power", {}) if isinstance(metrics.get("power"), dict) else {}
    timing = metrics.get("timing", {}) if isinstance(metrics.get("timing"), dict) else {}
    comparisons = [
        (area.get("logical_um2"), targets.get("logical_area", targets.get("area")), "<="),
        (area.get("cell_count"), targets.get("cell_count"), "<="),
        (power.get("mw"), targets.get("power"), "<="),
        (timing.get("wns_ns"), targets.get("wns"), ">="),
    ]
    checked_any = False
    for value, target, op in comparisons:
        if target is None or value is None:
            continue
        checked_any = True
        if op == "<=" and float(value) > float(target):
            return False
        if op == ">=" and float(value) < float(target):
            return False
    return checked_any


def _metrics_meet_targets(metrics: dict[str, Any], targets: dict[str, Any]) -> bool:
    timing = metrics.get("timing", {})
    area = metrics.get("area", {})
    power = metrics.get("power", {})
    routability = metrics.get("routability", {})
    comparisons = [
        (timing.get("wns_ns"), targets.get("wns"), ">="),
        (timing.get("tns_ns"), targets.get("tns"), ">="),
        (timing.get("setup_violation_count"), targets.get("setup_violations"), "<="),
        (timing.get("hold_violation_count"), targets.get("hold_violations"), "<="),
        (area.get("logical_um2"), targets.get("logical_area"), "<="),
        (area.get("physical_um2"), targets.get("physical_area"), "<="),
        (power.get("mw"), targets.get("power"), "<="),
        (routability.get("congestion"), targets.get("congestion", targets.get("routability")), "<="),
    ]
    for value, target, op in comparisons:
        if target is None or value is None:
            continue
        if op == ">=" and float(value) < float(target):
            return False
        if op == "<=" and float(value) > float(target):
            return False
    return True


def _signoff_targets_met(signoff: dict[str, Any], allow_drc_fail: bool, allow_lvs_fail: bool) -> bool:
    if not isinstance(signoff, dict):
        return True
    drc_status = str(signoff.get("drc_status", "not_run"))
    lvs_status = str(signoff.get("lvs_status", "not_run"))
    drc_ok = drc_status in {"pass", "unsupported", "partial", "not_run"} or allow_drc_fail
    lvs_ok = lvs_status in {"pass", "unsupported", "partial", "not_run"} or allow_lvs_fail
    if drc_status == "fail" and not allow_drc_fail:
        drc_ok = False
    if lvs_status == "fail" and not allow_lvs_fail:
        lvs_ok = False
    return drc_ok and lvs_ok


def _post_synth_targets_met(results: dict[str, Any], allow_fail: bool) -> bool:
    if not isinstance(results, dict):
        return True
    if bool(results.get("behavior_match")):
        return True
    classification = str(results.get("final_classification", "not_run"))
    if classification in {"unsupported", "not_run"}:
        return True
    return allow_fail


def _default_post_synth_summary(enabled: bool) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "behavior_match": False,
        "mismatch_kind": "not_run",
        "primary_mismatch": "not_run",
        "ordered_mismatches": [],
        "returncode": None,
        "mismatch_count": 0,
        "repair_attempts": [],
        "reference_source": None,
        "post_synth_source": None,
        "evidence_paths": [],
        "attempts": [],
        "best_attempt_index": None,
        "final_classification": "not_run",
        "reasons": [],
        "reason": None,
        "failure_kind": None,
    }


def _build_synthesis_stage_summary(synth_result: OpenROADRunResult | None) -> dict[str, Any]:
    failure_kind = None
    if synth_result is not None:
        failure_kind = synth_result.get("failure_kind")
        if failure_kind is None and synth_result.get("returncode") not in {None, 0}:
            failure_kind = classify_openroad_failure(
                str(synth_result.get("stdout", "")),
                str(synth_result.get("stderr", "")),
                synth_result.get("returncode"),
                str(synth_result.get("target", "synth")),
            )
    return {
        "status": synth_result.get("status", "not_run") if synth_result else "not_run",
        "failure_kind": failure_kind,
        "returncode": synth_result.get("returncode") if synth_result else None,
        "command": synth_result.get("command") if synth_result else None,
        "synthesized_netlist_path": _relative(synth_result.get("synthesized_netlist_path")) if synth_result and synth_result.get("synthesized_netlist_path") else None,
        "retry_attempted": False,
        "retry_reason": "elevated retry is unavailable from pipeline runtime" if failure_kind == "infrastructure" else None,
    }


def _run_post_synth_verification_once(
    top: str,
    bundle: CollateralBundle,
    flow_root: Path,
    rtl_path: Path,
    tb_path: Path | None,
    attempt: int,
    strategy: dict[str, Any] | None = None,
    config_path: Path | None = None,
    work_label: str = "post_synth",
) -> tuple[OpenROADRunResult, dict[str, Any]]:
    synth_config = config_path or bundle.config_mk
    synth_result = run_openroad_stage(flow_root, synth_config, "synth")
    work_dir = BUILD_DIR / "flow" / top / work_label / f"attempt_{attempt}"
    evidence_paths: list[str] = []
    synthesized_netlist = synth_result.get("report_paths", {}).get("synthesized_netlist") if isinstance(synth_result.get("report_paths"), dict) else None
    if synth_result.get("log_path"):
        evidence_paths.append(str(synth_result.get("log_path")))
    if tb_path is None or not tb_path.exists():
        return synth_result, {
            "enabled": True,
            "behavior_match": False,
            "mismatch_kind": "unsupported",
            "returncode": 1,
            "mismatch_count": 1,
            "repair_attempts": [],
            "reference_source": rtl_path.as_posix(),
            "post_synth_source": synthesized_netlist.as_posix() if isinstance(synthesized_netlist, Path) else None,
            "evidence_paths": evidence_paths,
            "final_classification": "unsupported",
            "reasons": ["post-synthesis verification requires a generated testbench"],
        }
    if not should_run_post_synth_equivalence(synth_result, synthesized_netlist):
        failure_kind = synth_result.get("failure_kind")
        reason = "synthesis did not complete"
        if failure_kind == "infrastructure":
            reason = "synthesis did not complete because the environment could not write ORFS outputs"
        return synth_result, {
            "enabled": False,
            "behavior_match": False,
            "mismatch_kind": "not_run",
            "primary_mismatch": "not_run",
            "ordered_mismatches": [],
            "returncode": synth_result.get("returncode"),
            "mismatch_count": 0,
            "repair_attempts": [],
            "reference_source": rtl_path.as_posix(),
            "post_synth_source": synthesized_netlist.as_posix() if isinstance(synthesized_netlist, Path) else None,
            "evidence_paths": evidence_paths,
            "final_classification": "not_run",
            "reasons": [reason],
            "reason": reason,
            "failure_kind": failure_kind,
        }
    if not isinstance(synthesized_netlist, Path) or not synthesized_netlist.exists():
        return synth_result, {
            "enabled": False,
            "behavior_match": False,
            "mismatch_kind": "not_run",
            "primary_mismatch": "not_run",
            "ordered_mismatches": [],
            "returncode": 1,
            "mismatch_count": 0,
            "repair_attempts": [],
            "reference_source": rtl_path.as_posix(),
            "post_synth_source": None,
            "evidence_paths": evidence_paths,
            "final_classification": "not_run",
            "reasons": ["synthesis did not complete"],
            "reason": "synthesis did not complete",
            "failure_kind": synth_result.get("failure_kind"),
        }

    synth_ports = extract_module_ports(synthesized_netlist, top) if isinstance(synthesized_netlist, Path) else {}
    tb_variant = prepare_post_synth_testbench(
        tb_path,
        top,
        work_dir,
        strategy=strategy,
        module_ports=synth_ports,
    )
    tb_for_attempt = tb_variant.get("path", tb_path)
    evidence_paths.extend(str(path) for path in tb_variant.get("generated_files", []))
    rtl_reference = run_rtl_reference_simulation(rtl_path, tb_for_attempt, top, work_dir)
    post_synth = run_post_synth_simulation(synthesized_netlist, tb_for_attempt, f"{top}_post_synth", work_dir)
    comparison = compare_behaviors(rtl_reference, post_synth)
    classified = classify_behavior_mismatch(comparison)
    return synth_result, {
        "enabled": True,
        "behavior_match": bool(comparison.get("behavior_match")),
        "mismatch_kind": classified.get("mismatch_kind"),
        "primary_mismatch": classified.get("primary_mismatch"),
        "ordered_mismatches": classified.get("ordered_mismatches", []),
        "returncode": post_synth.get("returncode"),
        "mismatch_count": int(comparison.get("mismatch_count", 0) or 0),
        "repair_attempts": [],
        "reference_source": comparison.get("reference_source"),
        "post_synth_source": comparison.get("post_synth_source"),
        "evidence_paths": list(dict.fromkeys([*comparison.get("evidence_paths", []), *evidence_paths])),
        "reference_result": rtl_reference,
        "post_synth_result": post_synth,
        "comparison": comparison,
        "classification": classified,
        "final_classification": "pass" if comparison.get("behavior_match") else "fail",
        "reasons": classified.get("reasons", []),
        "reason": None,
        "failure_kind": None,
        "first_mismatch_details": classified.get("first_mismatch_details"),
        "testbench_used": str(tb_for_attempt),
        "testbench_adaptation": tb_variant,
    }


def _run_post_synth_verification_loop(
    top: str,
    bundle: CollateralBundle,
    flow_root: Path,
    rtl_path: Path,
    tb_path: Path | None,
    ir: Any,
    max_iters: int,
) -> tuple[CollateralBundle, OpenROADRunResult | None, dict[str, Any]]:
    summary = _default_post_synth_summary(True)
    attempts: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []
    last_synth_result: OpenROADRunResult | None = None
    current_bundle = bundle
    strategy_state: dict[str, Any] = {"verification_modes": [], "notes": [], "applied_suggestions": []}

    for attempt in range(1, max(1, max_iters) + 1):
        synth_result, verification = _run_post_synth_verification_once(
            top,
            current_bundle,
            flow_root,
            rtl_path,
            tb_path,
            attempt,
            strategy=strategy_state,
        )
        last_synth_result = synth_result
        classification = classify_post_synth_mismatch(
            verification.get("classification", {"mismatch_kind": verification.get("mismatch_kind"), "reasons": verification.get("reasons", [])})
        )
        attempt_record = {
            "attempt": attempt,
            "enabled": verification.get("enabled"),
            "behavior_match": verification.get("behavior_match"),
            "mismatch_kind": verification.get("mismatch_kind"),
            "primary_mismatch": verification.get("primary_mismatch"),
            "ordered_mismatches": verification.get("ordered_mismatches", []),
            "returncode": verification.get("returncode"),
            "mismatch_count": verification.get("mismatch_count"),
            "reference_source": verification.get("reference_source"),
            "post_synth_source": verification.get("post_synth_source"),
            "evidence_paths": verification.get("evidence_paths", []),
            "testbench_used": verification.get("testbench_used"),
            "testbench_adaptation": verification.get("testbench_adaptation", {}),
            "reason": verification.get("reason"),
            "failure_kind": verification.get("failure_kind"),
            "bottleneck_classification": classification,
            "chosen_action_family": "none",
            "repair_suggestions": [],
        }
        attempts.append(attempt_record)
        if not verification.get("enabled"):
            break
        if verification.get("behavior_match") or verification.get("final_classification") == "unsupported":
            break

        suggestions = suggest_post_synth_repairs(classification, {"vars": {}})
        attempt_record["repair_suggestions"] = suggestions
        if not suggestions:
            break
        strategy_state = apply_post_synth_strategy(strategy_state, suggestions)
        action_family = str(strategy_state.get("chosen_action_family", "none"))
        attempt_record["chosen_action_family"] = action_family
        repair_record = {
            "attempt": attempt,
            "mismatch_kind": classification.get("bottleneck_classification"),
            "primary_mismatch": classification.get("primary_mismatch"),
            "chosen_repair_family": action_family,
            "files_changed": verification.get("testbench_adaptation", {}).get("generated_files", []),
            "result_after_rerun": "pending",
        }
        if strategy_state.get("last_repair"):
            repair_record.update(strategy_state.get("last_repair"))
        if strategy_state.get("regenerate_collateral"):
            current_bundle = generate_collateral(ROOT, ir, rtl_path, tb_path=tb_path, injected_fault=None)
            repair_record["files_changed"] = repair_record.get("files_changed", []) + [str(current_bundle.config_mk)]
            repairs.append(repair_record)
            continue
        repairs.append(repair_record)
        if strategy_state.get("regenerate_rtl"):
            break
        if strategy_state.get("verification_modes"):
            continue
        break

    best_attempt = next((item for item in attempts if item.get("behavior_match")), attempts[-1] if attempts else None)
    for repair in repairs:
        followup = next((item for item in attempts if item.get("attempt") == repair.get("attempt", 0) + 1), None)
        if followup is not None:
            repair["result_after_rerun"] = "match" if followup.get("behavior_match") else str(followup.get("mismatch_kind"))
            if not repair.get("files_changed"):
                repair["files_changed"] = followup.get("testbench_adaptation", {}).get("generated_files", [])
    if best_attempt:
        summary.update(
            {
                "behavior_match": bool(best_attempt.get("behavior_match")),
                "mismatch_kind": best_attempt.get("mismatch_kind"),
                "primary_mismatch": best_attempt.get("primary_mismatch"),
                "ordered_mismatches": best_attempt.get("ordered_mismatches", []),
                "returncode": best_attempt.get("returncode"),
                "mismatch_count": best_attempt.get("mismatch_count"),
                "reference_source": best_attempt.get("reference_source"),
                "post_synth_source": best_attempt.get("post_synth_source"),
                "evidence_paths": best_attempt.get("evidence_paths", []),
                "best_attempt_index": best_attempt.get("attempt"),
                "enabled": bool(best_attempt.get("enabled")),
                "final_classification": (
                    "pass"
                    if best_attempt.get("behavior_match")
                    else ("not_run" if not best_attempt.get("enabled") else best_attempt.get("mismatch_kind", "fail"))
                ),
                "reasons": list((best_attempt.get("bottleneck_classification") or {}).get("reasons", [])),
                "reason": best_attempt.get("reason"),
                "failure_kind": best_attempt.get("failure_kind"),
            }
        )
    summary["attempts"] = attempts
    summary["repair_attempts"] = repairs
    return current_bundle, last_synth_result, summary


def _effective_bottleneck(metrics: dict[str, Any], signoff: dict[str, Any]) -> dict[str, Any]:
    signoff_classification = classify_signoff_bottleneck(signoff)
    if signoff_classification.get("metric_kind") != "unknown":
        return signoff_classification
    return classify_qor_bottleneck(metrics)


def _improvement_amount(before: dict[str, Any], after: dict[str, Any], metric_kind: str) -> float | None:
    if metric_kind == "setup":
        before_value = before.get("timing", {}).get("setup_violation_count")
        after_value = after.get("timing", {}).get("setup_violation_count")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "hold":
        before_value = before.get("timing", {}).get("hold_violation_count")
        after_value = after.get("timing", {}).get("hold_violation_count")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "timing":
        before_value = before.get("timing", {}).get("wns_ns")
        after_value = after.get("timing", {}).get("wns_ns")
        return None if before_value is None or after_value is None else float(after_value) - float(before_value)
    if metric_kind == "logical_area":
        before_value = before.get("area", {}).get("logical_um2")
        after_value = after.get("area", {}).get("logical_um2")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "physical_area":
        before_value = before.get("area", {}).get("physical_um2")
        after_value = after.get("area", {}).get("physical_um2")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "power":
        before_value = before.get("power", {}).get("mw")
        after_value = after.get("power", {}).get("mw")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "congestion":
        before_value = before.get("routability", {}).get("congestion")
        after_value = after.get("routability", {}).get("congestion")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    if metric_kind == "routability":
        before_value = before.get("routability", {}).get("congestion")
        after_value = after.get("routability", {}).get("congestion")
        return None if before_value is None or after_value is None else float(before_value) - float(after_value)
    return None


def _copy_selected_reports(top: str, attempt: int, result: OpenROADRunResult | None) -> dict[str, str]:
    copied: dict[str, str] = {}
    if result is None:
        return copied
    snapshot_dir = BUILD_DIR / "flow" / top / "qor_attempts" / f"attempt_{attempt}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for label in ["reports", "logs", "results"]:
        for path in result.get("report_paths", {}).get(label, []):
            if path.name not in {"6_finish.rpt", "synth_stat.txt", "6_report.json", "5_1_grt.log", "clock_period.txt"}:
                continue
            target = snapshot_dir / path.name
            try:
                target.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
            except OSError:
                continue
            copied[path.name] = _relative(target) or str(target)
    if result.get("log_path") and result.get("log_path").exists():
        target = snapshot_dir / result.get("log_path").name
        try:
            target.write_text(result.get("log_path").read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        except OSError:
            return copied
        copied[result.get("log_path").name] = _relative(target) or str(target)
    return copied


def _build_qor_attempt_record(
    attempt: int,
    result: OpenROADRunResult | None,
    targets: dict[str, Any],
    bottlenecks: dict[str, Any],
    action: list[dict[str, Any]],
    config_path: Path | None,
    snapshot_paths: dict[str, str],
    baseline_metrics: dict[str, Any],
    action_family_matches_bottleneck: bool,
    candidate: dict[str, Any] | None,
    spec_name: str,
    design_kind: str | None,
    baseline_score: float,
    behavior_match: bool | None = None,
    post_synth_pass: bool | None = None,
) -> dict[str, Any]:
    metrics = result.get("qor_metrics", {}) if result else {}
    signoff = result.get("signoff", {}) if result else {}
    merged_metrics = merge_signoff_with_qor(metrics, signoff)
    score, score_reasons = score_qor(metrics, targets)
    score += float(merged_metrics.get("signoff_score_adjustment", 0.0) or 0.0)
    score_reasons.extend(list(merged_metrics.get("signoff_score_reasons", [])))
    metric_kind = str(bottlenecks.get("metric_kind", "unknown"))
    chosen_action_family = (
        str(candidate.get("family"))
        if candidate and candidate.get("family")
        else next((item.get("action_family") for item in action if item.get("action_family") not in {None, "reject"}), "none")
    )
    improvement_amount = _improvement_amount(baseline_metrics, metrics, metric_kind)
    return {
        "attempt": attempt,
        "spec_name": spec_name,
        "design_kind": design_kind,
        "target": result.get("target") if result else None,
        "status": result.get("status") if result else "not_run",
        "returncode": result.get("returncode") if result else None,
        "command": result.get("command") if result else None,
        "config_path": _relative(config_path) if config_path else None,
        "metrics": metrics,
        "signoff": signoff,
        "metric_kind": metric_kind,
        "bottleneck_classification": bottlenecks,
        "chosen_action_family": chosen_action_family,
        "chosen_knobs": action,
        "candidate_id": candidate.get("candidate_id") if candidate else None,
        "candidate_family": candidate.get("family") if candidate else None,
        "candidate_why": candidate.get("why_this_candidate") if candidate else None,
        "candidate_ml_predicted_score": candidate.get("ml_predicted_score") if candidate else None,
        "candidate_ml_ranking_reason": candidate.get("ml_ranking_reason") if candidate else None,
        "candidate_ml_features": candidate.get("ml_features") if candidate else None,
        "metric_source_file": bottlenecks.get("metric_source_file"),
        "tuning_action": action,
        "score": score,
        "score_before": baseline_score,
        "score_delta": score - baseline_score,
        "score_reasons": score_reasons,
        "targets_met": _metrics_meet_targets(metrics, targets),
        "signoff_targets_met": _signoff_targets_met(signoff, False, False),
        "improvement_amount": improvement_amount,
        "beat_baseline": score > baseline_score,
        "behavior_match": behavior_match,
        "post_synth_pass": post_synth_pass,
        "action_family_matched_bottleneck": action_family_matches_bottleneck,
        "snapshot_paths": snapshot_paths,
    }


def _build_ml_history_entry(attempt_record: dict[str, Any]) -> dict[str, Any]:
    entry = {
        "timestamp": None,
        "spec_name": attempt_record.get("spec_name"),
        "design_kind": attempt_record.get("design_kind"),
        "metric_kind": attempt_record.get("metric_kind"),
        "bottleneck_classification": (attempt_record.get("bottleneck_classification") or {}).get("bottleneck_classification")
        if isinstance(attempt_record.get("bottleneck_classification"), dict)
        else attempt_record.get("bottleneck_classification"),
        "primary_bottleneck": (attempt_record.get("bottleneck_classification") or {}).get("primary_bottleneck")
        if isinstance(attempt_record.get("bottleneck_classification"), dict)
        else None,
        "candidate_family": attempt_record.get("candidate_family", attempt_record.get("chosen_action_family")),
        "candidate_id": attempt_record.get("candidate_id"),
        "candidate_knobs": [
            str(item.get("knob"))
            for item in attempt_record.get("chosen_knobs", [])
            if isinstance(item, dict) and item.get("knob")
        ],
        "chosen_knobs": attempt_record.get("chosen_knobs", []),
        "qor_metrics": attempt_record.get("metrics", {}),
        "signoff_metrics": attempt_record.get("signoff", {}),
        "behavior_match": attempt_record.get("behavior_match"),
        "post_synth_pass": attempt_record.get("post_synth_pass"),
        "score": attempt_record.get("score"),
        "score_before": attempt_record.get("score_before"),
        "score_delta": attempt_record.get("score_delta"),
        "improvement_amount": attempt_record.get("improvement_amount"),
        "beat_baseline": attempt_record.get("beat_baseline"),
        "targets_met": attempt_record.get("targets_met"),
        "signoff_targets_met": attempt_record.get("signoff_targets_met"),
        "status": attempt_record.get("status"),
    }
    return entry


def _copy_selected_synth_reports(top: str, attempt: int, result: OpenROADRunResult | None) -> dict[str, str]:
    copied: dict[str, str] = {}
    if result is None:
        return copied
    snapshot_dir = BUILD_DIR / "flow" / top / "synth_attempts" / f"attempt_{attempt}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for label in ["reports", "logs", "results"]:
        for path in result.get("report_paths", {}).get(label, []):
            if path.name not in {"synth_stat.txt", "1_synth.json", "1_2_yosys.v", "clock_period.txt"}:
                continue
            try:
                if path.suffix in {".v", ".json", ".txt", ".log"}:
                    target = snapshot_dir / path.name
                    target.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                    copied[path.name] = _relative(target) or str(target)
            except OSError:
                continue
    return copied


def _build_synth_attempt_record(
    attempt: int,
    result: OpenROADRunResult | None,
    targets: dict[str, Any],
    bottleneck: dict[str, Any],
    action: list[dict[str, Any]],
    config_path: Path | None,
    snapshot_paths: dict[str, str],
    baseline_metrics: dict[str, Any],
    behavior_match: bool,
    candidate: dict[str, Any] | None,
    baseline_score: float,
) -> dict[str, Any]:
    metrics = result.get("qor_metrics", {}) if result else {}
    score, reasons = score_synth(metrics, targets, behavior_match=behavior_match)
    logical_before = baseline_metrics.get("area", {}).get("logical_um2") if isinstance(baseline_metrics.get("area"), dict) else None
    logical_after = metrics.get("area", {}).get("logical_um2") if isinstance(metrics.get("area"), dict) else None
    improvement_amount = None if logical_before is None or logical_after is None else float(logical_before) - float(logical_after)
    return {
        "attempt": attempt,
        "target": result.get("target") if result else "synth",
        "status": result.get("status") if result else "not_run",
        "returncode": result.get("returncode") if result else None,
        "command": result.get("command") if result else None,
        "config_path": _relative(config_path) if config_path else None,
        "metrics": metrics,
        "metric_kind": bottleneck.get("metric_kind", "unknown"),
        "bottleneck_classification": bottleneck,
        "chosen_action_family": candidate.get("family") if candidate else "baseline",
        "chosen_knobs": action,
        "candidate_id": candidate.get("candidate_id") if candidate else None,
        "candidate_family": candidate.get("family") if candidate else None,
        "candidate_why": candidate.get("why_this_candidate") if candidate else None,
        "candidate_predicted_score": candidate.get("predicted_score") if candidate else None,
        "candidate_ranking_reason": candidate.get("ranking_reason") if candidate else None,
        "behavior_match": behavior_match,
        "score": score,
        "score_before": baseline_score,
        "score_delta": score - baseline_score,
        "score_reasons": reasons,
        "improvement_amount": improvement_amount,
        "beat_baseline": score > baseline_score,
        "targets_met": _synth_targets_met(metrics, targets, behavior_match),
        "snapshot_paths": snapshot_paths,
        "synthesized_netlist_path": _relative(result.get("synthesized_netlist_path")) if result and result.get("synthesized_netlist_path") else None,
    }


def _build_synth_history_entry(
    attempt_record: dict[str, Any],
    spec_name: str,
    design_kind: str | None,
) -> dict[str, Any]:
    return {
        "spec_name": spec_name,
        "design_kind": design_kind,
        "metric_kind": attempt_record.get("metric_kind"),
        "bottleneck_classification": (attempt_record.get("bottleneck_classification") or {}).get("bottleneck_classification")
        if isinstance(attempt_record.get("bottleneck_classification"), dict)
        else attempt_record.get("bottleneck_classification"),
        "candidate_family": attempt_record.get("candidate_family"),
        "candidate_id": attempt_record.get("candidate_id"),
        "candidate_knobs": [
            str(item.get("knob"))
            for item in attempt_record.get("chosen_knobs", [])
            if isinstance(item, dict) and item.get("knob")
        ],
        "metrics": attempt_record.get("metrics", {}),
        "behavior_match": attempt_record.get("behavior_match"),
        "score": attempt_record.get("score"),
        "score_before": attempt_record.get("score_before"),
        "score_delta": attempt_record.get("score_delta"),
        "improvement_amount": attempt_record.get("improvement_amount"),
        "beat_baseline": attempt_record.get("beat_baseline"),
        "targets_met": attempt_record.get("targets_met"),
    }


def _run_synth_optimization_loop(
    top: str,
    bundle: CollateralBundle,
    flow_root: Path,
    rtl_path: Path,
    tb_path: Path | None,
    targets: dict[str, Any],
    max_iters: int,
    min_attempts: int,
    spec_name: str,
    design_kind: str | None,
) -> tuple[CollateralBundle, OpenROADRunResult | None, dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    design_dir = bundle.design_dir
    history_path = DEFAULT_SYNTH_HISTORY_PATH
    synth_history = load_synth_history(history_path)
    candidate_rankings: list[dict[str, Any]] = []
    base_config = _load_config_mk(bundle.config_mk)
    base_config["vars"] = dict(base_config.get("vars", {}))
    base_config["order"] = list(base_config.get("order", []))

    baseline_result, baseline_verification = _run_post_synth_verification_once(
        top,
        bundle,
        flow_root,
        rtl_path,
        tb_path,
        1,
        config_path=bundle.config_mk,
        work_label="synth_opt",
    )
    baseline_metrics = dict(baseline_result.get("qor_metrics", {}))
    baseline_metrics["targets"] = dict(targets)
    baseline_result["qor_metrics"] = baseline_metrics
    baseline_bottleneck = classify_synth_bottleneck(baseline_metrics)
    baseline_snapshot = _copy_selected_synth_reports(top, 1, baseline_result)
    baseline_record = _build_synth_attempt_record(
        1,
        baseline_result,
        targets,
        baseline_bottleneck,
        [],
        bundle.config_mk,
        baseline_snapshot,
        baseline_metrics,
        bool(baseline_verification.get("behavior_match")),
        None,
        0.0,
    )
    baseline_record["score_before"] = baseline_record["score"]
    baseline_record["score_delta"] = 0.0
    attempts.append(baseline_record)
    update_synth_history(_build_synth_history_entry(baseline_record, spec_name, design_kind), history_path)
    synth_history.append(_build_synth_history_entry(baseline_record, spec_name, design_kind))
    best_result = baseline_result
    best_record = baseline_record
    best_config = dict(base_config)
    best_config_path = bundle.config_mk
    best_score = baseline_record["score"]
    why_stopped = "max_iters_reached"
    explicit_targets = any(value is not None for key, value in targets.items() if key in {"logical_area", "area", "power", "cell_count"})
    min_required_attempts = max(3, int(min_attempts))
    attempt_budget = max(int(max_iters), min_required_attempts)

    if baseline_record["targets_met"] and explicit_targets:
        why_stopped = "targets_met"
    else:
        attempt_index = 2
        attempted_ids: set[str] = set()
        round_index = 1
        while attempt_index <= attempt_budget:
            current_metrics = dict(best_result.get("qor_metrics", {}))
            current_metrics["targets"] = dict(targets)
            bottleneck = classify_synth_bottleneck(current_metrics)
            candidates = generate_synth_candidates(best_config, bottleneck)
            ranked_candidates = rank_synth_candidates(
                candidates,
                synth_history,
                bottleneck=bottleneck,
                context={"spec_name": spec_name, "design_kind": design_kind},
            )
            candidate_rankings.append(
                {
                    "round": round_index,
                    "metric_kind": bottleneck.get("metric_kind"),
                    "bottleneck_classification": bottleneck.get("bottleneck_classification"),
                    "rankings": [
                        {
                            "rank": item.get("rank"),
                            "candidate_id": item.get("candidate_id"),
                            "candidate_family": item.get("family"),
                            "predicted_score": item.get("predicted_score"),
                            "ranking_reason": item.get("ranking_reason"),
                        }
                        for item in ranked_candidates
                    ],
                }
            )
            selected_batch = select_synth_candidates_for_round(
                ranked_candidates,
                attempted_ids,
                max_candidates=min(3, max(1, attempt_budget - attempt_index + 1)),
                min_families=3,
            )
            if not selected_batch:
                why_stopped = "forced_min_attempts_completed" if len(attempts) >= min_required_attempts else "no_further_improvement"
                break
            for selected in selected_batch:
                attempted_ids.add(str(selected.get("candidate_id")))
                trial_config = {
                    "vars": dict(best_config.get("vars", {})),
                    "order": list(best_config.get("order", [])),
                    "applied_suggestions": list(best_config.get("applied_suggestions", [])),
                    "notes": list(best_config.get("notes", [])),
                    "chosen_action_family": "none",
                    "action_family_matches_bottleneck": True,
                }
                knob_suggestions = [dict(knob, action_family=selected["family"], metric_kind=bottleneck.get("metric_kind")) for knob in selected.get("knobs", [])]
                trial_config = synth_candidate_to_config(selected, trial_config)
                config_path = design_dir / f"config_synth_round_{round_index}_{selected['candidate_id']}.mk"
                _write_config_mk(config_path, trial_config)
                result, verification = _run_post_synth_verification_once(
                    top,
                    bundle,
                    flow_root,
                    rtl_path,
                    tb_path,
                    attempt_index,
                    config_path=config_path,
                    work_label="synth_opt",
                )
                result_metrics = dict(result.get("qor_metrics", {}))
                result_metrics["targets"] = dict(targets)
                result["qor_metrics"] = result_metrics
                snapshot = _copy_selected_synth_reports(top, attempt_index, result)
                attempt_record = _build_synth_attempt_record(
                    attempt_index,
                    result,
                    targets,
                    bottleneck,
                    knob_suggestions,
                    config_path,
                    snapshot,
                    baseline_metrics,
                    bool(verification.get("behavior_match")),
                    selected,
                    baseline_record["score"],
                )
                attempts.append(attempt_record)
                history_entry = _build_synth_history_entry(attempt_record, spec_name, design_kind)
                update_synth_history(history_entry, history_path)
                synth_history.append(history_entry)

                if attempt_record["behavior_match"] and attempt_record["score"] > best_score:
                    best_score = attempt_record["score"]
                    best_result = result
                    best_record = attempt_record
                    best_config = trial_config
                    best_config_path = config_path

                attempt_index += 1
                if attempt_index > attempt_budget:
                    break

            attempts_done = len(attempts)
            if attempts_done < min_required_attempts:
                round_index += 1
                continue
            if explicit_targets and best_record.get("targets_met"):
                why_stopped = "targets_met"
                break
            if attempt_index > attempt_budget:
                why_stopped = "max_iters_reached"
                break
            round_index += 1

    if best_config_path != bundle.config_mk:
        bundle.config_mk = best_config_path
        if best_config_path not in bundle.generated_files:
            bundle.generated_files.append(best_config_path)

    summary = {
        "enabled": True,
        "targets": targets,
        "baseline_metrics": baseline_metrics,
        "attempts": attempts,
        "best_attempt_index": best_record.get("attempt"),
        "best_score": best_score,
        "best_netlist_path": best_record.get("synthesized_netlist_path"),
        "selected_config_path": _relative(best_config_path),
        "improvement_amount": best_record.get("improvement_amount", 0.0),
        "targets_met": best_record.get("targets_met", False),
        "behavior_match": best_record.get("behavior_match"),
        "stop_reason": why_stopped,
        "candidate_rankings": candidate_rankings,
        "why_the_best_candidate_won": (
            "baseline synthesis remained best because no candidate improved the synthesized netlist score"
            if best_record.get("attempt") == 1
            else f"candidate {best_record.get('candidate_id')} produced the best behavior-matching synthesized netlist"
        ),
        "why_the_loop_stopped": why_stopped,
    }
    return bundle, best_result, summary


def _run_qor_optimization_loop(
    top: str,
    bundle: CollateralBundle,
    mode: str,
    baseline_result: OpenROADRunResult,
    targets: dict[str, Any],
    max_iters: int,
    min_attempts: int,
    flow_root: Path,
    signoff_enabled: bool,
    max_signoff_iters: int,
    signoff_only: bool,
    allow_drc_fail: bool,
    allow_lvs_fail: bool,
    ir: Any,
    rtl_path: Path,
    tb_path: Path | None,
    spec_name: str,
    design_kind: str | None,
    ml_tune: bool,
    persist_ml_history: bool,
    post_synth_verification: dict[str, Any] | None,
) -> tuple[OpenROADRunResult, dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    design_dir = bundle.design_dir
    target_name = "synth" if mode == "synth" else "finish"
    ml_history_path = DEFAULT_ML_HISTORY_PATH
    ml_history = load_ml_history(ml_history_path) if ml_tune else []
    persist_history = bool(ml_tune or persist_ml_history)
    ml_candidate_rankings: list[dict[str, Any]] = []
    ml_features_used = [
        "spec_name",
        "design_kind",
        "metric_kind",
        "bottleneck_classification",
        "candidate_family",
        "candidate_knobs",
        "timing_pressure",
        "setup_violations",
        "hold_violations",
        "logical_area_um2",
        "physical_area_um2",
        "power_mw",
        "congestion",
        "utilization",
        "clock_period_ns",
    ]

    base_config = _load_config_mk(bundle.config_mk)
    base_config["vars"] = dict(base_config.get("vars", {}))
    base_config["order"] = list(base_config.get("order", []))

    baseline_metrics = dict(baseline_result.get("qor_metrics", {}))
    baseline_metrics["targets"] = dict(targets)
    baseline_result["qor_metrics"] = baseline_metrics
    baseline_signoff = baseline_result.get("signoff", {}) if signoff_enabled else {}
    baseline_classification = _effective_bottleneck(baseline_metrics, baseline_signoff)
    baseline_snapshot = _copy_selected_reports(top, 1, baseline_result)
    baseline_record = _build_qor_attempt_record(
        attempt=1,
        result=baseline_result,
        targets=targets,
        bottlenecks=baseline_classification,
        action=[],
        config_path=bundle.config_mk,
        snapshot_paths=baseline_snapshot,
        baseline_metrics=baseline_metrics,
        action_family_matches_bottleneck=True,
        candidate=None,
        spec_name=spec_name,
        design_kind=design_kind,
        baseline_score=0.0,
        behavior_match=post_synth_verification.get("behavior_match") if isinstance(post_synth_verification, dict) else None,
        post_synth_pass=_post_synth_targets_met(post_synth_verification or {}, False) if isinstance(post_synth_verification, dict) else None,
    )
    baseline_record["score_before"] = baseline_record["score"]
    baseline_record["score_delta"] = 0.0
    baseline_record["beat_baseline"] = False
    attempts.append(baseline_record)
    if ml_tune:
        baseline_history_entry = _build_ml_history_entry(baseline_record)
        ml_history.append(baseline_history_entry)
        if persist_history:
            update_ml_history(baseline_history_entry, ml_history_path)

    best_result = baseline_result
    best_record = baseline_record
    best_config = dict(base_config)
    best_config["vars"] = dict(base_config.get("vars", {}))
    best_config["order"] = list(base_config.get("order", []))
    best_config_path = bundle.config_mk
    best_score = baseline_record["score"]
    why_loop_stopped = "max iterations exhausted"
    candidate_registry_used: list[str] = []
    repairs_attempted: list[dict[str, Any]] = []
    attempt_index = 2
    total_rounds = 0
    stop_reason = "max_iters_reached"
    attempted_candidate_ids: set[str] = set()

    baseline_signoff_met = _signoff_targets_met(baseline_signoff, allow_drc_fail, allow_lvs_fail)
    if _metrics_meet_targets(baseline_metrics, targets) and (not signoff_enabled or baseline_signoff_met):
        why_loop_stopped = "baseline already met all QoR targets"
        stop_reason = "targets_met"
    else:
        min_rounds = max(0, min_attempts - 1)
        planned_qor_rounds = 0 if signoff_only else max(max(0, max_iters), min_rounds)
        planned_rounds = planned_qor_rounds + (max(0, max_signoff_iters) if signoff_enabled else 0)
        for round_index in range(1, max(1, planned_rounds) + 1):
            total_rounds = round_index
            current_metrics = dict(best_result.get("qor_metrics", {}))
            current_metrics["targets"] = dict(targets)
            best_result["qor_metrics"] = current_metrics
            current_signoff = best_result.get("signoff", {}) if signoff_enabled else {}
            classification = _effective_bottleneck(current_metrics, current_signoff)
            if classification.get("metric_kind") == "unknown":
                if round_index >= max(1, max_iters):
                    why_loop_stopped = "no dominant bottleneck remained after classification"
                    stop_reason = "max_iters_reached"
                    break
                classification = dict(classification)
                classification["metric_kind"] = "timing"
                classification["primary_bottleneck"] = "timing"
                classification["bottleneck_classification"] = "timing"
                classification["action_family_hint"] = "timing"
                classification["ordered_bottlenecks"] = ["timing", "logical_area", "power"]
                classification["reasons"] = ["forced minimum QoR exploration continues despite no dominant bottleneck"]
            if _metrics_meet_targets(current_metrics, targets) and _signoff_targets_met(current_signoff, allow_drc_fail, allow_lvs_fail):
                why_loop_stopped = "targets met"
                stop_reason = "targets_met"
                break

            signoff_classification = classification.get("primary_bottleneck") in {"drc", "lvs"} or (
                classification.get("bottleneck_classification") == "mixed"
                and any(item in {"drc", "lvs"} for item in classification.get("ordered_bottlenecks", []) if isinstance(item, str))
            )

            if signoff_classification:
                raw_repairs = suggest_signoff_repairs(classification, best_config)
                candidates = [
                    {
                        "family": str(repair.get("action_family", "none")),
                        "candidate_id": f"signoff_{classification.get('primary_bottleneck')}_{index}",
                        "family_priority_rank": index,
                        "metric_kind_it_targets": repair.get("metric_kind"),
                        "why_this_candidate": repair.get("reason"),
                        "knobs": [dict(repair)],
                        "mismatch": False,
                        "rejected": False,
                        "reject_reason": None,
                        "action_family_matched_bottleneck": str(repair.get("action_family")) == str(classification.get("action_family_hint")),
                    }
                    for index, repair in enumerate(raw_repairs, start=1)
                ]
            else:
                candidates = generate_qor_candidates(current_metrics, classification, best_config)
            family_order = [candidate["family"] for candidate in candidates if candidate["family"] not in candidate_registry_used]
            candidate_registry_used.extend(item for item in family_order if item not in candidate_registry_used)
            ranked_candidates = rank_qor_candidates(
                candidates,
                ml_history if ml_tune else [],
                current_metrics,
                classification,
                {"spec_name": spec_name, "design_kind": design_kind},
            )
            ml_candidate_rankings.append(
                {
                    "round": round_index,
                    "metric_kind": classification.get("metric_kind"),
                    "bottleneck_classification": classification.get("bottleneck_classification"),
                    "rankings": [
                        {
                            "rank": item.get("ml_rank"),
                            "candidate_id": item.get("candidate_id"),
                            "candidate_family": item.get("family"),
                            "predicted_score": item.get("ml_predicted_score"),
                            "ranking_reason": item.get("ml_ranking_reason"),
                            "rejected": item.get("rejected"),
                            "reject_reason": item.get("reject_reason"),
                        }
                        for item in ranked_candidates
                    ],
                }
            )

            selected_candidate = next(
                (
                    candidate
                    for candidate in ranked_candidates
                    if not candidate.get("rejected") and str(candidate.get("candidate_id")) not in attempted_candidate_ids
                ),
                None,
            )
            if selected_candidate is None:
                why_loop_stopped = "no valid ranked candidates remained to explore"
                stop_reason = "no_candidates"
                break

            candidate_id = str(selected_candidate.get("candidate_id"))
            attempted_candidate_ids.add(candidate_id)
            trial_config = {
                "vars": dict(best_config.get("vars", {})),
                "order": list(best_config.get("order", [])),
                "applied_suggestions": list(best_config.get("applied_suggestions", [])),
                "notes": list(best_config.get("notes", [])),
                "chosen_action_family": "none",
                "action_family_matches_bottleneck": True,
            }
            knob_suggestions = [
                dict(knob, action_family=selected_candidate["family"], metric_kind=classification.get("metric_kind"))
                for knob in selected_candidate.get("knobs", [])
            ]
            if signoff_classification:
                trial_config = apply_signoff_strategy(trial_config, knob_suggestions)
            else:
                trial_config = apply_qor_strategy(trial_config, knob_suggestions)
            trial_bundle = bundle
            if any(item.get("knob") == "REGENERATE_COLLATERAL" for item in knob_suggestions):
                trial_bundle = generate_collateral(ROOT, ir, rtl_path, tb_path=tb_path, injected_fault=None)
                repairs_attempted.append(
                    {
                        "attempt": attempt_index,
                        "action_family": selected_candidate["family"],
                        "candidate_id": selected_candidate["candidate_id"],
                        "reason": selected_candidate.get("why_this_candidate"),
                        "kind": "collateral_regeneration",
                    }
                )
            config_path = design_dir / f"config_qor_round_{round_index}_{selected_candidate['candidate_id']}.mk"
            _write_config_mk(config_path, trial_config)

            result = run_openroad_stage(flow_root, config_path, target_name)
            local_log = BUILD_DIR / "flow" / top / "logs" / f"openroad_{mode}_{selected_candidate['candidate_id']}.log"
            local_log.parent.mkdir(parents=True, exist_ok=True)
            combined = (result.get("stdout", "") + ("\n" + result.get("stderr", "") if result.get("stderr") else "")).strip()
            local_log.write_text(combined + ("\n" if combined else ""), encoding="utf-8")
            result["log_path"] = local_log
            result["log_paths"] = [local_log]
            result_metrics = dict(result.get("qor_metrics", {}))
            result_metrics["targets"] = dict(targets)
            result["qor_metrics"] = result_metrics
            snapshot = _copy_selected_reports(top, attempt_index, result)
            attempt_record = _build_qor_attempt_record(
                attempt=attempt_index,
                result=result,
                targets=targets,
                bottlenecks=classification,
                action=knob_suggestions,
                config_path=config_path,
                snapshot_paths=snapshot,
                baseline_metrics=baseline_metrics,
                action_family_matches_bottleneck=bool(trial_config.get("action_family_matches_bottleneck", True))
                and bool(selected_candidate.get("action_family_matched_bottleneck", True)),
                candidate=selected_candidate,
                spec_name=spec_name,
                design_kind=design_kind,
                baseline_score=baseline_record["score"],
                behavior_match=post_synth_verification.get("behavior_match") if isinstance(post_synth_verification, dict) else None,
                post_synth_pass=_post_synth_targets_met(post_synth_verification or {}, False) if isinstance(post_synth_verification, dict) else None,
            )
            attempts.append(attempt_record)
            if ml_tune:
                history_entry = _build_ml_history_entry(attempt_record)
                ml_history.append(history_entry)
                if persist_history:
                    update_ml_history(history_entry, ml_history_path)
            attempt_index += 1

            if attempt_record["score"] > best_score:
                best_score = attempt_record["score"]
                best_result = result
                best_record = attempt_record
                best_config = trial_config
                best_config_path = config_path
                bundle = trial_bundle
                why_loop_stopped = f"round {round_index} improved score with candidate {selected_candidate['candidate_id']}"
            elif len(attempts) >= min_attempts and round_index >= max(1, max_iters):
                why_loop_stopped = f"candidate {selected_candidate['candidate_id']} did not improve score and retry budget is exhausted"
                stop_reason = "max_iters_reached"
                break
            else:
                why_loop_stopped = f"candidate {selected_candidate['candidate_id']} did not beat the current best; reranking next round"

            if attempt_record["targets_met"] and (
                not signoff_enabled or _signoff_targets_met(result.get("signoff", {}), allow_drc_fail, allow_lvs_fail)
            ):
                why_loop_stopped = f"targets met by candidate {selected_candidate['candidate_id']}"
                stop_reason = "targets_met"
                break

    if best_config_path != bundle.config_mk and best_result is not None:
        select_log = BUILD_DIR / "flow" / top / "logs" / f"openroad_{mode}_best_selected.log"
        select_log.parent.mkdir(parents=True, exist_ok=True)
        combined = (best_result.get("stdout", "") + ("\n" + best_result.get("stderr", "") if best_result.get("stderr") else "")).strip()
        select_log.write_text(combined + ("\n" if combined else ""), encoding="utf-8")
        best_result["log_path"] = select_log
        best_result["log_paths"] = [select_log]

    if stop_reason == "forced_min_attempts_completed" and total_rounds >= max(1, max_iters):
        stop_reason = "max_iters_reached"

    summary = {
        "enabled": True,
        "targets": targets,
        "candidate_registry_used": list(QOR_KNOB_REGISTRY.keys()),
        "baseline_metrics": baseline_metrics,
        "attempts": attempts,
        "attempt_metrics": [attempt.get("metrics") for attempt in attempts if isinstance(attempt, dict) and attempt.get("metrics")],
        "score_per_attempt": [{"attempt": attempt.get("attempt"), "score": attempt.get("score")} for attempt in attempts if isinstance(attempt, dict)],
        "best_attempt_index": best_record.get("attempt"),
        "best_score": best_score,
        "final_selected_metrics": best_result.get("qor_metrics", {}) if best_result else {},
        "final_signoff": best_result.get("signoff", {}) if best_result else {},
        "improved": best_score > baseline_record["score"],
        "targets_met": _metrics_meet_targets(best_result.get("qor_metrics", {}) if best_result else {}, targets)
        and _signoff_targets_met(best_result.get("signoff", {}) if best_result else {}, allow_drc_fail, allow_lvs_fail),
        "selected_config_path": _relative(best_config_path),
        "chosen_action_family": best_record.get("chosen_action_family"),
        "metric_kind": best_record.get("metric_kind"),
        "bottleneck_classification": best_record.get("bottleneck_classification"),
        "action_family_matched_bottleneck": best_record.get("action_family_matched_bottleneck"),
        "repairs_attempted": repairs_attempted,
        "signoff_enabled": signoff_enabled,
        "signoff_only": signoff_only,
        "rounds_executed": total_rounds,
        "stop_reason": stop_reason,
        "why_the_best_candidate_won": (
            "baseline remained best because no candidate improved the multi-objective score"
            if best_record.get("attempt") == 1
            else f"candidate {best_record.get('candidate_id')} achieved the highest multi-objective score"
        ),
        "why_the_loop_stopped": why_loop_stopped,
        "ml_tuning": {
            "enabled": ml_tune,
            "history_path": _relative(ml_history_path) if persist_history else _relative(ml_history_path),
            "features_used": ml_features_used,
            "ranking_reason": best_record.get("candidate_ml_ranking_reason")
            if best_record.get("attempt") != 1
            else "baseline remained best after learned reranking",
            "candidate_rankings": ml_candidate_rankings,
            "selected_candidate": {
                "attempt": best_record.get("attempt"),
                "candidate_id": best_record.get("candidate_id"),
                "candidate_family": best_record.get("candidate_family"),
                "ranking_reason": best_record.get("candidate_ml_ranking_reason"),
                "predicted_score": best_record.get("candidate_ml_predicted_score"),
            },
            "score_before": baseline_record.get("score"),
            "score_after": best_score,
            "improvement_amount": best_score - baseline_record.get("score", 0.0),
            "best_attempt_index": best_record.get("attempt"),
            "targets_met": _metrics_meet_targets(best_result.get("qor_metrics", {}) if best_result else {}, targets)
            and _signoff_targets_met(best_result.get("signoff", {}) if best_result else {}, allow_drc_fail, allow_lvs_fail),
        },
    }
    return best_result, summary


def _final_classification(
    mode: str,
    rtl_ok: bool,
    collateral_ok: bool,
    post_synth_verification: dict[str, Any] | None,
    openroad_result: OpenROADRunResult | None,
    env_missing: bool,
    verify_post_synth: bool,
    allow_post_synth_fail: bool,
    run_signoff: bool,
    allow_drc_fail: bool,
    allow_lvs_fail: bool,
) -> str:
    if not rtl_ok:
        return "logical_failure"
    if mode == "rtl":
        return "pass"
    if not collateral_ok:
        return "logical_failure"
    if isinstance(post_synth_verification, dict) and post_synth_verification.get("failure_kind") == "infrastructure":
        return "infra_failure"
    if verify_post_synth and not _post_synth_targets_met(post_synth_verification or {}, allow_post_synth_fail):
        return "logical_failure" if post_synth_verification and post_synth_verification.get("enabled") else "infra_failure"
    if mode == "synth":
        if openroad_result and openroad_result.get("succeeded"):
            return "pass"
        if openroad_result and openroad_result.get("failure_kind") == "infrastructure":
            return "infra_failure"
        return "infra_failure" if env_missing or openroad_result is None else "logical_failure"
    if mode in {"openroad", "full"}:
        if openroad_result and openroad_result.get("succeeded"):
            signoff = openroad_result.get("signoff", {}) if isinstance(openroad_result.get("signoff"), dict) else {}
            if run_signoff and not _signoff_targets_met(signoff, allow_drc_fail, allow_lvs_fail):
                return "partial"
            return "pass"
        if openroad_result and openroad_result.get("failure_kind") == "infrastructure":
            return "infra_failure"
        return "infra_failure" if env_missing or openroad_result is None else "logical_failure"
    return "partial"


def _compose_pipeline_report(
    spec_path: Path,
    mode: str,
    agent_cmd: list[str],
    agent_report: dict[str, Any],
    agent_stage_info: dict[str, Any],
    collateral_bundle: CollateralBundle | None,
    collateral_issues: list[FlowIssue],
    downstream_repairs: list[dict[str, Any]],
    env_messages: list[str],
    signoff_tools: dict[str, Any],
    synth_optimization: dict[str, Any] | None,
    post_synth_verification: dict[str, Any] | None,
    synthesis_stage: dict[str, Any] | None,
    openroad_result: OpenROADRunResult | None,
    qor_optimization: dict[str, Any] | None,
    compile_log_path: Path | None,
    simulation_log_path: Path | None,
    verify_post_synth: bool,
    allow_post_synth_fail: bool,
    run_signoff: bool,
    allow_drc_fail: bool,
    allow_lvs_fail: bool,
) -> dict[str, Any]:
    verification = agent_report.get("verification", {}) if isinstance(agent_report.get("verification"), dict) else {}
    artifacts = agent_report.get("artifacts", {}) if isinstance(agent_report.get("artifacts"), dict) else {}
    rtl_path = _path_from_report(artifacts.get("rtl"))
    tb_path = _path_from_report(artifacts.get("testbench"))
    rtl_ok = bool(verification.get("overall_pass"))
    collateral_ok = collateral_bundle is not None and not collateral_issues
    env_missing = bool(env_messages)
    final_classification = _final_classification(
        mode,
        rtl_ok,
        collateral_ok,
        post_synth_verification,
        openroad_result,
        env_missing,
        verify_post_synth,
        allow_post_synth_fail,
        run_signoff,
        allow_drc_fail,
        allow_lvs_fail,
    )
    qor_paths = list(collateral_bundle.generated_files) if collateral_bundle else []
    if openroad_result:
        qor_paths.extend(openroad_result.get("artifacts", []))
    qor_summary = collect_qor_summary(qor_paths)
    openroad_artifacts = _collect_openroad_artifact_groups(openroad_result)
    synthesis_run_passed = bool(openroad_result and openroad_result.get("succeeded") and mode == "synth")
    openroad_run_passed = bool(openroad_result and openroad_result.get("succeeded") and mode in {"openroad", "full"})
    if qor_optimization is None:
        qor_optimization = {
            "enabled": False,
            "attempts": [],
            "best_attempt_index": None,
            "final_selected_metrics": qor_summary,
            "final_signoff": openroad_result.get("signoff", {}) if openroad_result else {},
            "improved": False,
            "targets_met": False,
            "ml_tuning": {
                "enabled": False,
                "history_path": _relative(DEFAULT_ML_HISTORY_PATH),
                "features_used": [],
                "ranking_reason": "ML tuning disabled",
                "candidate_rankings": [],
                "selected_candidate": None,
                "score_before": None,
                "score_after": None,
                "improvement_amount": None,
                "best_attempt_index": None,
                "targets_met": False,
            },
        }
    if synth_optimization is None:
        synth_optimization = {
            "enabled": False,
            "baseline_metrics": {},
            "attempts": [],
            "best_attempt_index": None,
            "improvement_amount": None,
            "targets_met": False,
            "stop_reason": None,
            "candidate_rankings": [],
        }
    signoff_result = openroad_result.get("signoff", {}) if openroad_result and isinstance(openroad_result.get("signoff"), dict) else {}
    if post_synth_verification is None:
        post_synth_verification = _default_post_synth_summary(verify_post_synth)
    if synthesis_stage is None:
        synthesis_stage = {"status": "not_run", "failure_kind": None}
    signoff_notes = list(signoff_result.get("notes", [])) if isinstance(signoff_result.get("notes"), list) else [str(signoff_tools.get("notes") or "")]
    magic_available = bool(signoff_tools.get("magic_available"))
    netgen_available = bool(signoff_tools.get("netgen_available"))
    signoff_classification = classify_signoff_bottleneck(signoff_result) if run_signoff else {"metric_kind": "unknown"}
    return {
        "input_spec_type": agent_report.get("spec_source_type"),
        "input_spec_path": str(spec_path.relative_to(ROOT)),
        "parsed_design_class": agent_report.get("design_kind"),
        "top_module": agent_report.get("top_module"),
        "selected_candidate": agent_report.get("candidate_analysis", {}).get("selected_candidate"),
        "ambiguity_findings": agent_report.get("ambiguity_findings", []),
        "unsupported_findings": agent_report.get("unsupported_findings", []),
        "rtl_generation_status": "pass" if rtl_path and rtl_path.exists() else "fail",
        "testbench_generation_status": "pass" if tb_path and tb_path.exists() else "not_generated",
        "compile_status": "pass" if verification.get("compile_pass") else "fail",
        "simulation_status": "pass" if verification.get("functional_sim_pass") or verification.get("smoke_sim_pass") else "fail",
        "synthesis_collateral_generation_status": "pass" if collateral_ok else "fail" if collateral_bundle else "not_run",
        "openroad_execution_status": (openroad_result.get("status") if openroad_result else "not_run") if mode != "rtl" else "not_run",
        "synthesis_stage": synthesis_stage,
        "synth_optimization": synth_optimization,
        "post_synth_verification": post_synth_verification,
        "qor_summary": qor_summary,
        "qor_optimization": qor_optimization,
        "signoff": {
            "enabled": run_signoff,
            "tool_availability": {
                "magic": magic_available,
                "netgen": netgen_available,
                "magic_usable": bool(signoff_tools.get("magic_usable")),
                "netgen_usable": bool(signoff_tools.get("netgen_usable")),
            },
            "tool_paths": {
                "magic": signoff_tools.get("magic_path"),
                "netgen": signoff_tools.get("netgen_path"),
            },
            "magic_rcfile_used": signoff_result.get("magic_rcfile_used"),
            "netgen_env_used": signoff_result.get("netgen_env_used", {}),
            "retry_attempts": signoff_result.get("retry_attempts", {}),
            "drc_status": signoff_result.get("drc_status", "not_run"),
            "lvs_status": signoff_result.get("lvs_status", "not_run"),
            "drc_violation_count": signoff_result.get("drc_violation_count", 0),
            "lvs_mismatch_count": signoff_result.get("lvs_mismatch_count", 0),
            "failure_kind": signoff_result.get("failure_kind"),
            "drc_report_paths": signoff_result.get("signoff_reports", {}).get("drc_report_paths", []) if isinstance(signoff_result.get("signoff_reports"), dict) else [],
            "lvs_report_paths": signoff_result.get("signoff_reports", {}).get("lvs_report_paths", []) if isinstance(signoff_result.get("signoff_reports"), dict) else [],
            "artifact_paths": signoff_result.get("signoff_artifacts", []),
            "bottleneck_classification": signoff_classification,
            "repairs_attempted": qor_optimization.get("repairs_attempted", []),
            "targets_met": _signoff_targets_met(signoff_result, allow_drc_fail, allow_lvs_fail),
            "final_classification": signoff_result.get("status", "not_run"),
            "notes": signoff_notes,
        },
        "artifacts": {
            "generated_rtl_path": _relative(rtl_path),
            "generated_testbench_path": _relative(tb_path),
            "compile_log": _relative(compile_log_path),
            "simulation_log": _relative(simulation_log_path),
            "synthesis_openroad_logs": [_relative(openroad_result.get("log_path"))] if openroad_result and openroad_result.get("log_path") and openroad_result.get("log_path").exists() else [],
            "output_artifacts": _collect_artifacts(collateral_bundle, openroad_result) if collateral_bundle else [],
            "openroad_reports": openroad_artifacts["reports"],
            "openroad_results": openroad_artifacts["results"],
            "openroad_logs": openroad_artifacts["logs"],
            "openroad_other_artifacts": openroad_artifacts["other"],
            "qor_report_paths": qor_summary.get("source_reports", []),
        },
        "commands": {
            "agent_command": " ".join(agent_cmd),
            "openroad_command": openroad_result.get("command") if openroad_result else None,
        },
        "repair_attempts": {
            "rtl": verification.get("retry_history", []),
            "downstream": downstream_repairs,
        },
        "downstream_validation": {
            "issues": _issue_summary(collateral_issues),
            "environment_messages": env_messages,
        },
        "final_classification": final_classification,
        "final_outcome": {
            "rtl_verified": rtl_ok,
            "synthesis_collateral_generated": collateral_ok,
            "synthesis_run_passed": synthesis_run_passed,
            "openroad_run_passed": openroad_run_passed,
            "post_synth_behavior_match": _post_synth_targets_met(post_synth_verification, allow_post_synth_fail) if verify_post_synth else None,
            "signoff_passed": _signoff_targets_met(signoff_result, allow_drc_fail, allow_lvs_fail) if run_signoff else None,
            "partially_supported": final_classification == "partial",
            "unsupported": final_classification == "logical_failure",
        },
        "agent_stage": {
            "returncode": 0 if rtl_ok else 1,
            "stdout": agent_stage_info.get("stdout", ""),
            "stderr": agent_stage_info.get("stderr", ""),
            "report_path": _relative(agent_stage_info.get("report_path")),
        },
    }


def main() -> int:
    args = parse_args()
    spec_path = resolve_spec(args.spec)
    top_guess = infer_top(spec_path)

    agent_cmd = ["python", "agent.py", "--spec", str(spec_path), "--verify", "sim", "--max-passes", str(args.max_passes)]
    if args.overwrite:
        agent_cmd.append("--overwrite")
    if args.inject_fault:
        agent_cmd.extend(["--inject-fault", args.inject_fault])
    try:
        agent_report, agent_stage_info = _run_agent_stage(
            spec_path=spec_path,
            overwrite=args.overwrite,
            max_passes=args.max_passes,
            inject_fault=args.inject_fault,
        )
    except Exception as exc:
        print(f"Pipeline failed during RTL stage: {exc}", file=sys.stderr)
        return 1

    actual_top = str(agent_report.get("top_module", top_guess))
    compile_log_path, simulation_log_path = _materialize_rtl_logs(actual_top, agent_report)
    rtl_ok = bool(agent_report.get("verification", {}).get("overall_pass")) if isinstance(agent_report.get("verification"), dict) else False

    selected_id = None
    candidate_analysis = agent_report.get("candidate_analysis", {})
    if isinstance(candidate_analysis, dict):
        selected_id = candidate_analysis.get("selected_candidate")
    _, candidate = _select_candidate(spec_path, str(selected_id) if selected_id else None)
    ir = lower_document_to_ir(candidate.document)

    artifacts = agent_report.get("artifacts", {}) if isinstance(agent_report.get("artifacts"), dict) else {}
    rtl_path = _path_from_report(artifacts.get("rtl"))
    tb_path = _path_from_report(artifacts.get("testbench"))
    if rtl_path is None or not rtl_path.exists():
        print("RTL stage did not produce a valid RTL artifact.", file=sys.stderr)
        return 1

    collateral_bundle: CollateralBundle | None = None
    collateral_issues: list[FlowIssue] = []
    downstream_repairs: list[dict[str, Any]] = []
    synth_optimization: dict[str, Any] | None = None
    post_synth_verification: dict[str, Any] | None = None
    synthesis_stage: dict[str, Any] | None = None
    openroad_result: OpenROADRunResult | None = None
    qor_optimization: dict[str, Any] | None = None
    env_messages: list[str] = []
    signoff_tools = detect_signoff_tools()
    synth_opt_enabled = bool(args.optimize_synth and args.mode in {"synth", "openroad", "full"})
    post_synth_enabled = bool(args.verify_post_synth and args.mode in {"synth", "openroad", "full"})
    signoff_enabled = bool(args.run_signoff and args.mode in {"openroad", "full"})

    if rtl_ok and args.mode in {"synth", "openroad", "full"}:
        collateral_bundle = generate_collateral(ROOT, ir, rtl_path, tb_path=tb_path, injected_fault=args.inject_flow_fault)
        collateral_issues = validate_collateral(collateral_bundle, ir.name)
        flow_attempt = 1
        while collateral_issues and flow_attempt < max(1, args.max_flow_passes):
            repair = attempt_collateral_repair(ROOT, ir, rtl_path, tb_path, collateral_bundle, collateral_issues)
            downstream_repairs.append(
                {
                    "attempt": flow_attempt,
                    "action": "collateral_regeneration",
                    "issues": _issue_summary(collateral_issues),
                    "changes": repair.actions,
                    "repaired": repair.repaired,
                }
            )
            if not repair.repaired or repair.bundle is None:
                break
            collateral_bundle = repair.bundle
            collateral_issues = validate_collateral(collateral_bundle, ir.name)
            flow_attempt += 1

        env = detect_openroad_environment()
        env_messages = env.get("messages", [])
        if not collateral_issues:
            synth_stage_result: OpenROADRunResult | None = None
            if synth_opt_enabled and env.get("flow_root") is not None:
                collateral_bundle, synth_stage_result, synth_optimization = _run_synth_optimization_loop(
                    top=ir.name,
                    bundle=collateral_bundle,
                    flow_root=env.get("flow_root"),
                    rtl_path=rtl_path,
                    tb_path=tb_path,
                    targets=_build_synth_targets(args),
                    max_iters=max(1, args.synth_max_iters),
                    min_attempts=max(1, args.synth_min_attempts),
                    spec_name=spec_path.stem,
                    design_kind=str(agent_report.get("design_kind")) if agent_report.get("design_kind") is not None else None,
                )
            if post_synth_enabled and env.get("flow_root") is not None:
                collateral_bundle, synth_stage_result, post_synth_verification = _run_post_synth_verification_loop(
                    top=ir.name,
                    bundle=collateral_bundle,
                    flow_root=env.get("flow_root"),
                    rtl_path=rtl_path,
                    tb_path=tb_path,
                    ir=ir,
                    max_iters=max(1, args.max_post_synth_iters),
                )
                synthesis_stage = _build_synthesis_stage_summary(synth_stage_result)
                if args.mode == "synth":
                    openroad_result = synth_stage_result
                if args.post_synth_only:
                    openroad_result = synth_stage_result
                if post_synth_verification.get("enabled") and not _post_synth_targets_met(post_synth_verification, bool(args.post_synth_allow_fail)):
                    env_messages.append("post-synthesis behavior check did not converge before the retry limit")
            elif synth_stage_result is not None and args.mode == "synth":
                openroad_result = synth_stage_result

            openroad_mode = "synth" if args.mode == "synth" else "openroad"
            can_proceed_to_openroad = (
                not post_synth_enabled
                or _post_synth_targets_met(post_synth_verification or {}, bool(args.post_synth_allow_fail))
            ) and not args.post_synth_only
            if args.mode == "synth" and synth_stage_result is not None:
                openroad_result = synth_stage_result
                can_proceed_to_openroad = False
            if can_proceed_to_openroad:
                if signoff_enabled:
                    os.environ["SPEC2RTL_RUN_SIGNOFF"] = "1"
                else:
                    os.environ.pop("SPEC2RTL_RUN_SIGNOFF", None)
                openroad_result = run_openroad_flow(ROOT, collateral_bundle, env, openroad_mode, attempt=1)
                if openroad_result.get("attempted") and not openroad_result.get("succeeded") and args.max_flow_passes > 1:
                    flow_issues = analyze_openroad_failure(str(openroad_result.get("message", "")))
                    if flow_issues:
                        repair = attempt_collateral_repair(ROOT, ir, rtl_path, tb_path, collateral_bundle, flow_issues)
                        downstream_repairs.append(
                            {
                                "attempt": flow_attempt,
                                "action": "openroad_failure_repair",
                                "issues": _issue_summary(flow_issues),
                                "changes": repair.actions,
                                "repaired": repair.repaired,
                            }
                        )
                        if repair.repaired and repair.bundle is not None:
                            collateral_bundle = repair.bundle
                            collateral_issues = validate_collateral(collateral_bundle, ir.name)
                            if not collateral_issues:
                                openroad_result = run_openroad_flow(ROOT, collateral_bundle, env, openroad_mode, attempt=2)

            if (
                (args.optimize_qor or args.ml_tune or signoff_enabled)
                and openroad_result
                and openroad_result.get("succeeded")
                and env.get("flow_root") is not None
                and not collateral_issues
            ):
                openroad_result, qor_optimization = _run_qor_optimization_loop(
                    top=ir.name,
                    bundle=collateral_bundle,
                    mode=openroad_mode,
                    baseline_result=openroad_result,
                    targets=_build_qor_targets(args),
                    max_iters=max(1, args.qor_max_iters),
                    min_attempts=max(1, args.min_qor_attempts),
                    flow_root=env.get("flow_root"),
                    signoff_enabled=signoff_enabled,
                    max_signoff_iters=max(0, args.max_signoff_iters),
                    signoff_only=bool(args.signoff_only),
                    allow_drc_fail=bool(args.drc_allow_fail),
                    allow_lvs_fail=bool(args.lvs_allow_fail),
                    ir=ir,
                    rtl_path=rtl_path,
                    tb_path=tb_path,
                    spec_name=spec_path.stem,
                    design_kind=str(agent_report.get("design_kind")) if agent_report.get("design_kind") is not None else None,
                    ml_tune=bool(args.ml_tune),
                    persist_ml_history=bool(args.persist_ml_history),
                    post_synth_verification=post_synth_verification,
                )

    pipeline_report = _compose_pipeline_report(
        spec_path=spec_path,
        mode=args.mode,
        agent_cmd=agent_cmd,
        agent_report=agent_report,
        agent_stage_info=agent_stage_info,
        collateral_bundle=collateral_bundle,
        collateral_issues=collateral_issues,
        downstream_repairs=downstream_repairs,
        env_messages=env_messages,
        signoff_tools=signoff_tools,
        synth_optimization=synth_optimization,
        post_synth_verification=post_synth_verification,
        synthesis_stage=synthesis_stage,
        openroad_result=openroad_result,
        qor_optimization=qor_optimization,
        compile_log_path=compile_log_path,
        simulation_log_path=simulation_log_path,
        verify_post_synth=post_synth_enabled,
        allow_post_synth_fail=bool(args.post_synth_allow_fail),
        run_signoff=signoff_enabled,
        allow_drc_fail=bool(args.drc_allow_fail),
        allow_lvs_fail=bool(args.lvs_allow_fail),
    )
    pipeline_report_file = pipeline_report_path(actual_top)
    write_yaml_report(pipeline_report_file, pipeline_report)

    if agent_stage_info.get("stdout"):
        print(str(agent_stage_info["stdout"]).rstrip())
    if agent_stage_info.get("stderr"):
        print(str(agent_stage_info["stderr"]).rstrip(), file=sys.stderr)
    print(f"Pipeline report: {pipeline_report_file.relative_to(ROOT)}")

    final_classification = str(pipeline_report.get("final_classification"))
    print(f"Final classification: {final_classification}")
    if collateral_bundle:
        print(f"Collateral directory: {collateral_bundle.design_dir.relative_to(ROOT)}")
    if openroad_result and openroad_result.get("command"):
        print(f"OpenROAD command: {openroad_result.get('command')}")

    if args.strict_exit:
        return 0 if final_classification == "pass" else 1
    if final_classification in {"pass", "partial", "partially_supported", "infra_failure"}:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
