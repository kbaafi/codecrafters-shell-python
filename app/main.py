from enum import Enum
import sys
from .common import PROMPT, is_executable_command
from .handlers import built_ins, run_executable
import os


class CommandType(Enum):
    BUILTIN = "BUILTIN"
    EXECUTABLE = "EXECUTABLE"
    INVALID = "INVALID"


def ascertain_command_type(command: str) -> CommandType:
    if command in built_ins:
        return CommandType.BUILTIN
    else:
        result, _ = is_executable_command(command)
        return CommandType.EXECUTABLE
    return CommandType.INVALID


def main():
    while True:
        user_input = input(PROMPT)
        if len(user_input) == 0 or not user_input:
            continue

        command = user_input.strip().split()[0]
        args = user_input.strip().split()[1:]


        command_type = ascertain_command_type(command)

        if command_type == CommandType.BUILTIN:
            result = built_ins[command](*args)
        elif command_type == CommandType.EXECUTABLE:
            result = run_executable(command, *args)
        else:
            print(f"{command}: command not found")
            continue

        # Handle results
        if result.interrupt:
            break
        elif isinstance(result.value, str):
            print(result.value)
        

if __name__ == "__main__":
    main()
