from __future__ import annotations

import argparse
import os
import subprocess

from .models import CommandType, Result
from .shell_context import ShellContext


def exit_handler(ctx: ShellContext, *args):
    _ = args
    _ = ctx
    return Result(interrupt=True)


def echo_handler(ctx: ShellContext, *args):
    _ = ctx
    return Result(value=" ".join(args) + "\n")


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


def _render_job_order_marking(ctx: ShellContext, job_id: int) -> str:
    job_ids = sorted(ctx.jobs.keys(), reverse=True)
    most_recent_job_id = job_ids[0] if job_ids else 0
    second_most_recent_job_id = job_ids[1] if len(job_ids) > 1 else 0

    if job_id == most_recent_job_id:
        return "+"
    elif job_id == second_most_recent_job_id:
        return "-"
    return " "


def _render_job_statuses(ctx: ShellContext, show_only_done=False) -> list[str]:
    if len(ctx.jobs) == 0:
        return []

    output: list[str] = []
    done_jobs = []
    for job_id, process_info in ctx.jobs.items():
        running_state = True if process_info.program.poll() is None else False

        if show_only_done and running_state:
            continue

        running = "Running" if running_state else "Done"
        spaces = " " * 17
        _tokens = (
            process_info.parsed_input.tokens
            if process_info.program.poll() is None
            else process_info.parsed_input.tokens[:-1]
        )
        job_order = _render_job_order_marking(ctx=ctx, job_id=job_id)
        command = " ".join(_tokens)
        status = f"[{job_id}]{job_order}  {running}{spaces}{command}"
        output.append(status)
        if process_info.program.poll() is not None:
            done_jobs.append(job_id)

    for job_id in done_jobs:
        del ctx.jobs[job_id]
    return output


def jobs_handler(ctx: ShellContext, *args):
    _ = args

    result = _render_job_statuses(ctx)
    return Result(value="\n".join(result)) if len(result) > 0 else Result(value=None)


def render_completed_jobs(ctx: ShellContext):
    result = _render_job_statuses(ctx, show_only_done=True)
    return Result(value="\n".join(result)) if len(result) > 0 else Result(value=None)


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


def history_handler(ctx: ShellContext, *args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", dest="read_history_file")
    parser.add_argument("-w", dest="write_history_file")
    parsed_args, remaining_args = parser.parse_known_args(args)

    if parsed_args.read_history_file is not None:
        with open(parsed_args.read_history_file, "r") as _file:
            lines = [line.strip() for line in _file]
            for line in lines:
                ctx.history.append(line)
        return Result()  # empty result
    elif parsed_args.write_history_file is not None:
        with open(parsed_args.write_history_file, "w") as _file:
            for line in ctx.history:
                _file.write(line + "\n")
        return Result()
    else:
        limit = int(remaining_args[0]) if len(remaining_args) > 0 else 0
        result = []
        for i, prompt in enumerate(ctx.history):
            result.append(f"\t{i+1} {prompt}")

        limited_result = result[(0 - abs(limit)) :] if limit else result
        return (
            Result(value="\n".join(limited_result))
            if len(limited_result) > 0
            else Result(value=None)
        )


def pwd_handler(ctx: ShellContext, *args):
    return Result(value=ctx.cwd)


def run_executable(command: str, *args, stdin: str | None = None):
    result = subprocess.run(
        [command, *args], capture_output=True, text=True, input=stdin
    )
    return Result(value=result.stdout, error=result.stderr)
