from enum import Enum
import sys
from .common import PROMPT, ParsedInput, tokenize_user_input, output_result
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

        parsed_input: ParsedInput = tokenize_user_input(user_input)
        command = parsed_input.tokens[0] if len(parsed_input.tokens) > 0 else ""
        args = parsed_input.tokens[1:] if len(parsed_input.tokens) > 1 else []

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
        else:
            output_result(result, parsed_input)
        
        

if __name__ == "__main__":
    main()
