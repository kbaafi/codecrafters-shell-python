import os
from dataclasses import dataclass, field

from .models import CommandType, ProcessInfo, Result


@dataclass
class ShellContext:
    built_ins: dict
    executables: dict
    curr_result: Result
    cwd: str = field(default_factory=os.getcwd)
    completers: dict[str, str] = field(default_factory=dict)
    jobs: dict[int, ProcessInfo] = field(default_factory=dict)

    def resolve_command(self, command: str) -> tuple[CommandType, str | None]:
        if command in self.built_ins:
            return CommandType.BUILTIN, None
        elif command in self.executables:
            return CommandType.EXECUTABLE, self.executables[command]
        return CommandType.INVALID, None
