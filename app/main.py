import os
import readline
import sys

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def make_completer(shell: Shell):
    cache = {"options": [], "text": None, "tab_count": 0, "base_dir": None}

    def build_file_system_completion_options(base_dir, partial_name, text):
        options: list[str] = []
        for entry in os.scandir(base_dir):
            if entry.is_file() and entry.name.startswith(partial_name):
                options.append(f"{entry.name}")
            elif entry.is_dir() and entry.name.startswith(partial_name):
                options.append(f"{entry.name}/")
        options = sorted(options)
        return {"options": options, "text": text, "base_dir": base_dir}

    def completer(text: str, state: int):
        nonlocal cache

        # if state == 0:
        line = readline.get_line_buffer()
        tokens = line.strip().split()

        # print("text:", text)
        # print("cache_text:", cache["text"])
        if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(" ")):
            options = [
                f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)
            ]
        else:
            partial = tokens[-1]
            if "/" not in partial:
                options = build_file_system_completion_options(
                    shell._ctx.cwd, partial, line
                )["options"]
                # if len(options) > 0:
                #     if cache["tab_count"] == 1:
                #         print(cache["text"])
                #         sys.stdout.write("\a")

                #         sys.stdout.flush()
                #         return None
                # return " ".join(options)
            else:
                display_dir, partial_file = partial.rsplit("/", 1)
                resolve_dir = (
                    display_dir
                    if partial.startswith("/")
                    else os.path.join(shell._ctx.cwd, display_dir or "/")
                )
                try:
                    options = build_file_system_completion_options(
                        resolve_dir, partial_file, line
                    )["options"]
                except OSError:
                    options = []
            if state == 0:
                if len(options) > 0 and cache["tab_count"] == 0:
                    cache["tab_count"] += 1
                    sys.stdout.write("\a")
                    sys.stdout.flush()
                    return None
                elif len(options) > 0 and cache["tab_count"] > 0:
                    cache["tab_count"] += 1
                    sys.stdout.write("")
                    sys.stdout.flush()
                    return f"\n {" ".join(options)}\n{line}"

            # if text != cache["text"]:
            #     cache["tab_count"] = 0
            #     cache["text"] = text
            # cache["options"] = options
            # cache["tab_count"] += 1

            # if len(cache["options"]) == 0:
            #     return None
            # if len(cache["options"]) == 1:
            #     return cache["options"][0]
            # if cache["tab_count"] == 1:
            #     sys.stdout.write("\a")
            #     sys.stdout.flush()
            #     return None
            # if cache["tab_count"] > 1:
            #     out = cache["base_dir"] + " ".join(cache["options"])
            #     # out = tokens[0]
            #     sys.stdout.write("")
            #     sys.stdout.flush()
            #     return out

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
