from __future__ import annotations

import argparse
import sys
from pathlib import Path

from run_sim import VerificationResult, verify_design
from spec2rtl.candidate_ranking import classify_final_verdict, score_candidate
from spec2rtl.feedback import (
    AttemptRecord,
    analyze_and_repair,
    build_attempt_record,
    generation_strategies,
    seed_fault_injection,
    write_attempt_snapshot,
)
from spec2rtl.ir import GeneratedTestbench, ModuleIR, NormalizedCandidateIR, SpecParseResultIR, VerificationEvidenceIR
from spec2rtl.lowering import lower_document_to_ir
from spec2rtl.renderers import render_testbench, render_verilog
from spec2rtl.spec_ingest import load_spec_source


ROOT = Path(__file__).resolve().parent
RTL_DIR = ROOT / "rtl"
TB_DIR = ROOT / "tb"
REPORT_DIR = ROOT / "build" / "reports"
DEFAULT_SPEC = ROOT / "spec.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthesizable Verilog from YAML specs")
    parser.add_argument("--spec", type=Path, default=None, help="Path to a YAML spec file")
    parser.add_argument("--top", help="Override the top module name")
    parser.add_argument("--out", type=Path, help="Output RTL file path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing artifacts")
    parser.add_argument("--verify", choices=["none", "compile", "sim"], default="compile")
    parser.add_argument("--max-passes", type=int, default=3)
    parser.add_argument(
        "--inject-fault",
        type=str,
        default=None,
        help="Inject a first-pass RTL bug, for example counter_hold_when_enabled, register_hold_when_enabled, shift_reverse_direction, fsm_force_self_loop, or zero_output:<target>",
    )
    return parser.parse_args()


def choose_spec_path(requested: Path | None) -> Path:
    if requested:
        path = requested if requested.is_absolute() else ROOT / requested
    else:
        path = DEFAULT_SPEC
    return path


def output_path(top: str, requested: Path | None) -> Path:
    if requested:
        return requested if requested.is_absolute() else ROOT / requested
    return RTL_DIR / f"{top}.v"


def testbench_path(top: str) -> Path:
    return TB_DIR / f"tb_{top}.sv"


def report_path(top: str) -> Path:
    return REPORT_DIR / f"{top}_report.yaml"


def ensure_writable(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")


def write_artifacts(rtl_path: Path, tb_path: Path | None, rtl_text: str, tb: GeneratedTestbench) -> None:
    rtl_path.parent.mkdir(exist_ok=True)
    rtl_path.write_text(rtl_text, encoding="utf-8")
    if tb_path and tb.text:
        tb_path.parent.mkdir(exist_ok=True)
        tb_path.write_text(tb.text, encoding="utf-8")


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if text == "" or any(ch in text for ch in [":", "#", "{", "}", "[", "]"]) or text.strip() != text:
        return f'"{text}"'
    return text


def is_block_scalar_candidate(value: object) -> bool:
    return isinstance(value, str) and "\n" in value


def render_yaml_report(report: dict[str, object], indent: int = 0) -> list[str]:
    lines: list[str] = []
    pad = " " * indent
    for key, value in report.items():
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.extend(render_yaml_report(value, indent + 2))
        elif isinstance(value, list):
            lines.append(f"{pad}{key}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(f"{pad}  -")
                    lines.extend(render_yaml_report(item, indent + 4))
                else:
                    lines.append(f"{pad}  - {yaml_scalar(item)}")
        elif is_block_scalar_candidate(value):
            lines.append(f"{pad}{key}: |-")
            for entry in str(value).splitlines():
                lines.append(f"{pad}  {entry}")
        else:
            lines.append(f"{pad}{key}: {yaml_scalar(value)}")
    return lines


def final_verification_classification(
    requested_mode: str,
    compile_result: VerificationResult | None,
    sim_result: VerificationResult | None,
    evidence: VerificationEvidenceIR,
) -> tuple[bool, bool]:
    if requested_mode != "sim" or not sim_result or not sim_result.succeeded:
        return False, False
    if evidence.achieved_level == "functional" and evidence.oracle_independent:
        return False, True
    if evidence.achieved_level == "smoke":
        return True, False
    return False, False


def build_report(
    spec_path: Path,
    parse_result: SpecParseResultIR,
    candidate: NormalizedCandidateIR,
    ir: ModuleIR,
    rtl_path: Path,
    tb_path: Path | None,
    injected_fault: str | None,
    max_attempts: int,
    requested_mode: str,
    compile_result: VerificationResult | None,
    sim_result: VerificationResult | None,
    evidence: VerificationEvidenceIR,
    attempts: list[AttemptRecord],
    candidate_summaries: list[dict[str, object]],
    final_classification: str,
) -> dict[str, object]:
    compile_pass = bool(compile_result and compile_result.succeeded)
    smoke_sim_pass, functional_sim_pass = final_verification_classification(requested_mode, compile_result, sim_result, evidence)
    support_status = (
        "supported"
        if final_classification == "functionally_verified"
        else "partially_supported" if final_classification == "compile_and_smoke_verified" or compile_pass or smoke_sim_pass else "unsupported"
    )
    if requested_mode == "none":
        conclusion = "generation only; verification was not requested"
    elif functional_sim_pass:
        conclusion = "functional verification passed with independent evidence"
    elif smoke_sim_pass:
        conclusion = "simulation passed, but only smoke-level evidence is available"
    elif compile_pass and requested_mode == "compile":
        conclusion = "compile-only verification passed"
    else:
        conclusion = "verification failed"
    partial_reasons = []
    if requested_mode == "sim" and not functional_sim_pass:
        partial_reasons.extend(evidence.limitations)
        if sim_result and sim_result.succeeded and evidence.achieved_level != "functional":
            partial_reasons.append("simulation did not meet the requested functional evidence threshold")
    repaired_after_feedback = bool((compile_pass or functional_sim_pass or smoke_sim_pass) and len(attempts) > 1)
    unrepaired_after_retry_limit = bool(attempts and len(attempts) >= max_attempts and not (functional_sim_pass or smoke_sim_pass or (requested_mode == "compile" and compile_pass)))

    return {
        "spec_source_type": parse_result.source_type,
        "spec_source": str(spec_path.relative_to(ROOT)),
        "top_module": ir.name,
        "design_kind": ir.design_kind,
        "final_classification": final_classification,
        "ambiguity_findings": [
            {
                "code": item.code,
                "severity": item.severity,
                "message": item.message,
                "inferred_value": item.inferred_value,
            }
            for item in candidate.ambiguities
        ],
        "unsupported_findings": list(candidate.unsupported),
        "extracted_semantics": candidate.extracted_semantics,
        "candidate_analysis": {
            "candidate_count": len(candidate_summaries),
            "selected_candidate": candidate.candidate_id,
            "candidates": candidate_summaries,
        },
        "artifacts": {
            "rtl": str(rtl_path.relative_to(ROOT)),
            "testbench": str(tb_path.relative_to(ROOT)) if tb_path and tb_path.exists() else None,
        },
        "repair_loop": {
            "enabled": requested_mode != "none",
            "max_attempts": max_attempts,
            "attempts_used": len(attempts),
            "injected_fault": injected_fault,
            "repaired_after_feedback": repaired_after_feedback,
            "unrepaired_after_retry_limit": unrepaired_after_retry_limit,
            "attempts":
                [
                    {
                        "attempt": item.attempt,
                        "strategy": item.strategy,
                        "rtl_file": item.rtl_snapshot,
                        "testbench_file": item.tb_snapshot,
                        "compile_command": item.compile_command,
                        "simulation_command": item.simulation_command,
                        "compile_status": item.compile_status,
                        "simulation_status": item.simulation_status,
                        "compile_stdout": item.compile_stdout,
                        "compile_stderr": item.compile_stderr,
                        "simulation_stdout": item.simulation_stdout,
                        "simulation_stderr": item.simulation_stderr,
                        "diagnosis_summary": item.diagnosis_summary,
                        "next_regeneration_changes": item.next_change_summary,
                    }
                    for item in attempts
                ],
        },
        "verification": {
            "support_status": support_status,
            "requested_mode": requested_mode,
            "requested_level": ir.verification.requested_level if requested_mode == "sim" else None,
            "generated_testbench_kind": evidence.tb_kind,
            "oracle_independent": evidence.oracle_independent,
            "compile_pass": compile_pass,
            "smoke_sim_pass": smoke_sim_pass,
            "functional_sim_pass": functional_sim_pass,
            "overall_pass": functional_sim_pass or smoke_sim_pass or (requested_mode == "compile" and compile_pass),
            "covered_checks": evidence.covered_checks,
            "limitations": evidence.limitations,
            "notes": evidence.notes,
            "partial_verification_reasons": partial_reasons,
            "assumptions": candidate.assumptions,
            "conclusion": conclusion,
            "compile": {
                "attempt": compile_result.attempt if compile_result else None,
                "ok": compile_pass,
                "message": compile_result.message if compile_result else None,
                "command": compile_result.command if compile_result else None,
            },
            "simulation": {
                "attempt": sim_result.attempt if sim_result else None,
                "ok": bool(sim_result and sim_result.succeeded),
                "message": sim_result.message if sim_result else None,
                "command": sim_result.command if sim_result else None,
            },
            "retry_history": [
                {"attempt": item.attempt, "action": item.action, "reason": item.reason}
                for item in ir.repairs
            ],
        },
    }


def write_yaml_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(render_yaml_report(report)) + "\n", encoding="utf-8")


def summarize_result(result: VerificationResult) -> str:
    parts = [f"stage={result.mode}", f"ok={result.succeeded}", f"attempt={result.attempt}"]
    if result.command:
        parts.append(f"command={result.command}")
    if result.message:
        parts.append(f"message={result.message}")
    return ", ".join(parts)


def candidate_rtl_path(top: str, candidate_id: str) -> Path:
    return ROOT / "build" / "candidates" / top / candidate_id / f"{top}.v"


def candidate_tb_path(top: str, candidate_id: str) -> Path:
    return ROOT / "build" / "candidates" / top / candidate_id / f"tb_{top}.sv"


def run_repair_loop(
    ir: ModuleIR,
    verify_mode: str,
    max_passes: int,
    candidate_id: str,
    injected_fault: str | None,
) -> dict[str, object]:
    ir, injected_changes = seed_fault_injection(ir, injected_fault)
    if injected_changes:
        for change in injected_changes:
            ir.notes.append(f"Repair demo setup: {change}")

    rtl_path = candidate_rtl_path(ir.name, candidate_id)
    tb_path = candidate_tb_path(ir.name, candidate_id)
    rtl_path.parent.mkdir(parents=True, exist_ok=True)

    final_result: VerificationResult | None = None
    compile_result: VerificationResult | None = None
    sim_result: VerificationResult | None = None
    tb_artifact = GeneratedTestbench(text=None, evidence=VerificationEvidenceIR(tb_kind="none", achieved_level="none"))
    used: set[str] = set()
    strategy = generation_strategies()[0]
    attempt_no = 1
    attempt_records: list[AttemptRecord] = []
    final_rtl_text = ""

    while strategy and attempt_no <= max(1, max_passes):
        used.add(strategy.name)
        sim_result = None
        rtl_text = render_verilog(ir, strategy)
        final_rtl_text = rtl_text
        tb_artifact = render_testbench(ir) if verify_mode == "sim" or ir.verification.enable_tb else tb_artifact
        write_artifacts(rtl_path, tb_path if tb_artifact.text else None, rtl_text, tb_artifact)
        rtl_snapshot, tb_snapshot = write_attempt_snapshot(ROOT, ir.name, attempt_no, rtl_text, tb_artifact.text, candidate_id=candidate_id)

        if verify_mode == "none":
            final_result = VerificationResult(
                mode="none",
                succeeded=True,
                returncode=0,
                command="",
                stdout="",
                stderr="",
                message="Generation completed without verification",
                attempt=attempt_no,
            )
            attempt_records.append(
                build_attempt_record(
                    attempt=attempt_no,
                    strategy=strategy,
                    rtl_snapshot=rtl_snapshot,
                    tb_snapshot=tb_snapshot,
                    compile_result=final_result,
                    sim_result=None,
                    diagnosis_summary="verification was disabled for this run",
                    next_change_summary=[],
                )
            )
            break

        compile_result = verify_design("compile", rtl_path=rtl_path, tb_path=None, top_name=ir.name, attempt=attempt_no)
        final_result = compile_result
        if not compile_result.succeeded:
            repair = analyze_and_repair(ir, compile_result, None, strategy, used, max_passes, attempt_no)
            attempt_records.append(
                build_attempt_record(
                    attempt=attempt_no,
                    strategy=strategy,
                    rtl_snapshot=rtl_snapshot,
                    tb_snapshot=tb_snapshot,
                    compile_result=compile_result,
                    sim_result=None,
                    diagnosis_summary=repair.diagnosis_summary,
                    next_change_summary=repair.next_change_summary,
                )
            )
            ir = repair.ir
            strategy = repair.strategy
            attempt_no += 1
            continue

        if verify_mode == "compile":
            attempt_records.append(
                build_attempt_record(
                    attempt=attempt_no,
                    strategy=strategy,
                    rtl_snapshot=rtl_snapshot,
                    tb_snapshot=tb_snapshot,
                    compile_result=compile_result,
                    sim_result=None,
                    diagnosis_summary="compile passed; no further repair required",
                    next_change_summary=[],
                )
            )
            break

        sim_result = verify_design("sim", rtl_path=rtl_path, tb_path=tb_path if tb_artifact.text else None, top_name=ir.name, attempt=attempt_no)
        final_result = sim_result
        if sim_result.succeeded:
            diagnosis = "simulation passed on the current RTL/testbench pair"
            if attempt_no > 1:
                diagnosis = "simulation passed after applying prior repair feedback"
            attempt_records.append(
                build_attempt_record(
                    attempt=attempt_no,
                    strategy=strategy,
                    rtl_snapshot=rtl_snapshot,
                    tb_snapshot=tb_snapshot,
                    compile_result=compile_result,
                    sim_result=sim_result,
                    diagnosis_summary=diagnosis,
                    next_change_summary=[],
                )
            )
            break

        repair = analyze_and_repair(ir, compile_result, sim_result, strategy, used, max_passes, attempt_no)
        attempt_records.append(
            build_attempt_record(
                attempt=attempt_no,
                strategy=strategy,
                rtl_snapshot=rtl_snapshot,
                tb_snapshot=tb_snapshot,
                compile_result=compile_result,
                sim_result=sim_result,
                diagnosis_summary=repair.diagnosis_summary,
                next_change_summary=repair.next_change_summary,
            )
        )
        ir = repair.ir
        strategy = repair.strategy
        attempt_no += 1

    return {
        "ir": ir,
        "rtl_path": rtl_path,
        "tb_path": tb_path if tb_artifact.text and tb_path.exists() else None,
        "rtl_text": final_rtl_text,
        "tb_artifact": tb_artifact,
        "final_result": final_result,
        "compile_result": compile_result,
        "sim_result": sim_result,
        "attempts": attempt_records,
    }


def candidate_summary(
    candidate: NormalizedCandidateIR,
    result: dict[str, object],
) -> dict[str, object]:
    compile_result = result["compile_result"]
    sim_result = result["sim_result"]
    evidence = result["tb_artifact"].evidence
    compile_ok = bool(compile_result and compile_result.succeeded)
    sim_ok = bool(sim_result and sim_result.succeeded)
    score = score_candidate(
        internal_score=candidate.internal_score,
        compile_ok=compile_ok,
        sim_ok=sim_ok,
        evidence=evidence,
        ambiguity_count=len(candidate.ambiguities),
        unsupported_count=len(candidate.unsupported),
        attempts_used=len(result["attempts"]),
    )
    classification = classify_final_verdict(
        compile_ok=compile_ok,
        sim_ok=sim_ok,
        evidence=evidence,
        ambiguity_count=len(candidate.ambiguities),
        unsupported_count=len(candidate.unsupported),
    )
    return {
        "candidate_id": candidate.candidate_id,
        "title": candidate.title,
        "score": score,
        "classification": classification,
        "assumptions": candidate.assumptions,
        "ambiguity_count": len(candidate.ambiguities),
        "unsupported_count": len(candidate.unsupported),
        "internal_checks": candidate.internal_checks,
        "compile_ok": compile_ok,
        "simulation_ok": sim_ok,
        "evidence_level": evidence.achieved_level,
        "oracle_independent": evidence.oracle_independent,
        "attempts_used": len(result["attempts"]),
        "extracted_semantics": candidate.extracted_semantics,
    }


def main() -> int:
    args = parse_args()
    spec_path = choose_spec_path(args.spec)
    parse_result = load_spec_source(spec_path, top_override=args.top)
    if not parse_result.candidates:
        print("No semantic candidates could be extracted from the specification.")
        return 2

    candidate_results: list[tuple[NormalizedCandidateIR, dict[str, object], dict[str, object]]] = []
    for candidate in parse_result.candidates:
        ir = lower_document_to_ir(candidate.document)
        candidate_result = run_repair_loop(ir, args.verify, max(1, args.max_passes), candidate.candidate_id, args.inject_fault)
        summary = candidate_summary(candidate, candidate_result)
        candidate_results.append((candidate, candidate_result, summary))

    candidate_results.sort(key=lambda item: item[2]["score"], reverse=True)
    selected_candidate, selected_result, selected_summary = candidate_results[0]
    final_result = selected_result["final_result"]
    if final_result is None:
        print("Generation did not produce a result.")
        return 2

    selected_ir: ModuleIR = selected_result["ir"]
    selected_tb_artifact: GeneratedTestbench = selected_result["tb_artifact"]
    compile_result: VerificationResult | None = selected_result["compile_result"]
    sim_result: VerificationResult | None = selected_result["sim_result"]
    attempt_records: list[AttemptRecord] = selected_result["attempts"]

    RTL_DIR.mkdir(exist_ok=True)
    TB_DIR.mkdir(exist_ok=True)
    rtl_path = output_path(selected_ir.name, args.out)
    tb_path = testbench_path(selected_ir.name)
    ensure_writable(rtl_path, args.overwrite)
    if args.verify == "sim":
        ensure_writable(tb_path, args.overwrite)
    write_artifacts(rtl_path, tb_path if selected_tb_artifact.text else None, selected_result["rtl_text"], selected_tb_artifact)

    print(f"Spec source: {spec_path.relative_to(ROOT)}")
    print(f"Spec source type: {parse_result.source_type}")
    print(f"Candidates evaluated: {len(candidate_results)}")
    print(f"Selected candidate: {selected_candidate.candidate_id} ({selected_candidate.title})")
    print(f"Generated RTL: {rtl_path.relative_to(ROOT)}")
    if (args.verify == "sim" or selected_ir.verification.enable_tb) and selected_tb_artifact.text and tb_path.exists():
        print(f"Generated testbench: {tb_path.relative_to(ROOT)}")
    print(f"Top module: {selected_ir.name}")
    print(f"Design kind: {selected_ir.design_kind}")
    print(f"Verification: {summarize_result(final_result)}")
    print("Ports:")
    for port in selected_ir.ports:
        suffix = f"[{port.width - 1}:0] " if port.width > 1 else ""
        print(f"  - {port.direction} {suffix}{port.name}")

    report = build_report(
        spec_path=spec_path,
        parse_result=parse_result,
        candidate=selected_candidate,
        ir=selected_ir,
        rtl_path=rtl_path,
        tb_path=tb_path if selected_tb_artifact.text and tb_path.exists() else None,
        injected_fault=args.inject_fault,
        max_attempts=max(1, args.max_passes),
        requested_mode=args.verify,
        compile_result=compile_result,
        sim_result=sim_result,
        evidence=selected_tb_artifact.evidence,
        attempts=attempt_records,
        candidate_summaries=[item[2] for item in candidate_results],
        final_classification=selected_summary["classification"],
    )
    out_report = report_path(selected_ir.name)
    write_yaml_report(out_report, report)
    print(f"Verification report: {out_report.relative_to(ROOT)}")

    return 0 if final_result.succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
