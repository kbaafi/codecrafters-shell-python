import subprocess
import os
from typing import Union
from .shell_context import ShellContext
from .models import Result, CommandType


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


def type_handler(ctx: ShellContext, *args):
    _ = ctx
    command = args[0]
    command_type, path = ctx.resolve_command(command=command)

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
