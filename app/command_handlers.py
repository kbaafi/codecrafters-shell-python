from __future__ import annotations

import argparse
import os
import subprocess

from .models import CommandType, Result, ShellContext


def exit_handler(ctx: ShellContext, *args):
    _ = args
    _ = ctx
    return Result(interrupt=True)


def echo_handler(ctx: ShellContext, *args):
    _ = ctx
    return Result(value=" ".join(args))


def cd_handler(ctx: ShellContext, *args):
    path = os.path.expanduser(args[0] if args else "~")

    if os.path.isabs(path):
        resolved = path
    else:
        resolved = os.path.normpath(os.path.join(ctx.cwd, path))

    if os.path.isdir(resolved):
        ctx.cwd = resolved
        return Result()
    return Result(value=f"cd: {path}: No such file or directory")


def complete_handler(ctx: ShellContext, *args):
    _ = ctx
    _ = args
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="print")
    parser.add_argument("-C", dest="completer_script")
    parsed_args, remaining_args = parser.parse_known_args(args)
    # print(parsed_args, remaining_args)

    if parsed_args.print is not None:
        if parsed_args.print in ctx.completers:
            return Result(
                value=f"complete -C '{ctx.completers[parsed_args.print]}' {parsed_args.print}"
            )
        else:
            return Result(
                value=f"complete: {parsed_args.print}: no completion specification"
            )
    elif parsed_args.completer_script is not None and remaining_args:
        ctx.completers[remaining_args[0]] = parsed_args.completer_script

    return Result(value=None)


def type_handler(ctx: ShellContext, *args):
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
