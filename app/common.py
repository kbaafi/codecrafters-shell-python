import os
import sys
from typing import Optional
from enum import Enum, auto
from .handlers import Result
from dataclasses import dataclass, field



PROMPT = "$ "


class CURSOR_STATE(Enum):
    IN_QUOTE = auto()
    OUT_QUOTE = auto()
    ESCAPE = auto()
    IN_QUOTE_ESCAPE = auto()


@dataclass
class ParsedInput:
    tokens: list[str] = field(default_factory=list)
    stdout_redirect: str | None = None
    stderr_redirect: str | None = None
    stdout_append: bool = False
    stderr_append: bool = False


def tokenize_user_input(input_str: str) -> ParsedInput:
    tokens = []
    current = []
    stdout_redirect = None
    stderr_redirect = None
    stderr_append = False
    stdout_append = False
    state = CURSOR_STATE.OUT_QUOTE
    quote_char = None

    def read_word(s: str, i: int) -> tuple[str, int]:
        while i < len (s) and s[i] == " ":
            i += 1
        start = i
        while i < len(s) and s[i] != " ":
            i += 1
        return s[start: i], i-1

    i = 0
    while i < len(input_str):
        ch = input_str[i]
        match state:
            case CURSOR_STATE.OUT_QUOTE:
                if ch in ("'", '"') and quote_char is None:
                    quote_char = ch
                    state = CURSOR_STATE.IN_QUOTE
                elif ch == "\\":
                    state = CURSOR_STATE.ESCAPE
                    quote_char = None
                elif ch in ("'", '"') and quote_char in ("'", '"'):
                    quote_char = None
                    state = CURSOR_STATE.OUT_QUOTE
                elif ch == " ":
                    if current:
                        tokens.append("".join(current))
                        current = []
                elif ch in ("1", "2") and i +1 < len(input_str) and input_str[i+1] == ">":
                    if current:
                        tokens.append("".join(current))
                        current = []
                    next_ch = input_str[i+2] if i+2 < len(input_str) else None
                    append_mode = next_ch == ">"
                    filename, i = read_word(input_str, i+3) if append_mode else read_word(input_str, i+2)
            
                    if ch == "1":
                        stdout_redirect = filename
                        stdout_append = append_mode
                    else:
                        stderr_redirect = filename
                        stderr_append = append_mode
                elif ch == ">":
                    if current:
                        tokens.append("".join(current))
                        current = []
                    next_ch = input_str[i+1] if i+1 < len(input_str) else None
                    stdout_append = next_ch == ">"
                    stdout_redirect, i = read_word(input_str, i + 2 if stdout_append else i + 1)
                else:
                    current.append(ch)

            case CURSOR_STATE.IN_QUOTE:
                if ch == quote_char:
                    quote_char = None
                    state = CURSOR_STATE.OUT_QUOTE
                elif quote_char == '"' and ch == "\\":
                    state = CURSOR_STATE.IN_QUOTE_ESCAPE
                else:
                    current.append(ch)

            case CURSOR_STATE.ESCAPE:
                current.append(ch)
                state = CURSOR_STATE.OUT_QUOTE

            case CURSOR_STATE.IN_QUOTE_ESCAPE:
                current.append(ch)
                state = CURSOR_STATE.IN_QUOTE
        i += 1
    if current:
        tokens.append("".join(current))

    return ParsedInput(
        tokens=tokens,
        stdout_redirect=stdout_redirect,
        stderr_redirect=stderr_redirect,
        stderr_append=stderr_append,
        stdout_append=stdout_append
    )


def _to_screen(text: str | None):
    if text:
        sys.stdout.write(text if text.endswith('\n') else text + '\n')

def _to_file(text: str | None, path: str, append: bool):
    with open(path, 'a' if append else 'w') as f:
        if append:
            f.write(f'{text}' or "")
            return
        f.write(text or "")

def output_result(result: Result, parsed_input: ParsedInput):
    if parsed_input.stderr_redirect is not None:
        _to_file(result.error, parsed_input.stderr_redirect, parsed_input.stderr_append)
        _to_screen(result.value)
    elif parsed_input.stdout_redirect is not None:
        _to_file(result.value, parsed_input.stdout_redirect, parsed_input.stdout_append)
        _to_screen(result.error)
    elif result.value:
        _to_screen(result.value)
    elif result.error:
        _to_screen(result.error)


