from __future__ import annotations

import argparse
import os
import subprocess

from .models import CommandType, JobOrder, Result, ShellContext


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
    parser.add_argument("-r", dest="deregiser_completer")
    parsed_args, remaining_args = parser.parse_known_args(args)

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
    elif parsed_args.deregiser_completer is not None:
        if parsed_args.deregiser_completer in ctx.completers:
            del ctx.completers[parsed_args.deregiser_completer]

    return Result(value=None)


def jobs_handler(ctx: ShellContext, *args):
    _ = args
    if len(ctx.jobs) == 0:
        return Result(value="")

    output = []
    done_jobs = []
    for job_id, process_info in ctx.jobs.items():
        job_order = " "
        if process_info.job_order == JobOrder.MOST_RECENT:
            job_order = "+"
        elif process_info.job_order == JobOrder.PREVIOUS_MOST_RECENT:
            job_order = "-"
        elif process_info.job_order == JobOrder.OTHER:
            job_order = " "
        running = "Running" if process_info.program.poll() is None else "Done"
        spaces = " " * 17
        command = " ".join(process_info.parsed_input.tokens)
        status = f"[{job_id}]{job_order}  {running}{spaces}{command}"
        output.append(status)
        if process_info.program.poll() is not None:
            done_jobs.append(job_id)

    for job_id in done_jobs:
        del ctx.jobs[job_id]

    return Result(value="\n".join(output))


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
