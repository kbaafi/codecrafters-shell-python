import os
import readline
import sys
from pathlib import Path

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell
from .shell_auto_complete import make_completer


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

        pipeline_tokens = user_input.split(sep="|")
        parsed_inputs: list[ParsedInput] = [
            tokenize_user_input(i) for i in pipeline_tokens
        ]

        if len(parsed_inputs) == 0:
            continue
        elif len(parsed_inputs) == 1:
            parsed_input = parsed_inputs[0]
            if parsed_input.command == "":
                continue
            shell.execute(parsed_input)
        else:
            shell.execute_pipeline(parsed_inputs)

        # Handle results
        if shell._ctx.curr_result.interrupt:
            break
        else:
            shell.output_results()


if __name__ == "__main__":
    main()
