from abc import ABC, abstractmethod
from enum import Enum
import os
from typing import Generic, TypeVar
import subprocess

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


def run_executable(command: str, *args):
    result = subprocess.run([command, *args])
    return Result[subprocess.CompletedProcess](value=result)


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
}
