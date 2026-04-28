from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Line:
    indent: int
    text: str


def parse_yaml_like(text: str) -> object:
    lines = _preprocess(text)
    if not lines:
        return {}
    value, index = _parse_block(lines, 0, lines[0].indent)
    if index != len(lines):
        raise ValueError("Could not parse complete YAML document")
    return value


def _preprocess(text: str) -> list[Line]:
    lines: list[Line] = []
    for raw in text.splitlines():
        stripped = _strip_inline_comment(raw.rstrip())
        if not stripped.strip():
            continue
        if stripped.lstrip().startswith("#"):
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError("YAML indentation must use multiples of two spaces")
        lines.append(Line(indent=indent, text=stripped.lstrip()))
    return lines


def _parse_block(lines: list[Line], index: int, indent: int) -> tuple[object, int]:
    if index >= len(lines):
        return {}, index
    if lines[index].text.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_list(lines: list[Line], index: int, indent: int) -> tuple[list[object], int]:
    items: list[object] = []
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent != indent or not line.text.startswith("- "):
            break
        payload = line.text[2:].strip()
        index += 1
        if payload == "":
            item, index = _parse_block(lines, index, indent + 2)
            items.append(item)
            continue
        if _looks_like_mapping(payload):
            key, value = _split_key_value(payload)
            item: dict[str, object] = {}
            if _is_block_scalar_token(value):
                nested, index = _parse_block_scalar(lines, index, indent + 2, folded=value.startswith(">"))
                item[key] = nested
            elif value == "":
                nested, index = _parse_block(lines, index, indent + 2)
                item[key] = nested
            else:
                item[key] = _parse_scalar(value)
            while index < len(lines) and lines[index].indent == indent + 2 and not lines[index].text.startswith("- "):
                sub_key, sub_value = _split_key_value(lines[index].text)
                index += 1
                if _is_block_scalar_token(sub_value):
                    nested, index = _parse_block_scalar(lines, index, indent + 4, folded=sub_value.startswith(">"))
                    item[sub_key] = nested
                elif sub_value == "":
                    nested, index = _parse_block(lines, index, indent + 4)
                    item[sub_key] = nested
                else:
                    item[sub_key] = _parse_scalar(sub_value)
            items.append(item)
            continue
        items.append(_parse_scalar(payload))
    return items, index


def _parse_map(lines: list[Line], index: int, indent: int) -> tuple[dict[str, object], int]:
    mapping: dict[str, object] = {}
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent != indent:
            raise ValueError("Invalid indentation inside YAML map")
        key, value = _split_key_value(line.text)
        index += 1
        if _is_block_scalar_token(value):
            nested, index = _parse_block_scalar(lines, index, indent + 2, folded=value.startswith(">"))
            mapping[key] = nested
        elif value == "":
            nested, index = _parse_block(lines, index, indent + 2)
            mapping[key] = nested
        else:
            mapping[key] = _parse_scalar(value)
    return mapping, index


def _looks_like_mapping(payload: str) -> bool:
    if payload.startswith("{") and payload.endswith("}"):
        return False
    if ":" not in payload:
        return False
    key, _, remainder = payload.partition(":")
    key = key.strip()
    if not key:
        return False
    if not key.replace("_", "").replace("-", "").isalnum():
        return False
    return remainder == "" or remainder.startswith(" ")


def _split_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"Expected key:value pair, got: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar(value: str) -> object:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        return _parse_inline_list(value[1:-1])
    if value.startswith("{") and value.endswith("}"):
        return _parse_inline_map(value[1:-1])
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    return value


def _parse_inline_list(body: str) -> list[object]:
    parts = _split_inline(body)
    return [_parse_scalar(part.strip()) for part in parts if part.strip()]


def _parse_inline_map(body: str) -> dict[str, object]:
    mapping: dict[str, object] = {}
    for part in _split_inline(body):
        if not part.strip():
            continue
        key, value = _split_key_value(part)
        mapping[key] = _parse_scalar(value)
    return mapping


def _split_inline(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char in {"[", "{"}:
            depth += 1
        elif char in {"]", "}"}:
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current).strip())
    return parts


def _is_block_scalar_token(value: str) -> bool:
    return value in {"|", ">", "|-", ">-"}


def _parse_block_scalar(lines: list[Line], index: int, indent: int, folded: bool) -> tuple[str, int]:
    collected: list[str] = []
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        content = line.text
        if line.indent > indent:
            content = " " * (line.indent - indent) + content
        collected.append(content)
        index += 1
    if folded:
        return " ".join(part.strip() for part in collected).strip(), index
    return "\n".join(collected), index


def _strip_inline_comment(text: str) -> str:
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for idx, char in enumerate(text):
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'} and (idx == 0 or text[idx - 1].isspace() or text[idx - 1] in "{[:,"):
            quote = char
            current.append(char)
            continue
        if char in {"[", "{"}:
            depth += 1
        elif char in {"]", "}"} and depth > 0:
            depth -= 1
        if char == "#" and depth == 0 and (idx == 0 or text[idx - 1].isspace()):
            break
        current.append(char)
    return "".join(current).rstrip()
