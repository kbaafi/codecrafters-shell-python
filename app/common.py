import os
from typing import Union
from enum import Enum


PROMPT = "$ "


class CURSOR_STATE(Enum):
    IN_QUOTE = "IN_QUOTE"
    OUT_QUOTE = "OUT_QUOTE"
    ESCAPE = "ESCAPE"


def is_executable_command(command) -> tuple[bool, Union[str, None]]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)

    for dir in dirs:
        full_path = os.path.join(dir, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return True, full_path
    return False, None


# def tokenize_args(input_str: str) -> list[str]:
#     tokens = []
#     current = []
#     quote_char = None
#     escaped = False
#     in_quote = False
#     cusor_state: CURSOR_STATE = CURSOR_STATE.OUT_QUOTE

#     for ch in input_str:
#         if ch in ("'", '"') and quote_char is None:
#             quote_char = ch
#             cusor_state = CURSOR_STATE.IN_QUOTE
#         elif cusor_state==CURSOR_STATE.IN_QUOTE and ch == quote_char:
#             quote_char = None
#             cusor_state = CURSOR_STATE.OUT_QUOTE
#         else:

        
#         if in_quote:
#             if ch = qu
#             current.append(ch)
#         else:
#             if ch == "\\": 
        

#         elif ch == " " and quote_char is None:
#             if current:
#                 tokens.append("".join(current))
#                 current = []
#         elif ch == "\\":
#             escaped = True
#             if current:
#                 tokens.append("".join(current))
#             current = []
#         elif escaped:
#             current.append(ch)
#             escaped = False
#             tokens.append("".join(current))
#             current = []
#         else:
#             current.append(ch)
#     if current:
#         tokens.append("".join(current))
#     return tokens


def tokenize_args(input_str: str) -> list[str]:
    tokens = []
    current = []
    state = CURSOR_STATE.OUT_QUOTE
    quote_char = None

    for ch in input_str:
        match state:
            case CURSOR_STATE.OUT_QUOTE:
                if ch in ("'", '"'):
                    quote_char = ch
                    state = CURSOR_STATE.IN_QUOTE
                elif ch == "\\":
                    state = CURSOR_STATE.ESCAPE
                # elif ch == " ":
                #     if current:
                #         tokens.append("".join(current))
                #         current = []
                else:
                    current.append(ch)

            case CURSOR_STATE.IN_QUOTE:
                if ch == quote_char:
                    quote_char = None
                    state = CURSOR_STATE.OUT_QUOTE
                else:
                    current.append(ch)

            case CURSOR_STATE.ESCAPE:
                if ch == " ":
                    if current:
                        tokens.append("".join(current))
                        tokens.append(ch)
                    else:
                        tokens.append(ch)
                    current = []
                else:
                    tokens.append(ch)
                    current = []
                state = CURSOR_STATE.OUT_QUOTE
    if current:
        tokens.append("".join(current))

    return tokens
