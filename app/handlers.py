from typing import Generic, Optional, TypeVar
import subprocess
import sys
import os
from enum import Enum
from dataclasses import dataclass

from typing import Union
from .shell_context import ShellContext

T = TypeVar("T")

class CommandType(Enum):
    BUILTIN = "BUILTIN"
    EXECUTABLE = "EXECUTABLE"
    INVALID = "INVALID"


@dataclass
class Result:
    value: Optional[str] = None
    error: Optional[str] = None
    interrupt: Optional[bool] = False


def is_executable_command(command) -> tuple[bool, Union[str, None]]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)

    for dir in dirs:
        full_path = os.path.join(dir, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return True, full_path
    return False, None 


def exit_handler(ctx: ShellContext, *args):
    _ = args
    return Result(interrupt=True)


def echo_handler(ctx: ShellContext, *args):
    return Result(value=" ".join(args))


def cd_handler(ctx: ShellContext, *args):
    path = args[0] if args else os.path.expanduser("~")

    if os.path.isabs(path):
        resolved = path
    elif path.startswith("~"):
        base_path = os.path.expanduser(path[0])
        try:
            resolved = base_path + path[1:]
        except:
            resolved = base_path
    else:
        resolved = os.path.normpath(os.path.join(ctx.cwd, path))

    if os.path.isdir(resolved):
        ctx.cwd = resolved
        return Result()
    return Result(value=f"cd: {path}: No such file or directory")


def resolve_command(command: str) -> tuple[CommandType, str | None]:
    if command in built_ins:
        return CommandType.BUILTIN, None
    found, full_path = is_executable_command(command)
    if found:
        return CommandType.EXECUTABLE, full_path
    return CommandType.INVALID, None


def type_handler(ctx: ShellContext, *args):
    _ = ctx
    command = args[0]
    command_type, path = resolve_command(command)

    match command_type:
        case CommandType.BUILTIN:
            return Result(value=f"{command} is a shell builtin")
        case CommandType.EXECUTABLE:
            return Result(value=f"{command} is {path}")
        case CommandType.INVALID:
            return Result(value=f"{command}: not found")
    

def pwd_handler(ctx: ShellContext, *args):
    return Result(value=ctx.cwd)



def run_executable(command: str, *args):
    result = subprocess.run([command, *args], capture_output=True, text=True)
    return Result(value=result.stdout, error=result.stderr)


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
    "type": type_handler,
    "pwd": pwd_handler,
    "cd": cd_handler
}
