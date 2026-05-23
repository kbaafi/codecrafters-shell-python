import os
from dataclasses import dataclass, field
from .command_handlers import exit_handler, echo_handler, type_handler, pwd_handler, cd_handler, run_executable
from .models import Result, CommandType
from typing import Union


# def is_executable_command(command) -> tuple[bool, Union[str, None]]:
#     path = os.environ["PATH"]
#     dirs = path.split(os.pathsep)

#     for dir in dirs:
#         full_path = os.path.join(dir, command)
#         if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
#             return True, full_path
#     return False, None

def get_executables() -> dict[str, str]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)
    executables = {}

    for dir in dirs:
        if not os.path.isdir(dir):
            continue
        executables.update({
            f: os.path.join(dir, f)
            for f in os.listdir(dir)
            if f not in executables
            and os.path.isfile(os.path.join(dir, f))
            and os.access(os.path.join(dir, f), os.X_OK)
        })
    return executables


def _default_built_ins():
    return {
        "exit": exit_handler,
        "echo": echo_handler,
        "type": type_handler,
        "pwd": pwd_handler,
        "cd": cd_handler,
    }


@dataclass
class ShellContext:
    cwd: str = field(default_factory=os.getcwd)
    built_ins: dict = field(default_factory=_default_built_ins)
    executables: dict = field(default_factory=get_executables)
    curr_result: Result = field(default_factory=Result)

    def execute(self, command: str, *args):
        if command in self.built_ins:
            self.curr_result = self.built_ins[command](self, *args)
        elif command in self.executables:
            path = self.executables[command]
            self.curr_result = run_executable(path, *args)
        else:
            self.curr_result = Result(error=f"{command}: command not found\n")

    def resolve_command(self, command: str) -> tuple[CommandType, str | None]:
        if command in self.built_ins:
            return CommandType.BUILTIN, None
        elif command in self.executables:
            return CommandType.EXECUTABLE, self.executables[command]
        return CommandType.INVALID, None
