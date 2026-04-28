from __future__ import annotations

from pathlib import Path

from spec2rtl.yaml_like import parse_yaml_like


def load_spec_document(spec_path: Path, top_override: str | None = None) -> dict[str, object]:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    text = spec_path.read_text(encoding="utf-8").strip()
    suffix = spec_path.suffix.lower()
    if suffix not in {".yaml", ".yml"}:
        raise ValueError(f"Unsupported spec format: {spec_path}. Only .yaml/.yml specs are accepted.")
    document = parse_yaml_like(text)
    if not isinstance(document, dict):
        raise ValueError("Top-level YAML document must be a mapping")
    document = _normalize_document(document)
    return _apply_top_override(document, top_override)


def _apply_top_override(document: dict[str, object], top_override: str | None) -> dict[str, object]:
    if not top_override:
        return document
    module = document.setdefault("module", {})
    if not isinstance(module, dict):
        raise ValueError("module section must be a mapping")
    module["name"] = top_override
    return document


def _normalize_document(document: dict[str, object]) -> dict[str, object]:
    if "module" in document and "ports" in document:
        return document
    if len(document) != 1:
        return document
    top_name, payload = next(iter(document.items()))
    if not isinstance(payload, dict):
        return document
    return _normalize_benchmark_spec(str(top_name), payload)


def _normalize_benchmark_spec(top_name: str, payload: dict[str, object]) -> dict[str, object]:
    ports = payload.get("ports", [])
    normalized_ports = [_normalize_port(item) for item in ports] if isinstance(ports, list) else []
    timing = _infer_timing(normalized_ports)
    verification_tb = {"enabled": True, "level": "smoke", "checks": ["generated compile/smoke validation"]}
    notes = []
    description = payload.get("description")
    if description is not None:
        notes.append(str(description))
    flow = _normalize_flow_hints(payload)
    return {
        "module": {"name": top_name},
        "ports": normalized_ports,
        "timing": timing,
        "design": {"kind": "generic", "notes": notes, "behavior": {}},
        "verification": {"tb": verification_tb},
        "flow": flow,
    }


def _normalize_port(entry: object) -> dict[str, object]:
    if not isinstance(entry, dict):
        raise ValueError("port entry must be a mapping")
    return {
        "name": str(entry["name"]),
        "dir": str(entry.get("dir", entry.get("direction", "input"))),
        "width": _infer_width(entry),
        "kind": str(entry.get("kind", "wire")),
        "description": str(entry.get("description", "")),
    }


def _infer_width(entry: dict[str, object]) -> int:
    width = entry.get("width")
    if isinstance(width, int):
        return max(1, width)
    if isinstance(width, str) and width.isdigit():
        return max(1, int(width))
    port_type = str(entry.get("type", ""))
    if "[" in port_type and ":" in port_type and "]" in port_type:
        body = port_type[port_type.find("[") + 1 : port_type.find("]")]
        msb, _, lsb = body.partition(":")
        if msb.strip().isdigit() and lsb.strip().isdigit():
            return abs(int(msb) - int(lsb)) + 1
    return 1


def _infer_timing(ports: list[dict[str, object]]) -> dict[str, object]:
    inputs = [str(port["name"]) for port in ports if str(port.get("dir")) == "input"]
    clock = next((name for name in inputs if name.lower() in {"clk", "clock"}), None)
    reset_name = next((name for name in inputs if name.lower() in {"reset", "rst", "rst_n", "reset_n"}), None)
    timing: dict[str, object] = {}
    if clock:
        timing["clock"] = clock
    if reset_name:
        timing["reset"] = {
            "signal": reset_name,
            "active": "low" if reset_name.lower().endswith("_n") else "high",
            "mode": "async" if reset_name.lower().endswith("_n") else "sync",
        }
    return timing


def _normalize_flow_hints(payload: dict[str, object]) -> dict[str, object]:
    flow: dict[str, object] = {}
    tech_node = payload.get("tech_node") or payload.get("technology")
    if tech_node is not None:
        flow["tech_node"] = str(tech_node)
        flow["platform"] = _infer_platform(str(tech_node))
    clock_period = payload.get("clock_period")
    if clock_period is not None:
        flow["clock_period"] = str(clock_period)
    if payload.get("module_signature") is not None:
        flow["module_signature"] = str(payload.get("module_signature"))
    return flow


def _infer_platform(tech_node: str) -> str:
    lowered = tech_node.lower()
    if "130" in lowered or "sky" in lowered:
        return "sky130hd"
    if "45" in lowered:
        return "nangate45"
    return lowered.replace(" ", "_")
