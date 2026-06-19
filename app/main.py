import os
import readline

from .common import PROMPT
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

    history_file = os.environ.get("HISTFILE", None)

    if history_file:
        shell.load_history(history_file)

    while True:
        user_input = input(f"{PROMPT}")
        if len(user_input) == 0 or not user_input:
            continue

        result = shell.handle_prompt(user_input=user_input)

        if result and result.interrupt:
            break

    if history_file:
        shell.save_history(history_file)


if __name__ == "__main__":
    main()
