import os
from typing import Union
from enum import Enum, auto


PROMPT = "$ "


class CURSOR_STATE(Enum):
    IN_QUOTE = auto()
    OUT_QUOTE = auto()
    ESCAPE = auto()
    IN_QUOTE_ESCAPE = auto()


def is_executable_command(command) -> tuple[bool, Union[str, None]]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)

    for dir in dirs:
        full_path = os.path.join(dir, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return True, full_path
    return False, None


def tokenize_args(input_str: str) -> list[str]:
    tokens = []
    current = []
    state = CURSOR_STATE.OUT_QUOTE
    quote_char = None

    for ch in input_str:
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
    if current:
        tokens.append("".join(current))

    return tokens
