from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

from run_sim import VerificationResult, verify_design
from spec2rtl.frontend import load_spec_document
from spec2rtl.ir import GeneratedTestbench, ModuleIR, RenderStrategy, RepairDecision, VerificationEvidenceIR
from spec2rtl.lowering import lower_document_to_ir
from spec2rtl.renderers import render_testbench, render_verilog


ROOT = Path(__file__).resolve().parent
RTL_DIR = ROOT / "rtl"
TB_DIR = ROOT / "tb"
REPORT_DIR = ROOT / "build" / "reports"
DEFAULT_YAML_SPEC = ROOT / "spec.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthesizable Verilog from YAML specs")
    parser.add_argument("--spec", type=Path, default=None, help="Path to a YAML spec file")
    parser.add_argument("--top", help="Override the top module name")
    parser.add_argument("--out", type=Path, help="Output RTL file path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing artifacts")
    parser.add_argument("--verify", choices=["none", "compile", "sim"], default="compile")
    parser.add_argument("--max-passes", type=int, default=3)
    return parser.parse_args()


def choose_spec_path(requested: Path | None) -> Path:
    if requested:
        path = requested if requested.is_absolute() else ROOT / requested
    else:
        path = DEFAULT_YAML_SPEC
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError(f"Only YAML specs are supported now: {path}")
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


def generation_strategies() -> list[RenderStrategy]:
    return [
        RenderStrategy(name="direct", internalize_outputs=False, include_header_comments=True),
        RenderStrategy(name="internalized", internalize_outputs=True, include_header_comments=True),
        RenderStrategy(name="minimal", internalize_outputs=True, include_header_comments=False),
    ]


def choose_next_strategy(result: VerificationResult, used: set[str], max_passes: int) -> tuple[RenderStrategy | None, str]:
    if len(used) >= max_passes:
        return None, "retry budget exhausted"
    message = f"{result.stdout}\n{result.stderr}\n{result.message}".lower()
    ordered = generation_strategies()
    if any(token in message for token in ["not a valid l-value", "cannot be driven", "reg", "wire"]):
        ordered = [ordered[1], ordered[2], ordered[0]]
        reason = "compile diagnostics suggested output reg/wire mismatch"
    elif any(token in message for token in ["syntax error", "invalid module item", "malformed"]):
        ordered = [ordered[2], ordered[1], ordered[0]]
        reason = "compile diagnostics suggested falling back to a minimal renderer"
    else:
        reason = "moving to the next render strategy after failed verification"
    for strategy in ordered:
        if strategy.name not in used:
            return strategy, reason
    return None, "no unused render strategy remained"


def apply_feedback(ir: ModuleIR, result: VerificationResult, attempt: int) -> tuple[ModuleIR, str]:
    next_ir = copy.deepcopy(ir)
    message = f"{result.stdout}\n{result.stderr}\n{result.message}".lower()
    if "unable to bind wire/reg/memory" in message and next_ir.design_kind == "fsm":
        next_ir.verification.requested_level = "smoke"
        reason = "simulation elaboration could not support deep FSM introspection; downgraded verification goal to smoke"
    elif "no independent oracle available" in message:
        next_ir.verification.requested_level = "smoke"
        reason = "verification oracle was unsupported; downgraded verification goal to smoke"
    else:
        reason = "kept semantic IR unchanged; feedback only influenced rendering strategy"
    next_ir.repairs.append(RepairDecision(attempt=attempt, action="feedback_adjustment", reason=reason))
    return next_ir, reason


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
    ir: ModuleIR,
    rtl_path: Path,
    tb_path: Path | None,
    requested_mode: str,
    compile_result: VerificationResult | None,
    sim_result: VerificationResult | None,
    evidence: VerificationEvidenceIR,
) -> dict[str, object]:
    compile_pass = bool(compile_result and compile_result.succeeded)
    smoke_sim_pass, functional_sim_pass = final_verification_classification(requested_mode, compile_result, sim_result, evidence)
    if functional_sim_pass:
        support_status = "supported"
    elif smoke_sim_pass or compile_pass:
        support_status = "partially_supported"
    else:
        support_status = "unsupported"
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

    return {
        "spec_source": str(spec_path.relative_to(ROOT)),
        "top_module": ir.name,
        "design_kind": ir.design_kind,
        "artifacts": {
            "rtl": str(rtl_path.relative_to(ROOT)),
            "testbench": str(tb_path.relative_to(ROOT)) if tb_path and tb_path.exists() else None,
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


def main() -> int:
    args = parse_args()
    spec_path = choose_spec_path(args.spec)
    document = load_spec_document(spec_path, top_override=args.top)
    ir = lower_document_to_ir(document)

    RTL_DIR.mkdir(exist_ok=True)
    TB_DIR.mkdir(exist_ok=True)
    rtl_path = output_path(ir.name, args.out)
    tb_path = testbench_path(ir.name)
    ensure_writable(rtl_path, args.overwrite)
    if args.verify == "sim":
        ensure_writable(tb_path, args.overwrite)

    final_result: VerificationResult | None = None
    compile_result: VerificationResult | None = None
    sim_result: VerificationResult | None = None
    tb_artifact = GeneratedTestbench(text=None, evidence=VerificationEvidenceIR(tb_kind="none", achieved_level="none"))
    used: set[str] = set()
    strategy = generation_strategies()[0]
    attempt_no = 1

    while strategy and attempt_no <= max(1, args.max_passes):
        used.add(strategy.name)
        rtl_text = render_verilog(ir, strategy)
        tb_artifact = render_testbench(ir) if args.verify == "sim" or ir.verification.enable_tb else tb_artifact
        write_artifacts(rtl_path, tb_path if tb_artifact.text else None, rtl_text, tb_artifact)

        if args.verify == "none":
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
            break

        compile_result = verify_design("compile", rtl_path=rtl_path, tb_path=None, top_name=ir.name, attempt=attempt_no)
        final_result = compile_result
        if not compile_result.succeeded:
            ir, reason = apply_feedback(ir, compile_result, attempt_no)
            next_strategy, strategy_reason = choose_next_strategy(compile_result, used, args.max_passes)
            ir.repairs.append(RepairDecision(attempt=attempt_no, action="retry_strategy", reason=f"{reason}; {strategy_reason}"))
            strategy = next_strategy
            attempt_no += 1
            continue

        if args.verify == "compile":
            break

        sim_result = verify_design("sim", rtl_path=rtl_path, tb_path=tb_path if tb_artifact.text else None, top_name=ir.name, attempt=attempt_no)
        final_result = sim_result
        if sim_result.succeeded:
            break

        ir, reason = apply_feedback(ir, sim_result, attempt_no)
        next_strategy, strategy_reason = choose_next_strategy(sim_result, used, args.max_passes)
        ir.repairs.append(RepairDecision(attempt=attempt_no, action="retry_strategy", reason=f"{reason}; {strategy_reason}"))
        strategy = next_strategy
        attempt_no += 1

    if final_result is None:
        print("Generation did not produce a result.")
        return 2

    print(f"Spec source: {spec_path.relative_to(ROOT)}")
    print(f"Generated RTL: {rtl_path.relative_to(ROOT)}")
    if (args.verify == "sim" or ir.verification.enable_tb) and tb_artifact.text and tb_path.exists():
        print(f"Generated testbench: {tb_path.relative_to(ROOT)}")
    print(f"Top module: {ir.name}")
    print(f"Design kind: {ir.design_kind}")
    print(f"Verification: {summarize_result(final_result)}")
    print("Ports:")
    for port in ir.ports:
        suffix = f"[{port.width - 1}:0] " if port.width > 1 else ""
        print(f"  - {port.direction} {suffix}{port.name}")

    report = build_report(
        spec_path=spec_path,
        ir=ir,
        rtl_path=rtl_path,
        tb_path=tb_path if tb_artifact.text and tb_path.exists() else None,
        requested_mode=args.verify,
        compile_result=compile_result,
        sim_result=sim_result,
        evidence=tb_artifact.evidence,
    )
    out_report = report_path(ir.name)
    write_yaml_report(out_report, report)
    print(f"Verification report: {out_report.relative_to(ROOT)}")

    return 0 if final_result.succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
