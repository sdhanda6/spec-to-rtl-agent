from __future__ import annotations

import re

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
    ports_doc = _document_ports(document, module)
    design = _normalized_design(document)
    timing = _expect_map(document.get("timing", {}), "timing")
    verification_doc = _expect_map(document.get("verification", {}), "verification")
    behavior_doc = _expect_map(design.get("behavior", {}), "design.behavior")
    ports = [_lower_port(entry) for entry in _expect_list(ports_doc, "ports")]
    timing_reset = _lower_reset(_expect_map(timing.get("reset", {}), "timing.reset"))
    signals = [_lower_signal(entry) for entry in _expect_list(document.get("signals", []), "signals")]
    state = [_lower_state(entry) for entry in _expect_list(design.get("state", []), "design.state")]
    inferred_processes, inferred_signals = _lower_operation_processes(behavior_doc, ports, signals, state, timing_reset)
    processes = [_lower_process(entry) for entry in _expect_list(behavior_doc.get("processes", []), "design.behavior.processes")]
    processes.extend(inferred_processes)
    combinational = [] if inferred_processes else _lower_combinational(behavior_doc)

    ir = ModuleIR(
        name=str(module.get("name", "phase2_top")),
        ports=ports,
        design_kind=str(design.get("kind", "generic")),  # type: ignore[arg-type]
        notes=[str(item) for item in _expect_list(design.get("notes", []), "design.notes")],
        flow_hints=_expect_map(document.get("flow", {}), "flow"),
        clock=_optional_str(timing.get("clock")),
        reset=timing_reset,
        signals=[*signals, *inferred_signals],
        state=state,
        counter=_lower_counter(_expect_map(behavior_doc.get("counter", {}), "design.behavior.counter")),
        register=_lower_register(_expect_map(behavior_doc.get("register", {}), "design.behavior.register")),
        shift_register=_lower_shift_register(
            _expect_map(behavior_doc.get("shift_register", {}), "design.behavior.shift_register")
        ),
        fsm=_lower_fsm(_expect_map(behavior_doc.get("fsm", {}), "design.behavior.fsm")),
        combinational=combinational,
        processes=processes,
        verification=_lower_verification(verification_doc),
    )
    return _auto_wrap_for_tapeout(ir)


def _document_ports(document: dict[str, object], module: dict[str, object]) -> object:
    ports = document.get("ports")
    if ports is None and isinstance(module.get("ports"), list):
        return module.get("ports")
    return ports if ports is not None else []


def _normalized_design(document: dict[str, object]) -> dict[str, object]:
    design = dict(_expect_map(document.get("design", {}), "design"))
    if "behavior" not in design and isinstance(document.get("behavior"), dict):
        design["behavior"] = document["behavior"]
    if "kind" not in design:
        behavior = design.get("behavior", {})
        if isinstance(behavior, dict) and behavior.get("operations"):
            design["kind"] = "combinational"
        else:
            design["kind"] = "generic"
    return design


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


def _lower_operation_processes(
    behavior_doc: dict[str, object],
    ports: list[PortIR],
    signals: list[SignalIR],
    state: list[StateSignalIR],
    reset: ResetIR | None,
) -> tuple[list[ProcessIR], list[SignalIR]]:
    raw_operations = behavior_doc.get("operations")
    if not isinstance(raw_operations, list):
        return [], []
    if all(isinstance(entry, dict) and "target" in entry for entry in raw_operations):
        return [], []

    operation_texts = [_operation_text(entry) for entry in raw_operations]
    operation_texts = [text for text in operation_texts if text]
    if not operation_texts:
        return [], []

    width_by_name = _known_widths(ports, signals, state)
    assigned_targets = _assigned_targets(operation_texts)
    inferred_signals: list[SignalIR] = []
    known_targets = set(width_by_name)
    for target in assigned_targets:
        if target in known_targets:
            continue
        width = _infer_assignment_width(target, operation_texts, width_by_name)
        width_by_name[target] = width
        known_targets.add(target)
        inferred_signals.append(SignalIR(name=target, width=width, kind="reg", description="inferred from operation list"))

    reset_names = _reset_names(ports, reset)
    body = _operation_texts_to_statements(operation_texts, reset_names)
    output_names = [port.name for port in ports if port.direction == "output"]
    if not body:
        body = [
            AssignmentIR(target=name, expr=parse_expr(name), blocking=False)
            for name in output_names
        ]
    reset_targets = _dedupe([*output_names, *(target for target in assigned_targets if target not in output_names)])
    reset_body = [AssignmentIR(target=target, expr=parse_expr("0"), blocking=False) for target in reset_targets]
    clock = _first_clock_port(ports)
    return [ProcessIR(kind="seq", body=body, clock=clock, reset=reset, reset_body=reset_body)], inferred_signals


def _operation_text(entry: object) -> str:
    if isinstance(entry, str):
        return entry.strip()
    if isinstance(entry, dict) and len(entry) == 1:
        key, value = next(iter(entry.items()))
        prefix = str(key).strip()
        if prefix.lower() == "else":
            return f"else: {value}".strip()
        if prefix.lower().startswith("else if") or prefix.lower().startswith("if "):
            return f"{prefix}: {value}".strip()
    return ""


def _operation_texts_to_statements(texts: list[str], reset_names: set[str]) -> list[AssignmentIR | IfIR]:
    body: list[AssignmentIR | IfIR] = []
    current_if: IfIR | None = None
    for text in texts:
        kind, condition, assignment_text = _parse_operation_line(text)
        if not assignment_text:
            continue
        assignment = _assignment_from_text(assignment_text)
        if assignment is None:
            continue
        if condition and _is_reset_condition(condition, reset_names):
            current_if = None
            continue
        if kind == "if":
            node = IfIR(condition=parse_expr(_normalize_expr(condition or "1")), then_body=[assignment])
            body.append(node)
            current_if = node
        elif kind == "else_if":
            node = IfIR(condition=parse_expr(_normalize_expr(condition or "1")), then_body=[assignment])
            if current_if is None:
                body.append(node)
            else:
                current_if.else_body = [node]
            current_if = node
        elif kind == "else":
            if current_if is None:
                body.append(assignment)
            else:
                current_if.else_body = [assignment]
            current_if = None
        else:
            body.append(assignment)
            current_if = None
    return body


def _parse_operation_line(text: str) -> tuple[str, str | None, str]:
    normalized = " ".join(text.strip().split())
    lowered = normalized.lower()
    if lowered.startswith("else if "):
        condition, _, assignment = normalized[8:].partition(":")
        return "else_if", condition.strip(), assignment.strip()
    if lowered.startswith("if "):
        condition, _, assignment = normalized[3:].partition(":")
        return "if", condition.strip(), assignment.strip()
    if lowered.startswith("else:"):
        return "else", None, normalized.split(":", 1)[1].strip()
    return "assign", None, normalized


def _assignment_from_text(text: str) -> AssignmentIR | None:
    parts = _assignment_parts(text)
    if parts is None:
        return None
    target, expr = parts
    return AssignmentIR(target=target, expr=parse_expr(_normalize_expr(expr)), blocking=False)


def _assignment_parts(text: str) -> tuple[str, str] | None:
    match = re.search(r"(?<![<>=!])=(?!=)", text)
    if not match:
        return None
    target = text[: match.start()].strip()
    expr = text[match.end() :].strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_$]*$", target) or not expr:
        return None
    return target, expr


def _normalize_expr(expr: str) -> str:
    text = expr.strip()
    text = re.sub(r"\band\b", "&&", text, flags=re.IGNORECASE)
    text = re.sub(r"\bor\b", "||", text, flags=re.IGNORECASE)
    return text


def _assigned_targets(texts: list[str]) -> list[str]:
    targets: list[str] = []
    for text in texts:
        _, _, assignment_text = _parse_operation_line(text)
        parts = _assignment_parts(assignment_text)
        if parts is not None:
            targets.append(parts[0])
    return _dedupe(targets)


def _known_widths(ports: list[PortIR], signals: list[SignalIR], state: list[StateSignalIR]) -> dict[str, int]:
    widths = {port.name: port.width for port in ports}
    widths.update({signal.name: signal.width for signal in signals})
    widths.update({item.name: item.width for item in state})
    return widths


def _infer_assignment_width(target: str, texts: list[str], width_by_name: dict[str, int]) -> int:
    literals = _target_related_literals(target, texts)
    if literals:
        return max(1, max(literals).bit_length())
    widths = []
    for text in texts:
        _, _, assignment_text = _parse_operation_line(text)
        parts = _assignment_parts(assignment_text)
        if parts is None or parts[0] != target:
            continue
        refs = [token for token in re.findall(r"\b[A-Za-z_][A-Za-z0-9_$]*\b", parts[1]) if token not in {"if", "else"}]
        widths.extend(width_by_name.get(ref, 1) for ref in refs)
    return max(widths) if widths else 1


def _target_related_literals(target: str, texts: list[str]) -> list[int]:
    values: list[int] = []
    patterns = [
        rf"\b{re.escape(target)}\s*(?:==|=)\s*(\d+)",
        rf"\b{re.escape(target)}\s*(?:<=|>=|<|>)\s*(\d+)",
    ]
    for text in texts:
        for pattern in patterns:
            values.extend(int(match.group(1)) for match in re.finditer(pattern, text))
    return values


def _reset_names(ports: list[PortIR], reset: ResetIR | None) -> set[str]:
    names = {reset.signal} if reset else set()
    names.update(port.name for port in ports if port.direction == "input" and port.name.lower() in {"reset", "rst", "rst_n", "reset_n"})
    return names


def _is_reset_condition(condition: str, reset_names: set[str]) -> bool:
    tokens = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_$]*\b", condition))
    return bool(tokens.intersection(reset_names))


def _auto_wrap_for_tapeout(ir: ModuleIR) -> ModuleIR:
    _register_all_outputs(ir)
    should_sequentialize = _needs_tapeout_sequentialization(ir)
    if not should_sequentialize:
        return ir

    clock = _ensure_clock_port(ir)
    reset = _ensure_reset_port(ir)
    ir.clock = clock
    ir.reset = reset

    if ir.combinational:
        body = [
            AssignmentIR(
                target=operation.target,
                expr=operation.expr if operation.expr is not None else parse_expr(_comb_operation_expr(operation)),
                blocking=False,
            )
            for operation in ir.combinational
        ]
        ir.processes.append(ProcessIR(kind="seq", body=body, clock=clock, reset=reset))
        ir.combinational = []

    for process in ir.processes:
        if process.kind == "comb":
            process.kind = "seq"  # type: ignore[assignment]
        process.clock = process.clock or clock
        process.reset = process.reset or reset
        _ensure_process_reset_body(ir, process)

    if not ir.processes and not any([ir.counter, ir.register, ir.shift_register, ir.fsm]):
        outputs = [port for port in ir.ports if port.direction == "output"]
        body = [AssignmentIR(target=port.name, expr=parse_expr(port.name), blocking=False) for port in outputs]
        process = ProcessIR(kind="seq", body=body, clock=clock, reset=reset)
        _ensure_process_reset_body(ir, process)
        ir.processes.append(process)

    if ir.design_kind == "combinational":
        ir.design_kind = "generic"  # type: ignore[assignment]
    if "auto-wrapped combinational/spec-only logic for clocked OpenROAD flow" not in ir.notes:
        ir.notes.append("auto-wrapped combinational/spec-only logic for clocked OpenROAD flow")
    return ir


def _needs_tapeout_sequentialization(ir: ModuleIR) -> bool:
    if ir.counter or ir.register or ir.shift_register or ir.fsm:
        return False
    has_clock = bool(ir.clock) or any(port.direction == "input" and port.name.lower() in {"clk", "clock"} for port in ir.ports)
    has_reg_output = any(port.direction == "output" and port.kind == "reg" for port in ir.ports)
    if ir.combinational or ir.design_kind in {"combinational", "generic"}:
        return True
    if ir.processes and all(process.kind == "comb" for process in ir.processes):
        return True
    if ir.processes and (not has_clock or not ir.reset):
        return True
    return not has_clock or not has_reg_output


def _register_all_outputs(ir: ModuleIR) -> None:
    for port in ir.ports:
        if port.direction == "output":
            port.kind = "reg"


def _ensure_clock_port(ir: ModuleIR) -> str:
    existing = ir.clock or _first_clock_port(ir.ports)
    if existing:
        if not any(port.name == existing for port in ir.ports):
            ir.ports.insert(0, PortIR(name=existing, direction="input", width=1, kind="wire", description="auto-inserted clock"))
        return existing
    ir.ports.insert(0, PortIR(name="clk", direction="input", width=1, kind="wire", description="auto-inserted clock"))
    return "clk"


def _ensure_reset_port(ir: ModuleIR) -> ResetIR:
    if ir.reset:
        if not any(port.name == ir.reset.signal for port in ir.ports):
            ir.ports.insert(1, PortIR(name=ir.reset.signal, direction="input", width=1, kind="wire", description="auto-inserted reset"))
        return ir.reset
    reset_name = next(
        (port.name for port in ir.ports if port.direction == "input" and port.name.lower() in {"reset", "rst", "rst_n", "reset_n"}),
        None,
    )
    if reset_name is None:
        reset_name = "reset"
        insert_at = 1 if ir.ports and ir.ports[0].name == (ir.clock or "clk") else 0
        ir.ports.insert(insert_at, PortIR(name=reset_name, direction="input", width=1, kind="wire", description="auto-inserted reset"))
    active_low = reset_name.lower().endswith("_n")
    return ResetIR(signal=reset_name, active_low=active_low, asynchronous=True)


def _ensure_process_reset_body(ir: ModuleIR, process: ProcessIR) -> None:
    reset_targets = set(_statement_targets(process.reset_body))
    required = [port.name for port in ir.ports if port.direction == "output"]
    required.extend(target for target in _statement_targets(process.body) if target not in required)
    for target in _dedupe(required):
        if target not in reset_targets:
            process.reset_body.append(AssignmentIR(target=target, expr=parse_expr("0"), blocking=False))


def _statement_targets(statements: list[AssignmentIR | IfIR]) -> list[str]:
    targets: list[str] = []
    for statement in statements:
        if isinstance(statement, AssignmentIR):
            targets.append(statement.target)
        else:
            targets.extend(_statement_targets(statement.then_body))
            targets.extend(_statement_targets(statement.else_body))
    return _dedupe(targets)


def _comb_operation_expr(operation: CombBehaviorIR) -> str:
    if operation.operator == "buf" and operation.operands:
        return operation.operands[0]
    if operation.operator == "not" and operation.operands:
        return f"~{operation.operands[0]}"
    if operation.operator == "and":
        return " & ".join(operation.operands)
    if operation.operator == "or":
        return " | ".join(operation.operands)
    if operation.operator == "xor":
        return " ^ ".join(operation.operands)
    if operation.operator == "add":
        return " + ".join(operation.operands)
    if operation.operator == "sub":
        return " - ".join(operation.operands)
    if operation.operator == "mux" and operation.select:
        false_value = operation.operands[0] if operation.operands else "0"
        true_value = operation.operands[1] if len(operation.operands) > 1 else false_value
        return f"{operation.select} ? {true_value} : {false_value}"
    if operation.operator == "eq":
        return " == ".join(operation.operands)
    if operation.operator == "lt":
        return " < ".join(operation.operands)
    if operation.operator == "gt":
        return " > ".join(operation.operands)
    return "0"


def _first_clock_port(ports: list[PortIR]) -> str | None:
    for port in ports:
        if port.direction == "input" and port.name.lower() in {"clk", "clock"}:
            return port.name
    return None


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            ordered.append(item)
            seen.add(item)
    return ordered


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
