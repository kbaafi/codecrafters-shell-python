import os
import readline

from .command_handlers import history_handler
from .common import PROMPT
from .shell import Shell, output_results
from .shell_auto_complete import make_completer


def main():
    shell = Shell()
    completer = make_completer(shell)
    readline.set_completer(completer)
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set bell-style audible")
    readline.parse_and_bind("set show-all-if-ambiguous off")

    history_file = os.environ.get("HISTFILE", None)

    if history_file:
        history_handler(shell._ctx, "-r", history_file)

    while True:
        user_input = input(f"{PROMPT}")
        if len(user_input) == 0 or not user_input:
            continue

        result, parsed_input = shell.process_prompt(user_input=user_input)

        if result and result.interrupt:
            break
        elif result:
            output_results(shell._ctx, result, parsed_input)

    if history_file:
        history_handler(shell._ctx, "-w", history_file)


if __name__ == "__main__":
    main()
