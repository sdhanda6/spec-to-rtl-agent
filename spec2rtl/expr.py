from __future__ import annotations

import re
from dataclasses import dataclass

from spec2rtl.ir import (
    BinaryExprIR,
    ConcatExprIR,
    ExprIR,
    IndexExprIR,
    LiteralExprIR,
    RefExprIR,
    SliceExprIR,
    TernaryExprIR,
    UnaryExprIR,
)


TOKEN_RE = re.compile(
    r"""
    \s*(
        <=|>=|==|!=|
        [(){}\[\],?:~+\-*/&|^<>]|
        \d+'[bdhBDH][0-9a-fA-F_xXzZ]+|
        \d+|
        [A-Za-z_]\w*
    )
    """,
    re.VERBOSE,
)


PRECEDENCE = {
    "|": 10,
    "^": 20,
    "&": 30,
    "==": 40,
    "!=": 40,
    "<": 50,
    "<=": 50,
    ">": 50,
    ">=": 50,
    "+": 60,
    "-": 60,
}


@dataclass
class TokenStream:
    tokens: list[str]
    index: int = 0

    def peek(self) -> str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def pop(self) -> str:
        if self.index >= len(self.tokens):
            raise ValueError("Unexpected end of expression")
        value = self.tokens[self.index]
        self.index += 1
        return value

    def expect(self, value: str) -> None:
        token = self.pop()
        if token != value:
            raise ValueError(f"Expected {value}, got {token}")


def parse_expr(value: object) -> ExprIR:
    if isinstance(value, dict):
        return parse_expr_mapping(value)
    if isinstance(value, int):
        return LiteralExprIR(kind="literal", value=str(value))
    text = str(value).strip()
    tokens = tokenize(text)
    stream = TokenStream(tokens)
    expr = parse_ternary(stream)
    if stream.peek() is not None:
        raise ValueError(f"Unexpected token in expression: {stream.peek()}")
    return expr


def parse_expr_mapping(mapping: dict[str, object]) -> ExprIR:
    if "ref" in mapping:
        return RefExprIR(kind="ref", name=str(mapping["ref"]))
    if "literal" in mapping:
        return LiteralExprIR(kind="literal", value=str(mapping["literal"]))
    if "not" in mapping:
        return UnaryExprIR(kind="unary", op="~", operand=parse_expr(mapping["not"]))
    if "concat" in mapping:
        parts = [parse_expr(item) for item in _expect_list(mapping["concat"])]
        return ConcatExprIR(kind="concat", parts=parts)
    if "slice" in mapping:
        item = mapping["slice"]
        if not isinstance(item, dict):
            raise ValueError("slice expression must be a mapping")
        return SliceExprIR(
            kind="slice",
            target=parse_expr(item["target"]),
            msb=int(item["msb"]),
            lsb=int(item.get("lsb", item["msb"])),
        )
    if "ternary" in mapping:
        item = mapping["ternary"]
        if not isinstance(item, dict):
            raise ValueError("ternary expression must be a mapping")
        return TernaryExprIR(
            kind="ternary",
            condition=parse_expr(item["cond"]),
            when_true=parse_expr(item["true"]),
            when_false=parse_expr(item["false"]),
        )
    if "op" in mapping:
        op = str(mapping["op"])
        operands = _expect_list(mapping.get("operands", []))
        if len(operands) == 1:
            return UnaryExprIR(kind="unary", op=op, operand=parse_expr(operands[0]))
        if len(operands) == 2:
            return BinaryExprIR(kind="binary", op=op, left=parse_expr(operands[0]), right=parse_expr(operands[1]))
    raise ValueError(f"Unsupported expression mapping: {mapping}")


def render_expr(expr: ExprIR) -> str:
    if isinstance(expr, LiteralExprIR):
        return expr.value
    if isinstance(expr, RefExprIR):
        return expr.name
    if isinstance(expr, UnaryExprIR):
        return f"{expr.op}{parenthesize(expr.operand)}"
    if isinstance(expr, BinaryExprIR):
        return f"{parenthesize(expr.left)} {expr.op} {parenthesize(expr.right)}"
    if isinstance(expr, TernaryExprIR):
        return f"{parenthesize(expr.condition)} ? {render_expr(expr.when_true)} : {render_expr(expr.when_false)}"
    if isinstance(expr, ConcatExprIR):
        return "{" + ", ".join(render_expr(item) for item in expr.parts) + "}"
    if isinstance(expr, SliceExprIR):
        if expr.msb == expr.lsb:
            return f"{render_expr(expr.target)}[{expr.msb}]"
        return f"{render_expr(expr.target)}[{expr.msb}:{expr.lsb}]"
    if isinstance(expr, IndexExprIR):
        return f"{render_expr(expr.target)}[{expr.index}]"
    raise TypeError(f"Unknown expression type: {type(expr).__name__}")


def parenthesize(expr: ExprIR) -> str:
    if isinstance(expr, (LiteralExprIR, RefExprIR, SliceExprIR, IndexExprIR)):
        return render_expr(expr)
    return f"({render_expr(expr)})"


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    pos = 0
    while pos < len(text):
        match = TOKEN_RE.match(text, pos)
        if not match:
            raise ValueError(f"Could not tokenize expression near: {text[pos:]}")
        token = match.group(1)
        tokens.append(token)
        pos = match.end()
    return tokens


def parse_ternary(stream: TokenStream) -> ExprIR:
    condition = parse_binary(stream, 0)
    if stream.peek() == "?":
        stream.pop()
        when_true = parse_ternary(stream)
        stream.expect(":")
        when_false = parse_ternary(stream)
        return TernaryExprIR(kind="ternary", condition=condition, when_true=when_true, when_false=when_false)
    return condition


def parse_binary(stream: TokenStream, min_prec: int) -> ExprIR:
    left = parse_unary(stream)
    while True:
        op = stream.peek()
        if op is None or op not in PRECEDENCE or PRECEDENCE[op] < min_prec:
            break
        prec = PRECEDENCE[op]
        stream.pop()
        right = parse_binary(stream, prec + 1)
        left = BinaryExprIR(kind="binary", op=op, left=left, right=right)
    return left


def parse_unary(stream: TokenStream) -> ExprIR:
    token = stream.peek()
    if token in {"~", "-"}:
        op = stream.pop()
        return UnaryExprIR(kind="unary", op=op, operand=parse_unary(stream))
    return parse_postfix(stream)


def parse_postfix(stream: TokenStream) -> ExprIR:
    expr = parse_primary(stream)
    while stream.peek() == "[":
        stream.pop()
        first = stream.pop()
        if stream.peek() == ":":
            stream.pop()
            second = stream.pop()
            stream.expect("]")
            expr = SliceExprIR(kind="slice", target=expr, msb=int(first), lsb=int(second))
        else:
            stream.expect("]")
            expr = IndexExprIR(kind="index", target=expr, index=int(first))
    return expr


def parse_primary(stream: TokenStream) -> ExprIR:
    token = stream.pop()
    if token == "(":
        expr = parse_ternary(stream)
        stream.expect(")")
        return expr
    if token == "{":
        parts: list[ExprIR] = []
        while stream.peek() != "}":
            parts.append(parse_ternary(stream))
            if stream.peek() == ",":
                stream.pop()
        stream.expect("}")
        return ConcatExprIR(kind="concat", parts=parts)
    if token[0].isdigit():
        return LiteralExprIR(kind="literal", value=token)
    return RefExprIR(kind="ref", name=token)


def _expect_list(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Expected a list")
    return value
