from abc import ABC, abstractmethod
from enum import Enum
import os
from typing import Generic, TypeVar
import subprocess

T = TypeVar("T")


class AbstractResult(ABC):
    @property
    @abstractmethod
    def result(self) -> str: ...


class BaseResult(AbstractResult):
    _interrupt: bool = False
    def __init__(self, result: str):
        self._result = result

    @property
    def result(self) -> str:
        return self._result
    
    @property
    def interrupt(self) -> bool:
        return self._interrupt
    

class ExitResult(BaseResult):
    _interrupt: bool = True


class StringResult(BaseResult):
    def __init__(self, result: str):
        super().__init__(result)


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
    

# class CommandType(Enum):
#     BUILTIN = "BUILTIN"
#     EXECUTABLE = "EXECUTABLE"
    


def exit_handler(*args):
    _ = args
    return Result[None](value=None, interrupt=True)


def echo_handler(*args):
    result_msg = f'{" ".join(args)}'
    return Result[str](value=result_msg)


# def type_handler(*args):
#     queried_command = str(args[0])
#     ctype: CommandType = CommandType.EXECUTABLE
#     if queried_command in built_ins:
#         ctype = CommandType.BUILTIN
#     return Result[CommandType](value=ctype)
    

# def executable_file_handler(*args):
#     command = args[0]
#     path = os.environ["PATH"]
#     dirs = path.split(os.pathsep)

#     for dir in dirs:
#         full_path = os.path.join(dir, command)
#         if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
#             return StringResult(f'{command} is {full_path}')
#     return StringResult(f'{command}: not found')

def run_executable(command: str, *args):
    result = subprocess.run([command, *args])
    return Result[subprocess.CompletedProcess](value=result)


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
}
