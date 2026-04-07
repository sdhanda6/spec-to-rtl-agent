from __future__ import annotations

from spec2rtl.expr import parse_expr
from spec2rtl.ir import (
    AssignmentIR,
    CombBehaviorIR,
    CombVectorIR,
    CounterBehaviorIR,
    FSMBehaviorIR,
    FSMOutputIR,
    IfIR,
    ModuleIR,
    PortIR,
    ProcessIR,
    RegisterBehaviorIR,
    ResetIR,
    SeqStepIR,
    SignalIR,
    ShiftRegisterBehaviorIR,
    StateSignalIR,
    TransitionIR,
    VerificationIntentIR,
)


def lower_document_to_ir(document: dict[str, object]) -> ModuleIR:
    module = _expect_map(document.get("module", {}), "module")
    design = _expect_map(document.get("design", {}), "design")
    timing = _expect_map(document.get("timing", {}), "timing")
    verification_doc = _expect_map(document.get("verification", {}), "verification")
    behavior_doc = _expect_map(design.get("behavior", {}), "design.behavior")

    return ModuleIR(
        name=str(module.get("name", "phase2_top")),
        ports=[_lower_port(entry) for entry in _expect_list(document.get("ports", []), "ports")],
        design_kind=str(design.get("kind", "generic")),  # type: ignore[arg-type]
        notes=[str(item) for item in _expect_list(design.get("notes", []), "design.notes")],
        clock=_optional_str(timing.get("clock")),
        reset=_lower_reset(_expect_map(timing.get("reset", {}), "timing.reset")),
        signals=[_lower_signal(entry) for entry in _expect_list(document.get("signals", []), "signals")],
        state=[_lower_state(entry) for entry in _expect_list(design.get("state", []), "design.state")],
        counter=_lower_counter(_expect_map(behavior_doc.get("counter", {}), "design.behavior.counter")),
        register=_lower_register(_expect_map(behavior_doc.get("register", {}), "design.behavior.register")),
        shift_register=_lower_shift_register(
            _expect_map(behavior_doc.get("shift_register", {}), "design.behavior.shift_register")
        ),
        fsm=_lower_fsm(_expect_map(behavior_doc.get("fsm", {}), "design.behavior.fsm")),
        combinational=_lower_combinational(behavior_doc),
        processes=[_lower_process(entry) for entry in _expect_list(behavior_doc.get("processes", []), "design.behavior.processes")],
        verification=_lower_verification(verification_doc),
    )


def _lower_port(entry: object) -> PortIR:
    mapping = _expect_map(entry, "port")
    return PortIR(
        name=str(mapping["name"]),
        direction=str(mapping.get("dir", mapping.get("direction", "input"))),  # type: ignore[arg-type]
        width=int(mapping.get("width", 1)),
        kind=str(mapping.get("kind", "wire")),
        description=str(mapping.get("description", "")),
    )


def _lower_reset(mapping: dict[str, object]) -> ResetIR | None:
    signal = mapping.get("signal")
    if not signal:
        return None
    return ResetIR(
        signal=str(signal),
        active_low=str(mapping.get("active", "high")).lower() == "low",
        asynchronous=str(mapping.get("mode", "async")).lower() == "async",
    )


def _lower_signal(entry: object) -> SignalIR:
    mapping = _expect_map(entry, "signal")
    return SignalIR(
        name=str(mapping["name"]),
        width=int(mapping.get("width", 1)),
        kind=str(mapping.get("kind", "wire")),  # type: ignore[arg-type]
        description=str(mapping.get("description", "")),
    )


def _lower_state(entry: object) -> StateSignalIR:
    mapping = _expect_map(entry, "state entry")
    return StateSignalIR(
        name=str(mapping["name"]),
        width=int(mapping.get("width", 1)),
        reset_value=int(mapping.get("reset", 0)),
    )


def _lower_counter(mapping: dict[str, object]) -> CounterBehaviorIR | None:
    if not mapping:
        return None
    return CounterBehaviorIR(
        target=str(mapping["target"]),
        enable=_optional_str(mapping.get("enable")),
        direction=str(mapping.get("direction", "up")),  # type: ignore[arg-type]
        step=int(mapping.get("step", 1)),
        wrap=bool(mapping.get("wrap", True)),
    )


def _lower_register(mapping: dict[str, object]) -> RegisterBehaviorIR | None:
    if not mapping:
        return None
    return RegisterBehaviorIR(
        target=str(mapping["target"]),
        data=str(mapping["data"]),
        enable=_optional_str(mapping.get("enable")),
        hold_value=_optional_str(mapping.get("hold")),
    )


def _lower_shift_register(mapping: dict[str, object]) -> ShiftRegisterBehaviorIR | None:
    if not mapping:
        return None
    return ShiftRegisterBehaviorIR(
        target=str(mapping["target"]),
        serial_in=str(mapping["serial_in"]),
        serial_out=_optional_str(mapping.get("serial_out")),
        enable=_optional_str(mapping.get("enable")),
        direction=str(mapping.get("direction", "left")),  # type: ignore[arg-type]
    )


def _lower_fsm(mapping: dict[str, object]) -> FSMBehaviorIR | None:
    if not mapping:
        return None
    transitions = []
    for entry in _expect_list(mapping.get("transitions", []), "design.behavior.fsm.transitions"):
        item = _expect_map(entry, "fsm transition")
        transitions.append(
            TransitionIR(
                src=str(item["src"]),
                dst=str(item["dst"]),
                condition=_optional_str(item.get("condition")),
                expect_hold_when_false=bool(item.get("expect_hold_when_false", True)),
            )
        )
    outputs = []
    for entry in _expect_list(mapping.get("outputs", []), "design.behavior.fsm.outputs"):
        item = _expect_map(entry, "fsm output")
        assignments = {
            str(key): str(value)
            for key, value in _expect_map(item.get("assignments", {}), "fsm output assignments").items()
        }
        outputs.append(FSMOutputIR(state=str(item["state"]), assignments=assignments))
    return FSMBehaviorIR(
        state_signal=str(mapping.get("state_signal", "state_q")),
        states=[str(item) for item in _expect_list(mapping.get("states", []), "design.behavior.fsm.states")],
        reset_state=str(mapping.get("reset_state", "IDLE")),
        transitions=transitions,
        outputs=outputs,
    )


def _lower_combinational(behavior_doc: dict[str, object]) -> list[CombBehaviorIR]:
    operations: list[CombBehaviorIR] = []
    for entry in _expect_list(behavior_doc.get("operations", []), "design.behavior.operations"):
        item = _expect_map(entry, "design.behavior.operations item")
        operations.append(
            CombBehaviorIR(
                target=str(item["target"]),
                operator=str(item.get("operator", "expr")),  # type: ignore[arg-type]
                operands=[str(value) for value in _expect_list(item.get("operands", []), "operation operands")],
                select=_optional_str(item.get("select")),
                expr=parse_expr(item["expr"]) if "expr" in item else None,
            )
        )
    if operations:
        return operations
    for entry in _expect_list(behavior_doc.get("assignments", []), "design.behavior.assignments"):
        item = _expect_map(entry, "combinational assignment")
        operations.append(_infer_operation_from_assignment(str(item["target"]), str(item["expr"])))
    return operations


def _lower_process(entry: object) -> ProcessIR:
    mapping = _expect_map(entry, "process")
    return ProcessIR(
        kind=str(mapping.get("kind", "comb")),  # type: ignore[arg-type]
        body=_lower_statements(_expect_list(mapping.get("body", []), "process.body")),
        clock=_optional_str(mapping.get("clock")),
        reset=_lower_reset(_expect_map(mapping.get("reset", {}), "process.reset")),
        reset_body=_lower_statements(_expect_list(mapping.get("reset_body", []), "process.reset_body")),
    )


def _lower_statements(entries: list[object]) -> list[AssignmentIR | IfIR]:
    statements: list[AssignmentIR | IfIR] = []
    for entry in entries:
        mapping = _expect_map(entry, "statement")
        if "assign" in mapping:
            item = _expect_map(mapping["assign"], "assign statement")
            statements.append(
                AssignmentIR(
                    target=str(item["target"]),
                    expr=parse_expr(item["expr"]),
                    blocking=bool(item.get("blocking", True)),
                )
            )
        elif "if" in mapping:
            item = _expect_map(mapping["if"], "if statement")
            statements.append(
                IfIR(
                    condition=parse_expr(item["cond"]),
                    then_body=_lower_statements(_expect_list(item.get("then", []), "if.then")),
                    else_body=_lower_statements(_expect_list(item.get("else", []), "if.else")),
                )
            )
        else:
            raise ValueError(f"Unsupported statement: {mapping}")
    return statements


def _infer_operation_from_assignment(target: str, expr: str) -> CombBehaviorIR:
    normalized = expr.strip()
    if "?" in normalized and ":" in normalized:
        condition, rhs = normalized.split("?", 1)
        when_true, when_false = rhs.split(":", 1)
        return CombBehaviorIR(
            target=target,
            operator="mux",
            operands=[when_false.strip(), when_true.strip()],
            select=condition.strip(),
            expr=parse_expr(normalized),
        )
    for symbol, operator in [("&", "and"), ("|", "or"), ("^", "xor"), ("+", "add"), ("-", "sub")]:
        parts = [part.strip() for part in normalized.split(symbol)]
        if len(parts) == 2 and all(parts):
            return CombBehaviorIR(target=target, operator=operator, operands=parts, expr=parse_expr(normalized))
    if normalized.startswith("~"):
        return CombBehaviorIR(target=target, operator="not", operands=[normalized[1:].strip()], expr=parse_expr(normalized))
    for symbol, operator in [("==", "eq"), ("<", "lt"), (">", "gt")]:
        parts = [part.strip() for part in normalized.split(symbol)]
        if len(parts) == 2 and all(parts):
            return CombBehaviorIR(target=target, operator=operator, operands=parts, expr=parse_expr(normalized))
    return CombBehaviorIR(target=target, operator="expr", expr=parse_expr(normalized))


def _lower_verification(mapping: dict[str, object]) -> VerificationIntentIR:
    tb = _expect_map(mapping.get("tb", {}), "verification.tb")
    return VerificationIntentIR(
        enable_tb=bool(tb.get("enabled", True)),
        checks=[str(item) for item in _expect_list(tb.get("checks", []), "verification.tb.checks")],
        requested_level=str(tb.get("level", "functional" if tb.get("enabled", True) else "none")),  # type: ignore[arg-type]
        comb_vectors=[_lower_comb_vector(entry) for entry in _expect_list(tb.get("comb_vectors", []), "verification.tb.comb_vectors")],
        seq_steps=[_lower_seq_step(entry) for entry in _expect_list(tb.get("seq_steps", []), "verification.tb.seq_steps")],
    )


def _lower_comb_vector(entry: object) -> CombVectorIR:
    mapping = _expect_map(entry, "comb vector")
    return CombVectorIR(
        name=str(mapping["name"]),
        drive={str(key): parse_expr(value) for key, value in _expect_map(mapping.get("drive", {}), "comb vector drive").items()},
        expect={str(key): parse_expr(value) for key, value in _expect_map(mapping.get("expect", {}), "comb vector expect").items()},
    )


def _lower_seq_step(entry: object) -> SeqStepIR:
    mapping = _expect_map(entry, "seq step")
    return SeqStepIR(
        name=str(mapping["name"]),
        drive={str(key): parse_expr(value) for key, value in _expect_map(mapping.get("drive", {}), "seq step drive").items()},
        expect={str(key): parse_expr(value) for key, value in _expect_map(mapping.get("expect", {}), "seq step expect").items()},
        edge=_optional_str(mapping.get("edge")),
        delay=int(mapping["delay"]) if "delay" in mapping else None,
    )


def _expect_map(value: object, label: str) -> dict[str, object]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def _expect_list(value: object, label: str) -> list[object]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)
