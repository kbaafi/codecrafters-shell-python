import os
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


@dataclass
class Result:
    value: Optional[str] = None
    error: Optional[str] = None
    interrupt: Optional[bool] = False


class CommandType(Enum):
    BUILTIN = auto()
    EXECUTABLE = auto()
    INVALID = auto()


@dataclass
class ShellContext:
    built_ins: dict
    executables: dict
    curr_result: Result
    cwd: str = field(default_factory=os.getcwd)

    def resolve_command(self, command: str) -> tuple[CommandType, str | None]:
        if command in self.built_ins:
            return CommandType.BUILTIN, None
        elif command in self.executables:
            return CommandType.EXECUTABLE, self.executables[command]
        return CommandType.INVALID, None
