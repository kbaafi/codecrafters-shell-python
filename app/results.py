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