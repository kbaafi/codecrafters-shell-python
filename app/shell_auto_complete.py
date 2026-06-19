import os
import readline
import subprocess
import sys

from .shell import Shell


def make_completer(shell: Shell):
    def build_file_system_matches(base_dir, partial_name, cwd, text_prefix):
        resolved_dir = (
            base_dir
            if base_dir.startswith("/")
            else os.path.join(cwd, base_dir) if base_dir else cwd
        )
        options: list[str] = []
        for entry in os.scandir(resolved_dir):
            if not partial_name:
                if entry.is_file():
                    options.append(f"{text_prefix}{entry.name} ")
                elif entry.is_dir():
                    options.append(f"{text_prefix}{entry.name}/")
            elif entry.name.startswith(partial_name):
                if entry.is_file():
                    options.append(f"{text_prefix}{entry.name} ")
                elif entry.is_dir():
                    options.append(f"{text_prefix}{entry.name}/")
        return sorted(options)

    def completer(text: str, state: int):
        line = readline.get_line_buffer()
        tokens = line.split()
        shell._refresh_executables()
        cmd = tokens[0] if tokens else ""
        is_typing_command = not line or (len(tokens) == 1 and not line[-1].isspace())

        if cmd in shell._ctx.completers:
            previous_text = tokens[-2] if len(tokens) >= 2 else ""
            script = shell._ctx.completers[cmd]
            env = os.environ.copy()
            env["COMP_LINE"] = line
            env["COMP_POINT"] = str(len(line))
            try:
                result = subprocess.run(
                    [script, cmd, text, previous_text],
                    capture_output=True,
                    text=True,
                    env=env,
                )
                options = [f"{line} " for line in result.stdout.splitlines()]
            except OSError:
                options = []
        elif is_typing_command:
            options = [f"{c} " for c in shell.known_commands if c.startswith(text)]
        else:
            # when text is empty, the last token in the line is the base path
            effective = (
                text
                if text
                else (tokens[-1] if tokens and tokens[-1].endswith("/") else text)
            )
            base_dir, partial_file = (
                effective.rsplit("/", 1) if "/" in effective else ("", effective)
            )
            text_prefix = effective[: len(effective) - len(partial_file)]
            try:
                options = build_file_system_matches(
                    base_dir, partial_file, shell._ctx.cwd, text_prefix
                )
            except OSError:
                options = []

        if state == 0 and len(options) > 1:
            sys.stdout.write("\a")
            sys.stdout.flush()
        return options[state] if state < len(options) else None

    return completer
