from dataclasses import dataclass, field
from typing import Optional
from enum import Enum, auto


@dataclass
class ParsedInput:
    tokens: list[str] = field(default_factory=list)
    stdout_redirect: str | None = None
    stderr_redirect: str | None = None
    stdout_append: bool = False
    stderr_append: bool = False


@dataclass
class Result:
    value: Optional[str] = None
    error: Optional[str] = None
    interrupt: Optional[bool] = False

class CommandType(Enum):
    BUILTIN = auto()
    EXECUTABLE = auto()
    INVALID = auto()