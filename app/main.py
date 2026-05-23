import os
import readline
import sys

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def make_completer(shell: Shell):
    cached = {"options": [], "text": None}

    def build_file_system_completion_options(base_dir, partial_name):
        options: list[str] = []
        for entry in os.scandir(base_dir):
            if entry.is_file() and entry.name.startswith(partial_name):
                options.append(f"{entry.name} ")
            elif entry.is_dir() and entry.name.startswith(partial_name):
                options.append(f"{entry.name}/")
        options = sorted(options)
        return {"options": options, "text": " ".join(options)}

    def completer(text: str, state: int):
        nonlocal cached
        if state == 0:
            line = readline.get_line_buffer()
            tokens = line.strip().split()
            if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(" ")):
                cached["options"] = [
                    f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)
                ]
                cached["text"] = text
            else:
                last_token = tokens[-1] if not line.endswith(" ") else ""
                partial = last_token

                if "/" not in partial:
                    cached = build_file_system_completion_options(
                        shell._ctx.cwd, partial
                    )
                else:
                    display_dir, partial_file = partial.rsplit("/", 1)
                    resolve_dir = (
                        display_dir
                        if partial.startswith("/")
                        else os.path.join(shell._ctx.cwd, display_dir or "/")
                    )
                    try:
                        cached = build_file_system_completion_options(
                            base_dir=resolve_dir, partial_name=partial_file
                        )
                    except OSError:
                        cached = {"options": [], "text": ""}

        if len(cached["options"]) == 0:
            return None
        if len(cached["options"]) == 1:
            return cached["options"][0] if state == 0 else None
        if state == 0:
            sys.stdout.write("\a")
            sys.stdout.flush()
            return ""
        if state == 1:
            sys.stdout.write("\n" + "  ".join(cached["options"]) + "\n")
            sys.stdout.flush()
            readline.redisplay()
            return None
        return None

    return completer


def main():
    shell = Shell()
    completer = make_completer(shell)
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
