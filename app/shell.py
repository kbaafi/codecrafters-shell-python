import os
import subprocess
import sys

from .command_handlers import (
    cd_handler,
    complete_handler,
    echo_handler,
    exit_handler,
    jobs_handler,
    pwd_handler,
    render_completed_jobs,
    run_executable,
    type_handler,
)
from .common import ParsedInput
from .models import ProcessInfo, Result
from .shell_context import ShellContext


def get_executables() -> dict[str, str]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)
    executables = {}

    for dir in dirs:
        if not os.path.isdir(dir):
            continue
        executables.update(
            {
                f: os.path.join(dir, f)
                for f in os.listdir(dir)
                if f not in executables
                and os.path.isfile(os.path.join(dir, f))
                and os.access(os.path.join(dir, f), os.X_OK)
            }
        )
    return executables


def _default_built_ins():
    return {
        "exit": exit_handler,
        "echo": echo_handler,
        "type": type_handler,
        "pwd": pwd_handler,
        "cd": cd_handler,
        "complete": complete_handler,
        "jobs": jobs_handler,
    }


def _to_screen(text: str | None):
    if text:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")


def _to_file(text: str | None, path: str, append: bool):
    if append and os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                with open(path, "a") as f:
                    f.write("\n")
    with open(path, "a" if append else "w") as f:
        f.write(text or "")


class Shell:
    def __init__(self) -> None:
        self._ctx = ShellContext(
            cwd=os.getcwd(),
            built_ins=_default_built_ins(),
            executables=get_executables(),
            curr_result=Result(value=None, error=None),
        )
        self._parsed_input: ParsedInput = ParsedInput(tokens=[])
        self._known_commands: list[str] = list(self._ctx.built_ins) + list(
            self._ctx.executables
        )

    def _refresh_executables(self):
        self._ctx.executables = get_executables()
        self._known_commands = list(self._ctx.built_ins) + list(self._ctx.executables)

    def execute(self, parsed_input: ParsedInput, stdin: str | None = None):
        self._refresh_executables()

        self._parsed_input = parsed_input

        if parsed_input.is_background:
            job = subprocess.Popen(parsed_input.tokens[:-1])
            current_max_job_id = (
                max(self._ctx.jobs.keys()) if len(self._ctx.jobs) > 0 else 0
            )

            self._ctx.jobs[current_max_job_id + 1] = ProcessInfo(
                program=job, parsed_input=parsed_input
            )

            self._ctx.curr_result = Result(
                value=f"[{current_max_job_id + 1}] {job.pid}"
            )
        else:
            if parsed_input.command in self._ctx.built_ins:
                self._ctx.curr_result = self._ctx.built_ins[parsed_input.command](
                    self._ctx, *parsed_input.args
                )
            elif parsed_input.command in self._ctx.executables:
                self._ctx.curr_result = run_executable(
                    parsed_input.command, *parsed_input.args, stdin=stdin
                )
            else:
                self._ctx.curr_result = Result(
                    error=f"{parsed_input.command}: command not found\n"
                )

    def execute_pipeline(self, command_pipeline: list[ParsedInput]):
        for parsed_input in command_pipeline:
            stdin = self._ctx.curr_result.value
            self._ctx.curr_result = Result(value=None, error=None)
            self.execute(parsed_input=parsed_input, stdin=stdin)

    def output_results(self):
        result = self._ctx.curr_result
        if self._parsed_input.stderr_redirect is not None:
            _to_file(
                result.error,
                self._parsed_input.stderr_redirect,
                self._parsed_input.stderr_append,
            )
            _to_screen(result.value)
        elif self._parsed_input.stdout_redirect is not None:
            _to_file(
                result.value,
                self._parsed_input.stdout_redirect,
                self._parsed_input.stdout_append,
            )
            _to_screen(result.error)
        elif result.value:
            _to_screen(result.value)
        elif result.error:
            _to_screen(result.error)

        result = render_completed_jobs(self._ctx)
        if result.value:
            _to_screen(result.value)

    @property
    def known_commands(self):
        return self._known_commands
