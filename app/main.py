from enum import Enum
import sys
from .common import PROMPT, tokenize_args
from .handlers import built_ins, run_executable, CommandType, resolve_command
import os
from .shell_context import ShellContext
import shlex


def main():
    shell_context = ShellContext()

    while True:
        user_input = input(PROMPT)
        if len(user_input) == 0 or not user_input:
            continue

        parts = tuple(user_input.strip().split(" ", 1))
        command = parts[0]
        args = tokenize_args("".join(parts[1])) if len(parts) > 1 else []

        command_type, _ = resolve_command(command)

        match command_type:
            case CommandType.BUILTIN:
                result = built_ins[command](shell_context, *args)
            case CommandType.EXECUTABLE:
                result = run_executable(command, *args)
            case _:
                print(f"{command}: command not found")
                continue

        # Handle results
        if result.interrupt:
            break
        elif isinstance(result.value, str):
            print(result.value)
        

if __name__ == "__main__":
    main()
