import os
import readline

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def main():
    shell = Shell()

    def completer(text: str, state):
        tokens = text.strip().split(" ")
        print(" tokens ", len(tokens), text)
        if len(tokens) == 1:
            options = [
                f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)
            ]
        elif len(tokens) > 1:
            args = "".join(tokens[1:])
            command = tokens[0]
            options = [
                f"{command} {file} "
                for file in os.listdir(shell._ctx.cwd)
                if os.path.isfile(os.path.join(shell._ctx.cwd, file))
                and os.access(
                    os.path.join(shell._ctx.cwd, file), os.R_OK | os.W_OK | os.F_OK
                )
                and os.path.join(shell._ctx.cwd, file).startswith(args)
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
