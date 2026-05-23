import readline

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def main():
    shell = Shell()

    def completer(text, state):
        options = [f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)]
        return options[state] if state < len(options) else None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        user_input = input(f"{PROMPT}")
        if len(user_input) == 0 or not user_input:
            continue

        parsed_input: ParsedInput = tokenize_user_input(user_input)
        command = parsed_input.tokens[0] if len(parsed_input.tokens) > 0 else ""
        args = parsed_input.tokens[1:] if len(parsed_input.tokens) > 1 else []

        if command == "":
            continue

        shell.execute(command, *args)

        # Handle results
        if shell._ctx.curr_result.interrupt:
            break
        else:
            shell.output_results(parsed_input)


if __name__ == "__main__":
    main()
