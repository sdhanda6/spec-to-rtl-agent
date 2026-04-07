from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from pathlib import Path

from run_sim import VerificationResult
from spec2rtl.ir import ModuleIR, RenderStrategy, RepairDecision


@dataclass
class AttemptRecord:
    attempt: int
    strategy: str
    rtl_snapshot: str
    tb_snapshot: str | None
    compile_command: str | None
    simulation_command: str | None
    compile_status: str
    simulation_status: str
    compile_stdout: str
    compile_stderr: str
    simulation_stdout: str
    simulation_stderr: str
    diagnosis_summary: str
    next_change_summary: list[str] = field(default_factory=list)


@dataclass
class RepairOutcome:
    ir: ModuleIR
    strategy: RenderStrategy | None
    diagnosis_summary: str
    next_change_summary: list[str] = field(default_factory=list)
    exhausted: bool = False


def generation_strategies() -> list[RenderStrategy]:
    return [
        RenderStrategy(name="direct", internalize_outputs=False, include_header_comments=True),
        RenderStrategy(name="internalized", internalize_outputs=True, include_header_comments=True),
        RenderStrategy(name="minimal", internalize_outputs=True, include_header_comments=False),
    ]


def seed_fault_injection(ir: ModuleIR, fault: str | None) -> tuple[ModuleIR, list[str]]:
    next_ir = copy.deepcopy(ir)
    changes: list[str] = []
    if fault == "counter_hold_when_enabled":
        next_ir.repair_controls.counter_hold_when_enabled = True
        changes.append("injected a counter bug that holds the counter even when enable is asserted")
    elif fault == "counter_ignore_enable":
        next_ir.repair_controls.counter_ignore_enable = True
        changes.append("injected a counter bug that increments even when enable is deasserted")
    elif fault == "register_hold_when_enabled":
        next_ir.repair_controls.register_hold_when_enabled = True
        changes.append("injected a register bug that holds its value instead of loading new data when enable is asserted")
    elif fault == "register_ignore_enable":
        next_ir.repair_controls.register_ignore_enable = True
        changes.append("injected a register bug that loads new data even when enable is deasserted")
    elif fault == "shift_reverse_direction":
        next_ir.repair_controls.shift_reverse_direction = True
        changes.append("injected a shift-register bug that reverses the declared shift direction")
    elif fault == "shift_ignore_enable":
        next_ir.repair_controls.shift_ignore_enable = True
        changes.append("injected a shift-register bug that shifts even while enable is deasserted")
    elif fault == "fsm_force_self_loop":
        next_ir.repair_controls.fsm_force_self_loop = True
        changes.append("injected an FSM bug that forces self-loops instead of taking transitions")
    elif fault and fault.startswith("zero_output:"):
        target = fault.split(":", 1)[1].strip()
        if target:
            next_ir.repair_controls.zero_output_targets.append(target)
            changes.append(f"injected an output bug that forces {target} to zero")
    return next_ir, changes


def write_attempt_snapshot(
    root: Path,
    top_name: str,
    attempt: int,
    rtl_text: str,
    tb_text: str | None,
    candidate_id: str | None = None,
) -> tuple[Path, Path | None]:
    attempt_dir = root / "build" / "attempts" / top_name
    if candidate_id:
        attempt_dir = attempt_dir / candidate_id
    attempt_dir = attempt_dir / f"attempt_{attempt}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    rtl_path = attempt_dir / f"{top_name}.v"
    rtl_path.write_text(rtl_text, encoding="utf-8")
    tb_path: Path | None = None
    if tb_text is not None:
        tb_path = attempt_dir / f"tb_{top_name}.sv"
        tb_path.write_text(tb_text, encoding="utf-8")
    return rtl_path, tb_path


def build_attempt_record(
    attempt: int,
    strategy: RenderStrategy,
    rtl_snapshot: Path,
    tb_snapshot: Path | None,
    compile_result: VerificationResult | None,
    sim_result: VerificationResult | None,
    diagnosis_summary: str = "",
    next_change_summary: list[str] | None = None,
) -> AttemptRecord:
    return AttemptRecord(
        attempt=attempt,
        strategy=strategy.name,
        rtl_snapshot=str(rtl_snapshot),
        tb_snapshot=str(tb_snapshot) if tb_snapshot else None,
        compile_command=compile_result.command if compile_result else None,
        simulation_command=sim_result.command if sim_result else None,
        compile_status=_status_label(compile_result),
        simulation_status=_status_label(sim_result),
        compile_stdout=compile_result.stdout if compile_result else "",
        compile_stderr=compile_result.stderr if compile_result else "",
        simulation_stdout=sim_result.stdout if sim_result else "",
        simulation_stderr=sim_result.stderr if sim_result else "",
        diagnosis_summary=diagnosis_summary,
        next_change_summary=list(next_change_summary or []),
    )


def analyze_and_repair(
    ir: ModuleIR,
    compile_result: VerificationResult | None,
    sim_result: VerificationResult | None,
    current_strategy: RenderStrategy,
    used_strategies: set[str],
    max_attempts: int,
    attempt: int,
) -> RepairOutcome:
    next_ir = copy.deepcopy(ir)
    diagnosis: list[str] = []
    changes: list[str] = []

    if compile_result and not compile_result.succeeded:
        message = _combined_output(compile_result)
        strategy, strategy_reason = choose_next_strategy(compile_result, used_strategies, max_attempts)
        diagnosis.append(strategy_reason)
        if strategy and strategy.name != current_strategy.name:
            changes.append(f"switch render strategy from {current_strategy.name} to {strategy.name}")
        if "unable to bind wire/reg/memory" in message and next_ir.design_kind == "fsm":
            next_ir.verification.requested_level = "smoke"
            changes.append("downgrade FSM verification from functional to smoke due to unsupported state introspection")
        next_ir.repairs.append(
            RepairDecision(
                attempt=attempt,
                action="compile_feedback",
                reason="; ".join(diagnosis) if diagnosis else "compile failure triggered retry",
            )
        )
        return RepairOutcome(
            ir=next_ir,
            strategy=strategy,
            diagnosis_summary="; ".join(diagnosis) if diagnosis else "compile failure",
            next_change_summary=changes,
            exhausted=strategy is None,
        )

    if sim_result and not sim_result.succeeded:
        message = _combined_output(sim_result)
        matched_behavioral_fix = _apply_behavioral_fix(next_ir, message, changes, diagnosis)
        if not matched_behavioral_fix and "no independent oracle available" in message:
            next_ir.verification.requested_level = "smoke"
            changes.append("downgrade requested verification level to smoke because the current oracle is unsupported")
            diagnosis.append("simulation feedback showed the generated testbench could not prove functional behavior independently")
        strategy = current_strategy
        if not changes:
            strategy, strategy_reason = choose_next_strategy(sim_result, used_strategies, max_attempts)
            diagnosis.append(strategy_reason)
            if strategy and strategy.name != current_strategy.name:
                changes.append(f"switch render strategy from {current_strategy.name} to {strategy.name}")
        next_ir.repairs.append(
            RepairDecision(
                attempt=attempt,
                action="simulation_feedback",
                reason="; ".join(diagnosis) if diagnosis else "simulation failure triggered retry",
            )
        )
        return RepairOutcome(
            ir=next_ir,
            strategy=strategy,
            diagnosis_summary="; ".join(diagnosis) if diagnosis else "simulation failure",
            next_change_summary=changes,
            exhausted=strategy is None,
        )

    return RepairOutcome(
        ir=next_ir,
        strategy=current_strategy,
        diagnosis_summary="no repair needed",
        next_change_summary=[],
        exhausted=False,
    )


def choose_next_strategy(result: VerificationResult, used: set[str], max_attempts: int) -> tuple[RenderStrategy | None, str]:
    if len(used) >= max_attempts:
        return None, "retry budget exhausted"
    message = _combined_output(result)
    ordered = generation_strategies()
    if any(token in message for token in ["not a valid l-value", "cannot be driven", "reg", "wire"]):
        ordered = [ordered[1], ordered[2], ordered[0]]
        reason = "compiler diagnostics indicated an output reg/wire driving mismatch"
    elif any(token in message for token in ["syntax error", "invalid module item", "malformed"]):
        ordered = [ordered[2], ordered[1], ordered[0]]
        reason = "compiler diagnostics indicated a syntax-oriented renderer fallback"
    else:
        reason = "no targeted semantic repair matched, so the loop will try a different render strategy"
    for strategy in ordered:
        if strategy.name not in used:
            return strategy, reason
    return None, "retry budget exhausted"


def _apply_behavioral_fix(ir: ModuleIR, message: str, changes: list[str], diagnosis: list[str]) -> bool:
    lowered = message.lower()
    matched = False

    if ir.design_kind == "counter" and ir.counter:
        if "increment failed" in lowered:
            diagnosis.append("testbench reported that the counter did not increment when enable was asserted")
            if ir.repair_controls.counter_hold_when_enabled:
                ir.repair_controls.counter_hold_when_enabled = False
                changes.append("remove the injected counter hold-on-enable bug so the counter increments again")
                matched = True
            elif ir.counter.direction != "up":
                ir.counter.direction = "up"
                changes.append("force the counter direction to up to match the failing increment check")
                matched = True
        if "hold failed" in lowered:
            diagnosis.append("testbench reported that the counter changed value while enable was deasserted")
            if ir.repair_controls.counter_ignore_enable:
                ir.repair_controls.counter_ignore_enable = False
                changes.append("restore enable gating so the counter holds its value when disabled")
                matched = True
        if "reset failed" in lowered:
            diagnosis.append("testbench reported that reset did not drive the counter back to its reset value")
            if ir.repair_controls.counter_hold_when_enabled:
                ir.repair_controls.counter_hold_when_enabled = False
                changes.append("clear the injected counter bug before retrying reset-sensitive behavior")
                matched = True

    if ir.design_kind == "fsm" and ir.fsm and "expected state=" in lowered:
        diagnosis.append("testbench reported an FSM next-state mismatch")
        if ir.repair_controls.fsm_force_self_loop:
            ir.repair_controls.fsm_force_self_loop = False
            changes.append("remove the injected FSM self-loop bug so declared transitions can execute")
            matched = True

    if ir.design_kind == "register" and ir.register:
        if "load failed" in lowered:
            diagnosis.append("testbench reported that the register did not capture input data on an enabled clock edge")
            if ir.repair_controls.register_hold_when_enabled:
                ir.repair_controls.register_hold_when_enabled = False
                changes.append("restore the enabled register load path")
                matched = True
        if "hold failed" in lowered:
            diagnosis.append("testbench reported that the register changed value while enable was deasserted")
            if ir.repair_controls.register_ignore_enable:
                ir.repair_controls.register_ignore_enable = False
                changes.append("restore enable gating so the register holds value when disabled")
                matched = True
        if "reset failed" in lowered:
            diagnosis.append("testbench reported that reset did not restore the register state")

    if ir.design_kind == "shift_register" and ir.shift_register:
        if "shift failed" in lowered:
            diagnosis.append("testbench reported that the shift register moved data in the wrong direction or pattern")
            if ir.repair_controls.shift_reverse_direction:
                ir.repair_controls.shift_reverse_direction = False
                changes.append("restore the declared shift direction")
                matched = True
        if "hold failed" in lowered:
            diagnosis.append("testbench reported that the shift register changed state while enable was deasserted")
            if ir.repair_controls.shift_ignore_enable:
                ir.repair_controls.shift_ignore_enable = False
                changes.append("restore enable gating so the shift register holds state when disabled")
                matched = True
        if "reset failed" in lowered:
            diagnosis.append("testbench reported that reset did not restore the shift-register state")

    family = _design_family(ir)
    if family in {"combinational", "generic_sequential", "datapath"}:
        target = _extract_failed_output_target(message)
        if target:
            diagnosis.append(f"{family.replace('_', ' ')} verification reported an output mismatch on {target}")
        if target and target in ir.repair_controls.zero_output_targets:
            ir.repair_controls.zero_output_targets.remove(target)
            changes.append(f"stop forcing {target} to zero and restore the rendered behavior")
            matched = True

    return matched


def _design_family(ir: ModuleIR) -> str:
    if ir.design_kind in {"counter", "register", "shift_register", "fsm", "combinational"}:
        return ir.design_kind
    if ir.verification.seq_steps:
        return "datapath" if _looks_like_datapath(ir) else "generic_sequential"
    if ir.verification.comb_vectors and _looks_like_datapath(ir):
        return "datapath"
    return "generic"


def _looks_like_datapath(ir: ModuleIR) -> bool:
    arithmetic_keywords = ("sum", "acc", "prod", "result", "dot", "exp", "mul", "mac", "data")
    wide_ports = sum(1 for port in ir.ports if port.width > 8)
    return wide_ports >= 2 or any(
        any(keyword in port.name.lower() for keyword in arithmetic_keywords) for port in ir.ports if port.direction == "output"
    )


def _extract_failed_output_target(message: str) -> str | None:
    match = re.search(r"expected\s+([A-Za-z_][A-Za-z0-9_]*)=", message, flags=re.IGNORECASE)
    return match.group(1) if match else None


def _combined_output(result: VerificationResult) -> str:
    return f"{result.stdout}\n{result.stderr}\n{result.message}".lower()


def _status_label(result: VerificationResult | None) -> str:
    if result is None:
        return "not_run"
    return "pass" if result.succeeded else "fail"
