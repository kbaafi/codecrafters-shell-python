import os
import readline
import sys
from pathlib import Path

from .common import PROMPT, ParsedInput, tokenize_user_input
from .shell import Shell


def make_completer(shell: Shell):
    cache = {"options": [], "text": None, "tab_count": 0, "base_dir": None}

    def build_file_system_matches(base_dir, partial_name, text):
        options: list[str] = []
        for entry in os.scandir(base_dir):
            if entry.name.startswith(partial_name):
                if entry.is_file():
                    options.append(
                        f"{text[: len(text) - len(partial_name)]}{entry.name} "
                    )
                elif entry.is_dir():
                    options.append(
                        f"{text[: len(text) - len(partial_name)]}{entry.name}/"
                    )
        options = sorted(options)
        return {"options": options, "text": text, "base_dir": base_dir}

    def completer(text: str, state: int):
        nonlocal cache

        # if state == 0:
        # line = readline.get_line_buffer()
        # print("line:", line)
        # print("text:", text)

        # print("text:", text)
        # print("cache_text:", cache["text"])
        # if len(tokens) == 0 or (len(tokens) == 1 and not line.endswith(" ")):
        # command, argstr = (
        #     line.strip().rsplit(" ", 1) if " " in line.strip() else (line.strip(), "")
        # )
        # argstr = text
        # print("command:", command)
        # print("argstr:", argstr)
        # print("text:", text)
        # options = [f"{cmd} " for cmd in shell.known_commands if cmd.startswith(text)]
        # if state < len(options):
        #     return options[state]

        # if options == []:
        # tokens = line.strip().split()
        # partial = tokens[-1]
        # if "/" not in partial:
        #     options = build_file_system_matches(shell._ctx.cwd, partial, line)[
        #         "options"
        #     ]
        #     # if len(options) > 0:
        #     #     if cache["tab_count"] == 1:
        #     #         print(cache["text"])
        #     #         sys.stdout.write("\a")

        #     #         sys.stdout.flush()
        #     #         return None
        #     # return " ".join(options)
        # else:
        line = readline.get_line_buffer()
        arg = line.split()[-1] if line.split() and not line[-1].isspace() else text
        base_dir, partial_file = arg.rsplit("/", 1) if "/" in arg else ("", arg)
        resolved_dir = (
            base_dir
            if base_dir.startswith("/")
            else os.path.join(shell._ctx.cwd, base_dir) if base_dir else shell._ctx.cwd
        )
        # try:
        #     options = build_file_system_matches(resolved_dir, partial_file, text)[
        #         "options"
        #     ]
        # except OSError:
        #     options = []
        try:
            options = build_file_system_matches(resolved_dir, partial_file, arg)[
                "options"
            ]
        except OSError:
            options = []
        # print("options:", options)

        # if state == 0:
        #     if len(options) > 0 and cache["tab_count"] == 0:
        #         cache["tab_count"] += 1
        #         sys.stdout.write("\a")
        #         sys.stdout.flush()
        #         return None
        #     elif len(options) > 0 and cache["tab_count"] > 0:
        #         cache["tab_count"] += 1

        #         out = " ".join(options)
        #         sys.stdout.write(out)
        #         sys.stdout.flush()
        #         return "\n"

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
        if state == 0 and len(options) > 1:
            sys.stdout.write("\a")
            sys.stdout.flush()
        return options[state] if state < len(options) else None

    return completer


def main():
    shell = Shell()
    completer = make_completer(shell)
    readline.set_completer(completer)
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
