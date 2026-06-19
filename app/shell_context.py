import os
from collections import deque
from dataclasses import dataclass, field
from typing import Optional

from .models import CommandType, ProcessInfo


@dataclass
class ShellContext:
    built_ins: dict
    executables: dict
    cwd: str = field(default_factory=os.getcwd)
    completers: dict[str, str] = field(default_factory=dict)
    jobs: dict[int, ProcessInfo] = field(default_factory=dict)
    full_history: deque = field(default_factory=deque)
    curr_history: deque = field(default_factory=deque)
    variables: dict[str, str] = field(default_factory=dict)

    def resolve_command(self, command: str) -> tuple[CommandType, str | None]:
        if command in self.built_ins:
            return CommandType.BUILTIN, None
        elif command in self.executables:
            return CommandType.EXECUTABLE, self.executables[command]
        return CommandType.INVALID, None

    def variable_exists(self, var_name: str):
        return True if var_name in self.variables else False

    def get_variable_value(self, var_name: str) -> Optional[str]:
        return None if self.variable_exists(var_name) else self.variables[var_name]
