from typing import Generic, TypeVar
import subprocess
import os
from enum import Enum

from app.common import is_executable_command

T = TypeVar("T")

class CommandType(Enum):
    BUILTIN = "BUILTIN"
    EXECUTABLE = "EXECUTABLE"
    INVALID = "INVALID"


class Result(Generic[T]):
    def __init__(self, value: T, interrupt: bool = False) -> None:
        self._value = value
        self._interrupt = interrupt

    @property
    def value(self) -> T:
        return self._value
    
    @property
    def interrupt(self) -> bool:
        return self._interrupt
    


def exit_handler(*args):
    _ = args
    return Result[None](value=None, interrupt=True)


def echo_handler(*args):
    result_msg = f'{" ".join(args)}'
    return Result[str](value=result_msg)


def resolve_command(command: str) -> tuple[CommandType, str | None]:
    if command in built_ins:
        return CommandType.BUILTIN, None
    found, full_path = is_executable_command(command)
    if found:
        return CommandType.EXECUTABLE, full_path
    return CommandType.INVALID, None


def type_handler(*args):
    command = args[0]
    command_type, path = resolve_command(command)

    match command_type:
        case CommandType.BUILTIN:
            return Result[str](value=f"{command} is a shell builtin")
        case CommandType.EXECUTABLE:
            return Result[str](value=f"{command} is {path}")
        case CommandType.INVALID:
            return Result[str](value=f"{command}: not found")
    

def pwd_handler(*args):
    return Result[str](value=os.getcwd())



def run_executable(command: str, *args):
    result = subprocess.run([command, *args])
    return Result[subprocess.CompletedProcess](value=result)


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
    "type": type_handler,
    "pwd": pwd_handler,
    # "cd": 
}
