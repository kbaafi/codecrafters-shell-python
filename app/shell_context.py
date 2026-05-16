import os


class ShellContext:
    def __init__(self) -> None:
        self._cwd = os.getcwd()

    @property
    def cwd(self) -> str:
        return self._cwd
    
    @cwd.setter
    def cwd(self, value) -> None:
        self._cwd = value