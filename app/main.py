from enum import Enum
import sys
from .common import PROMPT, is_executable_command
from .handlers import built_ins, run_executable, CommandType, resolve_command
import os
from .shell_context import ShellContext


def main():
    shell_context = ShellContext()

    while True:
        user_input = input(PROMPT)
        if len(user_input) == 0 or not user_input:
            continue

        parts = user_input.strip().split()
        command, *args = parts

        args = 

        command_type, full_path = resolve_command(command)

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
