from enum import Enum
import sys
from .common import PROMPT, tokenize_user_input
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

        result, redirect_file = tokenize_user_input(user_input)
        command = result[0] if len(result) > 0 else ""
        args = result[1:] if len(result) > 1 else []

        if command == "":
            continue

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
        elif isinstance(result.value, str) and result.value:
            if redirect_file:
                with open(redirect_file, 'w') as file:
                    file.write(result.value)
            else:
                print(result.value, end='')
        

if __name__ == "__main__":
    main()
