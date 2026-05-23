import os
import sys
from typing import Union, Optional
from enum import Enum, auto
from .handlers import Result



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


def tokenize_user_input(input_str: str) -> tuple[list[str], str|None, str|None]:
    tokens = []
    current = []
    stdout_redirect = None
    stderr_redirect = None
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
                    filename, i = read_word(input_str, i+2)
                    if ch == "1":
                        stdout_redirect = filename
                    else:
                        stderr_redirect = filename
                elif ch == ">":
                    if current:
                        tokens.append("".join(current))
                        current = []
                    stdout_redirect, i = read_word(input_str, i + 1)
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

    return tokens, stdout_redirect, stderr_redirect


def output_result(result: Result, stdout_redirect: Optional[str], stderr_redirect: Optional[str]):
    if stderr_redirect is not None:
        with open(stderr_redirect, 'w') as file:
            file.write(result.error or "")
        if result.value:
            output = result.value if result.value.endswith('\n') else result.value + '\n'
            sys.stdout.write(output)
    elif stdout_redirect is not None:
        with open(stdout_redirect, 'w') as file:
            file.write(result.value or "")
        if result.error:
            output = result.error if result.error.endswith('\n') else result.error + '\n'
            sys.stdout.write(output)
    elif result.value:
        output = result.value if result.value.endswith('\n') else result.value + '\n'
        sys.stdout.write(output)
        
