from __future__ import annotations

import copy
import re
from pathlib import Path

from spec2rtl.frontend import load_spec_document
from spec2rtl.ir import AmbiguityFindingIR, NormalizedCandidateIR, SpecParseResultIR


TEXT_SUFFIXES = {".txt", ".md", ".rst", ".spec"}


def load_spec_source(spec_path: Path, top_override: str | None = None) -> SpecParseResultIR:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    text = spec_path.read_text(encoding="utf-8").strip()
    suffix = spec_path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        document = load_spec_document(spec_path, top_override=top_override)
        extracted = _extract_structured_semantics(document)
        candidate = NormalizedCandidateIR(
            candidate_id="cand_1",
            title="structured_document",
            source_type="yaml",
            document=document,
            extracted_semantics=extracted,
            internal_checks=_structured_internal_checks(document),
            internal_score=_structured_score(document),
        )
        return SpecParseResultIR(
            source_type="yaml",
            raw_text=text,
            normalized_source=document,
            extracted_semantics=extracted,
            candidates=[candidate],
        )
    if suffix in TEXT_SUFFIXES or suffix not in {".yaml", ".yml"}:
        return _parse_text_spec(spec_path, text, top_override=top_override)
    raise ValueError(f"Unsupported spec format: {spec_path}")


def _extract_structured_semantics(document: dict[str, object]) -> dict[str, object]:
    module = document.get("module", {}) if isinstance(document.get("module"), dict) else {}
    timing = document.get("timing", {}) if isinstance(document.get("timing"), dict) else {}
    design = document.get("design", {}) if isinstance(document.get("design"), dict) else {}
    behavior = design.get("behavior", {}) if isinstance(design.get("behavior"), dict) else {}
    flow = document.get("flow", {}) if isinstance(document.get("flow"), dict) else {}
    return {
        "module_name": module.get("name"),
        "ports": document.get("ports", []),
        "clock": timing.get("clock"),
        "reset": timing.get("reset"),
        "state": design.get("state", []),
        "behavior_keys": sorted(behavior.keys()),
        "design_kind_hint": design.get("kind", "generic"),
        "flow": flow,
    }


def _structured_internal_checks(document: dict[str, object]) -> list[str]:
    checks: list[str] = []
    if isinstance(document.get("module"), dict) and document["module"].get("name"):
        checks.append("module name present")
    ports = document.get("ports")
    if isinstance(ports, list) and ports:
        checks.append("port list present")
    timing = document.get("timing")
    if isinstance(timing, dict) and timing.get("clock"):
        checks.append("clock semantics present")
    return checks


def _structured_score(document: dict[str, object]) -> float:
    score = 1.0
    if isinstance(document.get("ports"), list) and document["ports"]:
        score += 0.5
    if isinstance(document.get("timing"), dict) and document["timing"].get("clock"):
        score += 0.25
    if isinstance(document.get("design"), dict) and document["design"].get("behavior"):
        score += 0.5
    return score


def _parse_text_spec(spec_path: Path, text: str, top_override: str | None = None) -> SpecParseResultIR:
    findings: list[AmbiguityFindingIR] = []
    lower = text.lower()
    module_name = top_override or _extract_module_name(text) or spec_path.stem
    if not _extract_module_name(text):
        findings.append(
            AmbiguityFindingIR(
                code="module_name_inferred",
                message="module name was not stated explicitly; inferred from the file name",
                severity="warning",
                inferred_value=module_name,
            )
        )

    clock = _extract_clock(text)
    reset = _extract_reset(text)
    ports = _extract_ports(text, findings)
    state_specs = _extract_state_specs(text)
    output_names = {port["name"] for port in ports if port["dir"] == "output"}
    input_names = {port["name"] for port in ports if port["dir"] == "input"}

    behavior, verification_tb, behavior_findings, assumptions, branch_points = _extract_text_behavior(
        lower, input_names, output_names, state_specs, clock, reset
    )
    findings.extend(behavior_findings)

    document = {
        "module": {"name": module_name},
        "ports": ports,
        "timing": {"clock": clock} if clock else {},
        "design": {"kind": "generic", "notes": ["normalized from unstructured text"], "state": state_specs, "behavior": behavior},
        "verification": {"tb": verification_tb},
    }
    if reset:
        document.setdefault("timing", {})["reset"] = reset
        if not reset.get("polarity_explicit"):
            findings.append(
                AmbiguityFindingIR(
                    code="reset_polarity_inferred",
                    message="reset polarity was not explicit in the prose; inferred from naming conventions",
                    severity="warning",
                    inferred_value=str(reset.get("active")),
                )
            )
        if not reset.get("mode_explicit"):
            findings.append(
                AmbiguityFindingIR(
                    code="reset_mode_inferred",
                    message="reset timing mode was not explicit in the prose; defaulted to synchronous reset",
                    severity="warning",
                    inferred_value=str(reset.get("mode")),
                )
            )

    extracted = {
        "module_name": module_name,
        "clock": clock,
        "reset": reset,
        "ports": ports,
        "state_variables": state_specs,
        "behavior_summary": _behavior_summary(behavior),
    }

    candidates = _generate_text_candidates(document, extracted, assumptions, findings, branch_points)
    return SpecParseResultIR(
        source_type="text",
        raw_text=text,
        normalized_source=document,
        extracted_semantics=extracted,
        findings=findings,
        candidates=candidates,
    )


def _extract_module_name(text: str) -> str | None:
    patterns = [
        r"\bmodule\s+(?:named\s+)?([A-Za-z_][A-Za-z0-9_]*)",
        r"\bblock\s+(?:named\s+)?([A-Za-z_][A-Za-z0-9_]*)",
        r"\bdesign\s+(?:a|an)?\s*module\s+(?:named\s+)?([A-Za-z_][A-Za-z0-9_]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_clock(text: str) -> str | None:
    match = re.search(r"(?:rising edge|posedge|clock(?:ed)? by)\s+(?:of\s+)?([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    if re.search(r"\bclock\b", text, flags=re.IGNORECASE):
        return "clk"
    return None


def _extract_reset(text: str) -> dict[str, object] | None:
    reset_signal = None
    named = re.search(r"\b(rst_n|reset_n|reset|rst)\b", text, flags=re.IGNORECASE)
    if named:
        reset_signal = named.group(1)
    else:
        match = re.search(r"reset(?: signal)?\s+([A-Za-z_][A-Za-z0-9_]*)", text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1)
            if candidate.lower() not in {"is", "low", "high", "active", "asserted"}:
                reset_signal = candidate
    if not reset_signal:
        return None
    polarity_explicit = bool(re.search(r"(active[- ]low|active[- ]high|reset is low|reset is high|when .* reset .* low|when .* reset .* high)", text, flags=re.IGNORECASE))
    active_low = bool(re.search(r"(active[- ]low|reset is low|when .* reset .* low|negedge)", text, flags=re.IGNORECASE)) or (not polarity_explicit and reset_signal.lower().endswith("_n"))
    mode_explicit = bool(re.search(r"\basync|asynchronous|synchronous|sync\b", text, flags=re.IGNORECASE))
    asynchronous = bool(re.search(r"\basync|asynchronous|negedge|posedge .* or", text, flags=re.IGNORECASE))
    return {
        "signal": reset_signal,
        "active": "low" if active_low else "high",
        "mode": "async" if asynchronous else "sync",
        "polarity_explicit": polarity_explicit,
        "mode_explicit": mode_explicit,
    }


def _extract_ports(text: str, findings: list[AmbiguityFindingIR]) -> list[dict[str, object]]:
    ports: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip(" -*\t")
        if not line:
            continue
        if line.lower().startswith("inputs:"):
            _extend_port_list(line.split(":", 1)[1], "input", ports, seen, findings)
            continue
        if line.lower().startswith("outputs:"):
            _extend_port_list(line.split(":", 1)[1], "output", ports, seen, findings)
            continue
        match = re.match(
            r"(?:(input|output)\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^\)]*)\))?\s*(?::|-)?\s*(.*)$",
            line,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        direction = (match.group(1) or "").lower()
        if direction not in {"input", "output"}:
            continue
        name = match.group(2)
        width_text = f"{match.group(3) or ''} {match.group(4) or ''}"
        width = _extract_width(width_text)
        if width is None:
            width = 1
            findings.append(
                AmbiguityFindingIR(
                    code="width_defaulted",
                    message=f"width for port {name} was not explicit; defaulted to 1 bit",
                    severity="warning",
                    inferred_value="1",
                )
            )
        ports.append({"name": name, "dir": direction, "width": width, "kind": "reg" if direction == "output" else "wire"})
        seen.add(name)
    if not ports:
        findings.append(AmbiguityFindingIR(code="ports_missing", message="no ports could be extracted from the text spec", severity="error"))
    return ports


def _extend_port_list(body: str, direction: str, ports: list[dict[str, object]], seen: set[str], findings: list[AmbiguityFindingIR]) -> None:
    for chunk in re.split(r",|;", body):
        item = chunk.strip()
        if not item:
            continue
        match = re.match(r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*\(([^\)]*)\))?(?:\s+([0-9]+)-bit)?", item, flags=re.IGNORECASE)
        if not match:
            continue
        name = match.group(1)
        if name in seen:
            continue
        width = _extract_width(" ".join(part for part in [match.group(2) or "", match.group(3) or ""] if part)) or 1
        if width == 1 and not match.group(2) and not match.group(3):
            findings.append(
                AmbiguityFindingIR(
                    code="width_defaulted",
                    message=f"width for port {name} was not explicit; defaulted to 1 bit",
                    severity="warning",
                    inferred_value="1",
                )
            )
        ports.append({"name": name, "dir": direction, "width": width, "kind": "reg" if direction == "output" else "wire"})
        seen.add(name)


def _extract_width(text: str) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d+)\s*-\s*bit|(\d+)\s*bit", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1) or match.group(2))
    match = re.search(r"\[(\d+)\s*:\s*(\d+)\]", text)
    if match:
        return abs(int(match.group(1)) - int(match.group(2))) + 1
    return None


def _extract_state_specs(text: str) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?:is|as)\s+an?\s+(\d+)-bit\s+(?:state|register|counter)", text, flags=re.IGNORECASE):
        specs.append({"name": match.group(1), "width": int(match.group(2)), "reset": 0})
    return specs


def _extract_text_behavior(
    lower: str,
    input_names: set[str],
    output_names: set[str],
    state_specs: list[dict[str, object]],
    clock: str | None,
    reset: dict[str, object] | None,
) -> tuple[dict[str, object], dict[str, object], list[AmbiguityFindingIR], list[str], dict[str, list[object]]]:
    findings: list[AmbiguityFindingIR] = []
    assumptions: list[str] = []
    branch_points: dict[str, list[object]] = {}

    if any(phrase in lower for phrase in ["increment", "decrement", "hold value", "hold its value", "load", "assert output for one cycle"]):
        if not clock:
            findings.append(
                AmbiguityFindingIR(
                    code="clock_inferred",
                    message="sequential behavior was detected but no clock name was explicit; using inferred clock name clk",
                    severity="warning",
                    inferred_value="clk",
                )
            )
            assumptions.append("sequential behavior requires a clock; inferred clock name clk")
            clock = "clk"
            branch_points["clock"] = ["clk"]

    process_result = _infer_process_from_text(lower, input_names, output_names, state_specs, clock, reset)
    if process_result is not None:
        behavior, verification = process_result
        return behavior, verification, findings, assumptions, branch_points

    findings.append(
        AmbiguityFindingIR(
            code="behavior_unparsed",
            message="the text spec did not map cleanly into supported sequential or combinational rules",
            severity="error",
        )
    )
    return {"processes": []}, {"enabled": True, "level": "smoke", "checks": ["generated compile/smoke validation"]}, findings, assumptions, branch_points


def _infer_process_from_text(
    lower: str,
    input_names: set[str],
    output_names: set[str],
    state_specs: list[dict[str, object]],
    clock: str | None,
    reset: dict[str, object] | None,
) -> tuple[dict[str, object], dict[str, object]] | None:
    target = next(iter(state_specs), None)
    if target is None:
        first_output = next(iter(output_names), None)
        if first_output:
            target = {"name": first_output, "width": 1, "reset": 0}
            state_specs.append(target)
    if target is None:
        return None

    target_name = str(target["name"])
    reset_body = [{"assign": {"target": target_name, "expr": "0", "blocking": False}}]
    body: list[dict[str, object]] = []

    enable = _first_matching_name(lower, input_names, ["enable", "en", "start", "load", "set"])
    if "increment" in lower:
        hold_expr = target_name
        step = _extract_step(lower)
        then_expr = f"{target_name} + {step}"
        if enable:
            body.append({"assign": {"target": target_name, "expr": hold_expr, "blocking": False}})
            body.append({"if": {"cond": enable, "then": [{"assign": {"target": target_name, "expr": then_expr, "blocking": False}}]}})
        else:
            body.append({"assign": {"target": target_name, "expr": then_expr, "blocking": False}})
        verification = {"enabled": True, "level": "functional", "checks": ["extracted reset", "extracted increment/hold behavior"], "seq_steps": []}
        if reset and reset.get("signal"):
            verification["seq_steps"].append({"name": "reset_assert", "drive": {str(reset["signal"]): 0 if reset.get("active") == "low" else 1, enable or "dummy_enable": 0}, "delay": 1, "expect": {target_name: 0}})
        if enable:
            edge = f"posedge {clock or 'clk'}"
            drive = {enable: 1}
            if reset and reset.get("signal"):
                drive[str(reset["signal"])] = 1 if reset.get("active") == "low" else 0
            verification["seq_steps"].append({"name": "increment_step", "drive": drive, "edge": edge, "expect": {target_name: step}})
            verification["seq_steps"].append({"name": "hold_step", "drive": {enable: 0}, "edge": edge, "expect": {target_name: step}})
        return {"processes": [{"kind": "seq", "body": body, "reset": reset or {}, "reset_body": reset_body}]}, _sanitize_text_tb(verification, input_names)

    if "hold its value" in lower or "hold value" in lower or "latch" in lower or "assert" in lower:
        trigger = _first_matching_name(lower, input_names, ["set", "set_pulse", "trigger", "in_valid", "valid", "start"])
        if trigger:
            body.append({"assign": {"target": target_name, "expr": target_name, "blocking": False}})
            body.append({"if": {"cond": trigger, "then": [{"assign": {"target": target_name, "expr": "1", "blocking": False}}]}})
            verification = {"enabled": True, "level": "functional", "checks": ["extracted reset", "extracted set/hold behavior"], "seq_steps": []}
            if reset and reset.get("signal"):
                verification["seq_steps"].append({"name": "reset_assert", "drive": {str(reset["signal"]): 0 if reset.get("active") == "low" else 1, trigger: 0}, "delay": 1, "expect": {target_name: 0}})
            edge = f"posedge {clock or 'clk'}"
            verification["seq_steps"].append({"name": "set_state", "drive": {trigger: 1}, "edge": edge, "expect": {target_name: 1}})
            verification["seq_steps"].append({"name": "hold_state", "drive": {trigger: 0}, "edge": edge, "expect": {target_name: 1}})
            return {"processes": [{"kind": "seq", "body": body, "reset": reset or {}, "reset_body": reset_body}]}, _sanitize_text_tb(verification, input_names)

    if "load" in lower and enable:
        data_name = _first_other_input(input_names, {enable})
        if data_name:
            body.append({"assign": {"target": target_name, "expr": target_name, "blocking": False}})
            body.append({"if": {"cond": enable, "then": [{"assign": {"target": target_name, "expr": data_name, "blocking": False}}]}})
            verification = {"enabled": True, "level": "functional", "checks": ["extracted reset", "extracted load behavior"], "seq_steps": []}
            if reset and reset.get("signal"):
                verification["seq_steps"].append({"name": "reset_assert", "drive": {str(reset["signal"]): 0 if reset.get("active") == "low" else 1, enable: 0, data_name: 0}, "delay": 1, "expect": {target_name: 0}})
            verification["seq_steps"].append({"name": "load_data", "drive": {enable: 1, data_name: 1}, "edge": f"posedge {clock or 'clk'}", "expect": {target_name: 1}})
            return {"processes": [{"kind": "seq", "body": body, "reset": reset or {}, "reset_body": reset_body}]}, _sanitize_text_tb(verification, input_names)

    return None


def _first_matching_name(text: str, names: set[str], preferred_fragments: list[str]) -> str | None:
    ordered = sorted(names, key=lambda item: (len(item), item))
    for fragment in preferred_fragments:
        for name in ordered:
            if fragment in name.lower() and re.search(rf"\b{re.escape(name.lower())}\b", text):
                return name
    for name in ordered:
        if re.search(rf"\b{re.escape(name.lower())}\b", text):
            return name
    return None


def _first_other_input(names: set[str], excluded: set[str]) -> str | None:
    for name in sorted(names):
        if name not in excluded and name not in {"clk", "clock", "rst", "rst_n", "reset", "reset_n"}:
            return name
    return None


def _extract_step(text: str) -> int:
    match = re.search(r"increment(?:s)?(?: by)?\s+(\d+)", text, flags=re.IGNORECASE)
    return int(match.group(1)) if match else 1


def _behavior_summary(behavior: dict[str, object]) -> list[str]:
    summaries: list[str] = []
    if "processes" in behavior:
        processes = behavior.get("processes", [])
        if isinstance(processes, list):
            summaries.append(f"normalized {len(processes)} process(es)")
    for key in ["counter", "register", "shift_register", "fsm", "operations", "assignments"]:
        if behavior.get(key):
            summaries.append(f"contains {key}")
    return summaries


def _generate_text_candidates(
    base_document: dict[str, object],
    extracted: dict[str, object],
    assumptions: list[str],
    findings: list[AmbiguityFindingIR],
    branch_points: dict[str, list[object]],
) -> list[NormalizedCandidateIR]:
    base_candidate = NormalizedCandidateIR(
        candidate_id="cand_1",
        title="text_normalized_primary",
        source_type="text",
        document=base_document,
        extracted_semantics=extracted,
        assumptions=list(assumptions),
        ambiguities=list(findings),
        unsupported=[item.message for item in findings if item.severity == "error"],
        internal_checks=_structured_internal_checks(base_document),
        internal_score=max(0.0, _structured_score(base_document) - 0.1 * len(findings)),
    )
    candidates = [base_candidate]

    timing = base_document.get("timing", {}) if isinstance(base_document.get("timing"), dict) else {}
    reset = timing.get("reset") if isinstance(timing.get("reset"), dict) else None
    if (
        reset
        and isinstance(reset, dict)
        and not any(item.code == "behavior_unparsed" for item in findings)
        and not bool(reset.get("polarity_explicit"))
    ):
        alt = copy.deepcopy(base_document)
        alt_reset = alt.setdefault("timing", {}).setdefault("reset", {})
        alt_reset["active"] = "high" if reset.get("active") == "low" else "low"
        candidates.append(
            NormalizedCandidateIR(
                candidate_id="cand_2",
                title="text_alternate_reset_polarity",
                source_type="text",
                document=alt,
                extracted_semantics={**extracted, "alternate_reset_active": alt_reset["active"]},
                assumptions=list(assumptions) + ["alternate candidate flips reset polarity because the prose could be read ambiguously"],
                ambiguities=list(findings)
                + [
                    AmbiguityFindingIR(
                        code="alternate_reset_candidate",
                        message="generated alternate candidate with opposite reset polarity for ambiguous prose",
                        severity="warning",
                        inferred_value=str(alt_reset["active"]),
                    )
                ],
                unsupported=[item.message for item in findings if item.severity == "error"],
                internal_checks=_structured_internal_checks(alt),
                internal_score=max(0.0, _structured_score(alt) - 0.3 - 0.1 * len(findings)),
            )
        )
    return candidates


def _sanitize_text_tb(tb: dict[str, object], input_names: set[str]) -> dict[str, object]:
    seq_steps = tb.get("seq_steps", [])
    if not isinstance(seq_steps, list):
        return tb
    filtered_steps: list[dict[str, object]] = []
    for step in seq_steps:
        if not isinstance(step, dict):
            continue
        filtered = dict(step)
        drive = filtered.get("drive", {})
        if isinstance(drive, dict):
            filtered["drive"] = {name: value for name, value in drive.items() if name in input_names}
        filtered_steps.append(filtered)
    tb["seq_steps"] = filtered_steps
    return tb
