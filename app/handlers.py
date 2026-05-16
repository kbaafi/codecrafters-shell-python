from abc import ABC, abstractmethod


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



def exit_handler(*args):
    _ = args
    return ExitResult(None)


def echo_handler(*args):
    result_msg = f'{" ".join(args)} \n'
    return StringResult(result_msg)


def type_handler(*args):
    queried_command = str(args[0])
    if queried_command in built_ins:
        return StringResult(f'{queried_command} is a shell builtin')
    else:
        return StringResult(f'{queried_command}: not found')


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
    "type": type_handler,
}
