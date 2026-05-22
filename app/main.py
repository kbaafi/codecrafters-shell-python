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
        user_input = input(f'{PROMPT}')
        if len(user_input) == 0 or not user_input:
            continue

        result, stdout_redirect, stderr_redirect = tokenize_user_input(user_input)
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
                sys.stdout.write(f"{command}: command not found\n")
                continue

        # Handle results
        if result.interrupt:
            break
        if stderr_redirect is not None:
            with open(stderr_redirect, 'w') as file:
                file.write(result.error or "")
            if result.value:
                output = result.value if result.value.endswith('\n') else result.value + '\n'
                sys.stdout.write(output)
        # elif result.error:
        #     output = result.error if result.error.endswith('\n') else result.error + '\n'
        #     sys.stdout.write(output)

        elif stdout_redirect is not None:
            with open(stdout_redirect, 'w') as file:
                file.write(result.value or "")
        elif result.value:
            output = result.value if result.value.endswith('\n') else result.value + '\n'
            sys.stdout.write(output)
        
        

if __name__ == "__main__":
    main()
