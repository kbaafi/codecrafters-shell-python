import os
import readline
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
            if entry.name.startswith(partial_name):
                if entry.is_file():
                    options.append(f"{text_prefix}{entry.name} ")
                elif entry.is_dir():
                    options.append(f"{text_prefix}{entry.name}/")
        return sorted(options)

    def completer(text: str, state: int):

        line = readline.get_line_buffer()
        tokens = line.split()
        is_command = not tokens or (len(tokens) == 1 and not line[-1].isspace())

        if is_command:
            shell._refresh_executables()
            options = [f"{c} " for c in shell.known_commands if c.startswith(text)]
        else:
            arg = tokens[-1] if not line[-1].isspace() else ""
            base_dir, partial_file = arg.rsplit("/", 1) if "/" in arg else ("", arg)
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
