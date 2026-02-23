#!/usr/bin/env python3
"""HackScript: a tiny scripting language for HackUSU.

Features:
- Variables via `let name = expression;`
- Printing via `print expression;`
- `if (...) { ... } else { ... }`
- `while (...) { ... }`
- Arithmetic, comparisons, booleans, strings, logical operators
- Line comments with `//`
"""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any


class HackScriptError(Exception):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    lexeme: str
    literal: Any
    line: int


KEYWORDS = {
    "let": "LET",
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "true": "TRUE",
    "false": "FALSE",
    "nil": "NIL",
    "and": "AND",
    "or": "OR",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens

    def _scan_token(self) -> None:
        c = self._advance()
        singles = {
            "(": "LEFT_PAREN",
            ")": "RIGHT_PAREN",
            "{": "LEFT_BRACE",
            "}": "RIGHT_BRACE",
            ",": "COMMA",
            ".": "DOT",
            ";": "SEMICOLON",
            "+": "PLUS",
            "-": "MINUS",
            "*": "STAR",
            "%": "PERCENT",
        }

        if c in singles:
            self._add_token(singles[c])
        elif c == "!":
            self._add_token("BANG_EQUAL" if self._match("=") else "BANG")
        elif c == "=":
            self._add_token("EQUAL_EQUAL" if self._match("=") else "EQUAL")
        elif c == "<":
            self._add_token("LESS_EQUAL" if self._match("=") else "LESS")
        elif c == ">":
            self._add_token("GREATER_EQUAL" if self._match("=") else "GREATER")
        elif c == "/":
            if self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            else:
                self._add_token("SLASH")
        elif c in (" ", "\r", "\t"):
            return
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self._string()
        elif c.isdigit():
            self._number()
        elif c.isalpha() or c == "_":
            self._identifier()
        else:
            raise HackScriptError(f"[line {self.line}] Unexpected character: {c}")

    def _identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[self.start : self.current]
        kind = KEYWORDS.get(text, "IDENTIFIER")
        self._add_token(kind)

    def _number(self) -> None:
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        lexeme = self.source[self.start : self.current]
        self._add_token("NUMBER", float(lexeme))

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
            self._advance()

        if self._is_at_end():
            raise HackScriptError(f"[line {self.line}] Unterminated string.")

        self._advance()  # closing quote
        value = self.source[self.start + 1 : self.current - 1]
        self._add_token("STRING", value)

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def _add_token(self, kind: str, literal: Any = None) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(kind, text, literal, self.line))


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[dict[str, Any]]:
        statements: list[dict[str, Any]] = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return statements

    def _declaration(self) -> dict[str, Any]:
        if self._match("LET"):
            return self._let_declaration()
        return self._statement()

    def _let_declaration(self) -> dict[str, Any]:
        name = self._consume("IDENTIFIER", "Expected variable name.")
        self._consume("EQUAL", "Expected '=' after variable name.")
        initializer = self._expression()
        self._consume("SEMICOLON", "Expected ';' after variable declaration.")
        return {"type": "let", "name": name.lexeme, "value": initializer}

    def _statement(self) -> dict[str, Any]:
        if self._match("PRINT"):
            expr = self._expression()
            self._consume("SEMICOLON", "Expected ';' after print value.")
            return {"type": "print", "expr": expr}
        if self._match("IF"):
            return self._if_statement()
        if self._match("WHILE"):
            return self._while_statement()
        if self._match("LEFT_BRACE"):
            return {"type": "block", "statements": self._block()}
        expr = self._expression()
        self._consume("SEMICOLON", "Expected ';' after expression.")
        return {"type": "expr_stmt", "expr": expr}

    def _if_statement(self) -> dict[str, Any]:
        self._consume("LEFT_PAREN", "Expected '(' after if.")
        condition = self._expression()
        self._consume("RIGHT_PAREN", "Expected ')' after if condition.")
        then_branch = self._statement()
        else_branch = self._statement() if self._match("ELSE") else None
        return {
            "type": "if",
            "condition": condition,
            "then": then_branch,
            "else": else_branch,
        }

    def _while_statement(self) -> dict[str, Any]:
        self._consume("LEFT_PAREN", "Expected '(' after while.")
        condition = self._expression()
        self._consume("RIGHT_PAREN", "Expected ')' after while condition.")
        body = self._statement()
        return {"type": "while", "condition": condition, "body": body}

    def _block(self) -> list[dict[str, Any]]:
        statements: list[dict[str, Any]] = []
        while not self._check("RIGHT_BRACE") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume("RIGHT_BRACE", "Expected '}' after block.")
        return statements

    def _expression(self) -> dict[str, Any]:
        return self._assignment()

    def _assignment(self) -> dict[str, Any]:
        expr = self._or()
        if self._match("EQUAL"):
            equals = self._previous()
            value = self._assignment()
            if expr["type"] == "variable":
                return {"type": "assign", "name": expr["name"], "value": value}
            raise HackScriptError(f"[line {equals.line}] Invalid assignment target.")
        return expr

    def _or(self) -> dict[str, Any]:
        expr = self._and()
        while self._match("OR"):
            op = self._previous().kind
            right = self._and()
            expr = {"type": "logical", "left": expr, "op": op, "right": right}
        return expr

    def _and(self) -> dict[str, Any]:
        expr = self._equality()
        while self._match("AND"):
            op = self._previous().kind
            right = self._equality()
            expr = {"type": "logical", "left": expr, "op": op, "right": right}
        return expr

    def _equality(self) -> dict[str, Any]:
        expr = self._comparison()
        while self._match("BANG_EQUAL", "EQUAL_EQUAL"):
            op = self._previous().kind
            right = self._comparison()
            expr = {"type": "binary", "left": expr, "op": op, "right": right}
        return expr

    def _comparison(self) -> dict[str, Any]:
        expr = self._term()
        while self._match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            op = self._previous().kind
            right = self._term()
            expr = {"type": "binary", "left": expr, "op": op, "right": right}
        return expr

    def _term(self) -> dict[str, Any]:
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            op = self._previous().kind
            right = self._factor()
            expr = {"type": "binary", "left": expr, "op": op, "right": right}
        return expr

    def _factor(self) -> dict[str, Any]:
        expr = self._unary()
        while self._match("STAR", "SLASH", "PERCENT"):
            op = self._previous().kind
            right = self._unary()
            expr = {"type": "binary", "left": expr, "op": op, "right": right}
        return expr

    def _unary(self) -> dict[str, Any]:
        if self._match("BANG", "MINUS"):
            op = self._previous().kind
            right = self._unary()
            return {"type": "unary", "op": op, "right": right}
        return self._primary()

    def _primary(self) -> dict[str, Any]:
        if self._match("FALSE"):
            return {"type": "literal", "value": False}
        if self._match("TRUE"):
            return {"type": "literal", "value": True}
        if self._match("NIL"):
            return {"type": "literal", "value": None}
        if self._match("NUMBER", "STRING"):
            return {"type": "literal", "value": self._previous().literal}
        if self._match("IDENTIFIER"):
            return {"type": "variable", "name": self._previous().lexeme}
        if self._match("LEFT_PAREN"):
            expr = self._expression()
            self._consume("RIGHT_PAREN", "Expected ')' after expression.")
            return {"type": "group", "expr": expr}
        token = self._peek()
        raise HackScriptError(f"[line {token.line}] Expected expression.")

    def _match(self, *kinds: str) -> bool:
        for kind in kinds:
            if self._check(kind):
                self._advance()
                return True
        return False

    def _consume(self, kind: str, message: str) -> Token:
        if self._check(kind):
            return self._advance()
        token = self._peek()
        raise HackScriptError(f"[line {token.line}] {message}")

    def _check(self, kind: str) -> bool:
        return not self._is_at_end() and self._peek().kind == kind

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().kind == "EOF"

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]


class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self.parent = parent
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise HackScriptError(f"Undefined variable '{name}'.")

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise HackScriptError(f"Undefined variable '{name}'.")


class Interpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, statements: list[dict[str, Any]]) -> None:
        for stmt in statements:
            self._execute(stmt)

    def _execute(self, stmt: dict[str, Any]) -> None:
        stype = stmt["type"]
        if stype == "let":
            self.env.define(stmt["name"], self._eval(stmt["value"]))
        elif stype == "print":
            print(self._stringify(self._eval(stmt["expr"])))
        elif stype == "expr_stmt":
            self._eval(stmt["expr"])
        elif stype == "block":
            self._execute_block(stmt["statements"], Environment(self.env))
        elif stype == "if":
            if self._is_truthy(self._eval(stmt["condition"])):
                self._execute(stmt["then"])
            elif stmt["else"] is not None:
                self._execute(stmt["else"])
        elif stype == "while":
            while self._is_truthy(self._eval(stmt["condition"])):
                self._execute(stmt["body"])
        else:
            raise HackScriptError(f"Unknown statement type: {stype}")

    def _execute_block(self, statements: list[dict[str, Any]], env: Environment) -> None:
        previous = self.env
        try:
            self.env = env
            for stmt in statements:
                self._execute(stmt)
        finally:
            self.env = previous

    def _eval(self, expr: dict[str, Any]) -> Any:
        etype = expr["type"]
        if etype == "literal":
            return expr["value"]
        if etype == "group":
            return self._eval(expr["expr"])
        if etype == "variable":
            return self.env.get(expr["name"])
        if etype == "assign":
            value = self._eval(expr["value"])
            self.env.assign(expr["name"], value)
            return value
        if etype == "unary":
            right = self._eval(expr["right"])
            return self._eval_unary(expr["op"], right)
        if etype == "logical":
            left = self._eval(expr["left"])
            if expr["op"] == "OR":
                return left if self._is_truthy(left) else self._eval(expr["right"])
            return left if not self._is_truthy(left) else self._eval(expr["right"])
        if etype == "binary":
            return self._eval_binary(expr)
        raise HackScriptError(f"Unknown expression type: {etype}")

    def _eval_unary(self, op: str, right: Any) -> Any:
        if op == "MINUS":
            self._ensure_number(right)
            return -float(right)
        if op == "BANG":
            return not self._is_truthy(right)
        raise HackScriptError(f"Unknown unary operator: {op}")

    def _eval_binary(self, expr: dict[str, Any]) -> Any:
        left = self._eval(expr["left"])
        right = self._eval(expr["right"])
        op = expr["op"]

        if op == "PLUS":
            if isinstance(left, str) or isinstance(right, str):
                return f"{self._stringify(left)}{self._stringify(right)}"
            self._ensure_number(left)
            self._ensure_number(right)
            return float(left) + float(right)
        if op == "MINUS":
            self._ensure_number(left)
            self._ensure_number(right)
            return float(left) - float(right)
        if op == "STAR":
            self._ensure_number(left)
            self._ensure_number(right)
            return float(left) * float(right)
        if op == "SLASH":
            self._ensure_number(left)
            self._ensure_number(right)
            if float(right) == 0:
                raise HackScriptError("Division by zero.")
            return float(left) / float(right)
        if op == "PERCENT":
            self._ensure_number(left)
            self._ensure_number(right)
            return float(left) % float(right)
        if op == "GREATER":
            return float(left) > float(right)
        if op == "GREATER_EQUAL":
            return float(left) >= float(right)
        if op == "LESS":
            return float(left) < float(right)
        if op == "LESS_EQUAL":
            return float(left) <= float(right)
        if op == "EQUAL_EQUAL":
            return left == right
        if op == "BANG_EQUAL":
            return left != right

        raise HackScriptError(f"Unknown binary operator: {op}")

    @staticmethod
    def _is_truthy(value: Any) -> bool:
        return value not in (None, False)

    @staticmethod
    def _ensure_number(value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise HackScriptError(f"Expected number but got {type(value).__name__}.")

    @staticmethod
    def _stringify(value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)


def run(source: str) -> None:
    tokens = Lexer(source).scan_tokens()
    statements = Parser(tokens).parse()
    Interpreter().interpret(statements)


def run_file(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        run(source)
        return 0
    except HackScriptError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 1


def repl() -> int:
    print("HackScript REPL. Type `exit` to quit.")
    interpreter = Interpreter()
    while True:
        try:
            line = input("hs> ")
        except EOFError:
            print()
            return 0
        if line.strip() in {"exit", "quit"}:
            return 0
        if not line.strip():
            continue
        try:
            tokens = Lexer(line if line.endswith(";") else f"{line};").scan_tokens()
            statements = Parser(tokens).parse()
            interpreter.interpret(statements)
        except HackScriptError as exc:
            print(f"error: {exc}")


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print("Usage: python hackscript.py [script.hk]", file=sys.stderr)
        return 64
    if len(argv) == 2:
        return run_file(argv[1])
    return repl()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
