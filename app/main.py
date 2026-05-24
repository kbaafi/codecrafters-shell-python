import os
import readline
import sys

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def make_completer(shell: Shell):
    cache = {"options": [], "text": None, "tab_count": 0}
    tab_count = {"n": 0, "last_text": None}

    def build_file_system_completion_options(base_dir, partial_name, text):
        options: list[str] = []
        for entry in os.scandir(base_dir):
            if entry.is_file() and entry.name.startswith(partial_name):
                options.append(f"{entry.name} ")
            elif entry.is_dir() and entry.name.startswith(partial_name):
                options.append(f"{entry.name}/")
        options = sorted(options)
        return {"options": options, "text": text}

    def completer(text: str, state: int):
        nonlocal cache
        nonlocal tab_count

        line = readline.get_line_buffer()
        tokens = line.strip().split()
        if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(" ")):
            cache["options"] = [
                f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)
            ]
            cache["text"] = text
        else:
            partial = tokens[-1]
            # line_stub = tokens[:-1]
            # line_stub_str = " ".join(line_stub)
            # print(line)
            # print("tokens", tokens)
            # print("stub", line_stub_str)
            # print("partial", partial)
            # print("text", " ".join(tokens[:-2]))

            if "/" not in partial:
                cache = build_file_system_completion_options(
                    shell._ctx.cwd, partial, line
                )
            else:
                display_dir, partial_file = partial.rsplit("/", 1)
                resolve_dir = (
                    display_dir
                    if partial.startswith("/")
                    else os.path.join(shell._ctx.cwd, display_dir or "/")
                )
                try:
                    cache = build_file_system_completion_options(
                        resolve_dir, partial_file, line
                    )
                except OSError:
                    cache = {"options": [], "text": ""}
        # print(cache["options"])
        # print(cache["text"])
        # return cache["options"][0] if len(cache["options"]) > 0 else None

        if len(cache["options"]) == 0:
            return None
        elif len(cache["options"]) == 1:
            return cache["options"][0]
        if state == 0:
            cache["tab_count"] += 1
            if cache["tab_count"] == 1:
                sys.stdout.write("\a")
                sys.stdout.flush()
                return None
            if cache["tab_count"] > 1:
                return " ".join(cache["options"])

        # if len(cached["options"]) == 0:
        #     return None
        # if len(cached["options"]) == 1:
        #     return cached["options"][0] if state == 0 else None
        # if state == 0:
        #     if tab_count["last_text"] == text:
        #         tab_count["n"] += 1
        #     else:
        #         tab_count["n"] = 1
        #         tab_count["last_text"] = text
        #     if tab_count["n"] == 1:
        #         sys.stdout.write("\a")
        #         sys.stdout.flush()
        #         return None
        #     else:
        #         sys.stdout.write("\n" + "  ".join(sorted(cached["options"])) + "\n")
        #         sys.stdout.write("\n" + tab_count["last_text"] + "\n")
        #         sys.stdout.flush()
        #         readline.redisplay()
        #         # return tab_count["last_text"]
        #         # return "  ".join(cached["options"])
        #         return text

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
