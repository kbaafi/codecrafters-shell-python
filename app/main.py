import os
import readline

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def main():
    shell = Shell()

    def completer(text: str, state):
        line = readline.get_line_buffer()
        tokens = line.strip().split()
        if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(" ")):
            options = [
                f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)
            ]
        else:
            partial = tokens[-1] if line.endswith(" ") else text
            options = [
                f"{file} "
                for file in os.listdir(shell._ctx.cwd)
                if file.startswith(partial)
            ]

        return options[state] if state < len(options) else None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

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
