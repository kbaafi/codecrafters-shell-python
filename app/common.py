from enum import Enum, auto

from .models import ParsedInput

PROMPT = "$ "


class CURSOR_STATE(Enum):
    IN_QUOTE = auto()
    OUT_QUOTE = auto()
    ESCAPE = auto()
    IN_QUOTE_ESCAPE = auto()


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
        while i < len(s) and s[i] == " ":
            i += 1
        start = i
        while i < len(s) and s[i] != " ":
            i += 1
        return s[start:i], i - 1

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
                elif (
                    ch in ("1", "2")
                    and i + 1 < len(input_str)
                    and input_str[i + 1] == ">"
                ):
                    if current:
                        tokens.append("".join(current))
                        current = []
                    next_ch = input_str[i + 2] if i + 2 < len(input_str) else None
                    append_mode = next_ch == ">"
                    filename, i = (
                        read_word(input_str, i + 3)
                        if append_mode
                        else read_word(input_str, i + 2)
                    )

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
                    next_ch = input_str[i + 1] if i + 1 < len(input_str) else None
                    stdout_append = next_ch == ">"
                    stdout_redirect, i = read_word(
                        input_str, i + 2 if stdout_append else i + 1
                    )
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
        stdout_append=stdout_append,
    )
