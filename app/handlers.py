from typing import Generic, TypeVar
import subprocess
from .common import is_executable_command
import os

T = TypeVar("T")


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


def type_handler(*args):
    command = args[0]
    if command in built_ins:
        return Result[str](value=f"{command} is a shell builtin")
    found, full_path = is_executable_command(command)
    if found:
        return Result[str](value=f"{command} is {full_path}")
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
    "pwd": pwd_handler
}
