import os
import readline
import sys
from pathlib import Path

from .common import PROMPT, ParsedInput, tokenize_user_input
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
        arg = line.split()[-1] if line.split() and not line[-1].isspace() else text
        base_dir, partial_file = arg.rsplit("/", 1) if "/" in arg else ("", arg)
        text_prefix = text[: len(text) - len(partial_file)]
        try:
            options = build_file_system_matches(
                base_dir, partial_file, shell._ctx.cwd, text_prefix
            )
        except OSError:
            options = []

        # if options == []:
        #     print("arg:", arg, "line:", line, "text:", text)

        if state == 0 and len(options) > 1:
            sys.stdout.write("\a")
            sys.stdout.flush()
        return options[state] if state < len(options) else None

    return completer


def main():
    shell = Shell()
    completer = make_completer(shell)
    readline.set_completer(completer)
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set bell-style audible")
    readline.parse_and_bind("set show-all-if-ambiguous off")

    while True:
        user_input = input(f"{PROMPT}")
        if len(user_input) == 0 or not user_input:
            continue

        parsed_input: ParsedInput = tokenize_user_input(user_input)

        if parsed_input.command == "":
            continue

        shell.execute(parsed_input)

        # Handle results
        if shell._ctx.curr_result.interrupt:
            break
        else:
            shell.output_results()


if __name__ == "__main__":
    main()
