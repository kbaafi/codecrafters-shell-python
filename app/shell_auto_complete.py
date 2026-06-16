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
        sys.stdout.write(f"{resolved_dir=}, {partial_name=}\n")
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
        is_command = len(tokens) == 1
        if is_command:
            shell._refresh_executables()
            cmd = tokens[0] if tokens else text
            if cmd in shell._ctx.completers:
                script = shell._ctx.completers[cmd]
                env = os.environ.copy()
                env["COMP_LINE"] = line
                env["COMP_POINT"] = str(len(line))
                try:
                    result = subprocess.run(
                        [script, cmd],
                        capture_output=True,
                        text=True,
                        env=env,
                    )
                    options = [f"{l} " for l in result.stdout.splitlines() if l]
                except OSError:
                    options = []
            else:
                options = [f"{c} " for c in shell.known_commands if c.startswith(text)]
        else:
            base_dir, partial_file = text.rsplit("/", 1) if "/" in text else ("", text)
            sys.stdout.write(f"{base_dir=}, {partial_file=}\n")
            text_prefix = text[: len(text) - len(partial_file)]
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
