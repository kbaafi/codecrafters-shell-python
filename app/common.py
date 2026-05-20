import os
from typing import Union

PROMPT = "$ "


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
    quote_char = None
    escaped = False

    for ch in input_str:
        if ch in ("'", '"') and quote_char is None:
            quote_char = ch
        elif ch == quote_char:
            quote_char = None
        elif ch == " " and quote_char is None:
            if current:
                tokens.append("".join(current))
                current = []
        elif ch == "\\":
            escaped = True
            if current:
                tokens.append("".join(current))
                current = []
        elif escaped:
            current.append(ch)
            escaped = False
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens
