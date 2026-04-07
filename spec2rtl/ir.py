from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


Direction = Literal["input", "output"]
DesignKind = Literal["counter", "register", "shift_register", "fsm", "combinational", "generic"]
VerificationLevel = Literal["none", "smoke", "functional"]
CombOperator = Literal["expr", "buf", "not", "and", "or", "xor", "add", "sub", "mux", "eq", "lt", "gt"]
StmtKind = Literal["assign", "if"]
SpecSourceType = Literal["yaml", "text"]
FinalClassification = Literal["functionally_verified", "compile_and_smoke_verified", "partially_supported", "unsupported_or_ambiguous"]


@dataclass
class PortIR:
    name: str
    direction: Direction
    width: int = 1
    kind: str = "wire"
    description: str = ""


@dataclass
class SignalIR:
    name: str
    width: int = 1
    kind: Literal["wire", "reg"] = "wire"
    description: str = ""


@dataclass
class ExprIR:
    kind: str


@dataclass
class LiteralExprIR(ExprIR):
    value: str


@dataclass
class RefExprIR(ExprIR):
    name: str


@dataclass
class UnaryExprIR(ExprIR):
    op: str
    operand: "ExprIR"


@dataclass
class BinaryExprIR(ExprIR):
    op: str
    left: "ExprIR"
    right: "ExprIR"


@dataclass
class TernaryExprIR(ExprIR):
    condition: "ExprIR"
    when_true: "ExprIR"
    when_false: "ExprIR"


@dataclass
class ConcatExprIR(ExprIR):
    parts: list["ExprIR"] = field(default_factory=list)


@dataclass
class SliceExprIR(ExprIR):
    target: "ExprIR"
    msb: int
    lsb: int


@dataclass
class IndexExprIR(ExprIR):
    target: "ExprIR"
    index: int


@dataclass
class ResetIR:
    signal: str
    active_low: bool = False
    asynchronous: bool = True


@dataclass
class StateSignalIR:
    name: str
    width: int = 1
    reset_value: int = 0


@dataclass
class CounterBehaviorIR:
    target: str
    enable: str | None = None
    direction: Literal["up", "down"] = "up"
    step: int = 1
    wrap: bool = True


@dataclass
class RegisterBehaviorIR:
    target: str
    data: str
    enable: str | None = None
    hold_value: str | None = None


@dataclass
class ShiftRegisterBehaviorIR:
    target: str
    serial_in: str
    serial_out: str | None = None
    enable: str | None = None
    direction: Literal["left", "right"] = "left"


@dataclass
class TransitionIR:
    src: str
    dst: str
    condition: str | None = None
    expect_hold_when_false: bool = True


@dataclass
class FSMOutputIR:
    state: str
    assignments: dict[str, str] = field(default_factory=dict)


@dataclass
class FSMBehaviorIR:
    state_signal: str
    states: list[str]
    reset_state: str
    transitions: list[TransitionIR] = field(default_factory=list)
    outputs: list[FSMOutputIR] = field(default_factory=list)


@dataclass
class CombBehaviorIR:
    target: str
    operator: CombOperator = "expr"
    operands: list[str] = field(default_factory=list)
    select: str | None = None
    expr: ExprIR | None = None


@dataclass
class VerificationIntentIR:
    enable_tb: bool = True
    checks: list[str] = field(default_factory=list)
    requested_level: VerificationLevel = "smoke"
    comb_vectors: list["CombVectorIR"] = field(default_factory=list)
    seq_steps: list["SeqStepIR"] = field(default_factory=list)


@dataclass
class AmbiguityFindingIR:
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "warning"
    inferred_value: str | None = None


@dataclass
class NormalizedCandidateIR:
    candidate_id: str
    title: str
    source_type: SpecSourceType
    document: dict[str, Any]
    extracted_semantics: dict[str, Any] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    ambiguities: list[AmbiguityFindingIR] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    internal_checks: list[str] = field(default_factory=list)
    internal_score: float = 0.0


@dataclass
class SpecParseResultIR:
    source_type: SpecSourceType
    raw_text: str
    normalized_source: dict[str, Any] | None = None
    extracted_semantics: dict[str, Any] = field(default_factory=dict)
    findings: list[AmbiguityFindingIR] = field(default_factory=list)
    candidates: list[NormalizedCandidateIR] = field(default_factory=list)


@dataclass
class VerificationEvidenceIR:
    tb_kind: str = "none"
    achieved_level: VerificationLevel = "none"
    oracle_independent: bool = False
    covered_checks: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class GeneratedTestbench:
    text: str | None
    evidence: VerificationEvidenceIR


@dataclass
class RepairDecision:
    attempt: int
    action: str
    reason: str


@dataclass
class RepairControlsIR:
    counter_hold_when_enabled: bool = False
    counter_ignore_enable: bool = False
    register_hold_when_enabled: bool = False
    register_ignore_enable: bool = False
    shift_reverse_direction: bool = False
    shift_ignore_enable: bool = False
    fsm_force_self_loop: bool = False
    zero_output_targets: list[str] = field(default_factory=list)


@dataclass
class AssignmentIR:
    target: str
    expr: ExprIR
    blocking: bool = True


@dataclass
class IfIR:
    condition: ExprIR
    then_body: list["StatementIR"] = field(default_factory=list)
    else_body: list["StatementIR"] = field(default_factory=list)


StatementIR = AssignmentIR | IfIR


@dataclass
class ProcessIR:
    kind: Literal["comb", "seq"]
    body: list[StatementIR] = field(default_factory=list)
    clock: str | None = None
    reset: ResetIR | None = None
    reset_body: list[StatementIR] = field(default_factory=list)


@dataclass
class CombVectorIR:
    name: str
    drive: dict[str, ExprIR] = field(default_factory=dict)
    expect: dict[str, ExprIR] = field(default_factory=dict)


@dataclass
class SeqStepIR:
    name: str
    drive: dict[str, ExprIR] = field(default_factory=dict)
    expect: dict[str, ExprIR] = field(default_factory=dict)
    edge: str | None = None
    delay: int | None = None


@dataclass
class ModuleIR:
    name: str
    ports: list[PortIR]
    design_kind: DesignKind
    notes: list[str] = field(default_factory=list)
    clock: str | None = None
    reset: ResetIR | None = None
    signals: list[SignalIR] = field(default_factory=list)
    state: list[StateSignalIR] = field(default_factory=list)
    counter: CounterBehaviorIR | None = None
    register: RegisterBehaviorIR | None = None
    shift_register: ShiftRegisterBehaviorIR | None = None
    fsm: FSMBehaviorIR | None = None
    combinational: list[CombBehaviorIR] = field(default_factory=list)
    processes: list[ProcessIR] = field(default_factory=list)
    verification: VerificationIntentIR = field(default_factory=VerificationIntentIR)
    repairs: list[RepairDecision] = field(default_factory=list)
    repair_controls: RepairControlsIR = field(default_factory=RepairControlsIR)


@dataclass
class RenderStrategy:
    name: str
    internalize_outputs: bool = False
    include_header_comments: bool = True
