import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


@dataclass
class ParsedInput:
    tokens: list[str] = field(default_factory=list)
    stdout_redirect: str | None = None
    stderr_redirect: str | None = None
    stdout_append: bool = False
    stderr_append: bool = False

    @property
    def command(self) -> str:
        return self.tokens[0] if len(self.tokens) > 0 else ""

    @property
    def args(self) -> list[str]:
        return self.tokens[1:] if len(self.tokens) > 1 else []

    @property
    def is_background(self) -> bool:
        return self.tokens[-1] == "&" if len(self.tokens) > 0 else False


@dataclass
class Result:
    value: Optional[str] = None
    error: Optional[str] = None
    interrupt: Optional[bool] = False


class JobOrder(Enum):
    MOST_RECENT = auto()
    PREVIOUS_MOST_RECENT = auto()
    OTHER = auto()


@dataclass
class ProcessInfo:
    program: subprocess.Popen
    parsed_input: ParsedInput


class CommandType(Enum):
    BUILTIN = auto()
    EXECUTABLE = auto()
    INVALID = auto()
