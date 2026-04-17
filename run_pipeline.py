from __future__ import annotations

import argparse
import contextlib
import io
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
from spec2rtl.flow_repair import (
    FlowIssue,
    analyze_openroad_failure,
    attempt_collateral_repair,
    validate_collateral,
)
from spec2rtl.lowering import lower_document_to_ir
from spec2rtl.openroad import OpenROADRunResult, detect_openroad_environment, run_openroad_flow
from spec2rtl.qor import collect_qor_summary
from spec2rtl.spec_ingest import load_spec_source


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
        artifacts.extend(_relative(path) for path in openroad_result.artifacts)
        if openroad_result.log_path:
            artifacts.append(_relative(openroad_result.log_path))
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
    for path in openroad_result.artifacts:
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


def _final_classification(mode: str, rtl_ok: bool, collateral_ok: bool, openroad_result: OpenROADRunResult | None, env_missing: bool) -> str:
    if not rtl_ok:
        return "unsupported"
    if mode == "rtl":
        return "RTL verified"
    if not collateral_ok:
        return "partially supported"
    if mode == "synth":
        if openroad_result and openroad_result.succeeded:
            return "synthesis run passed"
        return "partially supported" if env_missing or openroad_result is None else "unsupported"
    if mode in {"openroad", "full"}:
        if openroad_result and openroad_result.succeeded:
            return "OpenROAD run passed"
        return "partially supported" if env_missing or openroad_result is None else "unsupported"
    return "partially supported"


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
    openroad_result: OpenROADRunResult | None,
    compile_log_path: Path | None,
    simulation_log_path: Path | None,
) -> dict[str, Any]:
    verification = agent_report.get("verification", {}) if isinstance(agent_report.get("verification"), dict) else {}
    artifacts = agent_report.get("artifacts", {}) if isinstance(agent_report.get("artifacts"), dict) else {}
    rtl_path = _path_from_report(artifacts.get("rtl"))
    tb_path = _path_from_report(artifacts.get("testbench"))
    rtl_ok = bool(verification.get("overall_pass"))
    collateral_ok = collateral_bundle is not None and not collateral_issues
    env_missing = bool(env_messages)
    final_classification = _final_classification(mode, rtl_ok, collateral_ok, openroad_result, env_missing)
    qor_paths = list(collateral_bundle.generated_files) if collateral_bundle else []
    if openroad_result:
        qor_paths.extend(openroad_result.artifacts)
    qor_summary = collect_qor_summary(qor_paths)
    openroad_artifacts = _collect_openroad_artifact_groups(openroad_result)
    synthesis_run_passed = bool(openroad_result and openroad_result.succeeded and mode == "synth")
    openroad_run_passed = bool(openroad_result and openroad_result.succeeded and mode in {"openroad", "full"})
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
        "openroad_execution_status": (openroad_result.status if openroad_result else "not_run") if mode != "rtl" else "not_run",
        "qor_summary": qor_summary,
        "artifacts": {
            "generated_rtl_path": _relative(rtl_path),
            "generated_testbench_path": _relative(tb_path),
            "compile_log": _relative(compile_log_path),
            "simulation_log": _relative(simulation_log_path),
            "synthesis_openroad_logs": [_relative(openroad_result.log_path)] if openroad_result and openroad_result.log_path and openroad_result.log_path.exists() else [],
            "output_artifacts": _collect_artifacts(collateral_bundle, openroad_result) if collateral_bundle else [],
            "openroad_reports": openroad_artifacts["reports"],
            "openroad_results": openroad_artifacts["results"],
            "openroad_logs": openroad_artifacts["logs"],
            "openroad_other_artifacts": openroad_artifacts["other"],
            "qor_report_paths": qor_summary.get("source_reports", []),
        },
        "commands": {
            "agent_command": " ".join(agent_cmd),
            "openroad_command": openroad_result.command if openroad_result else None,
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
            "partially_supported": final_classification == "partially supported",
            "unsupported": final_classification == "unsupported",
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
    openroad_result: OpenROADRunResult | None = None
    env_messages: list[str] = []

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

        env = detect_openroad_environment(ROOT)
        env_messages = env.messages
        if not collateral_issues:
            openroad_mode = "synth" if args.mode == "synth" else "openroad"
            openroad_result = run_openroad_flow(ROOT, collateral_bundle, env, openroad_mode, attempt=1)
            if openroad_result.attempted and not openroad_result.succeeded and args.max_flow_passes > 1:
                flow_issues = analyze_openroad_failure(openroad_result.message)
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
        openroad_result=openroad_result,
        compile_log_path=compile_log_path,
        simulation_log_path=simulation_log_path,
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
    if openroad_result and openroad_result.command:
        print(f"OpenROAD command: {openroad_result.command}")

    if args.mode == "rtl":
        return 0 if rtl_ok else 1
    if args.mode in {"synth", "openroad", "full"}:
        if openroad_result and openroad_result.succeeded:
            return 0
        if collateral_bundle and not collateral_issues and env_messages:
            return 1
        return 0 if collateral_bundle and not collateral_issues and args.mode == "synth" and not openroad_result else 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
