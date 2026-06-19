import os

from app.models import CommandType, ParsedInput
from app.shell import Shell


def test_cwd_initialized_to_current_dir():
    shell = Shell()
    assert shell._ctx.cwd == os.getcwd()


def test_built_ins_registered():
    shell = Shell()
    assert "echo" in shell._ctx.built_ins
    assert "exit" in shell._ctx.built_ins
    assert "type" in shell._ctx.built_ins
    assert "pwd" in shell._ctx.built_ins
    assert "cd" in shell._ctx.built_ins


def test_executables_populated():
    shell = Shell()
    assert len(shell._ctx.executables) > 0


def test_execute_builtin_echo():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["echo", "hello", "world"]))
    assert result.value == "hello world\n"


def test_execute_builtin_pwd():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["pwd"]))
    assert result.value == shell._ctx.cwd


def test_execute_builtin_cd(tmp_path):
    shell = Shell()
    shell.execute(ParsedInput(tokens=["cd", str(tmp_path)]))
    assert shell._ctx.cwd == str(tmp_path)


def test_execute_cd_invalid_path():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["cd", "/nonexistent/path/xyz"]))
    assert result.value is not None
    assert "No such file or directory" in result.value


def test_execute_exit():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["exit"]))
    assert result.interrupt is True


def test_execute_unknown_command():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["notarealcommand"]))
    assert result.error is not None
    assert "command not found" in result.error


def test_resolve_command_builtin():
    shell = Shell()
    cmd_type, path = shell._ctx.resolve_command("echo")
    assert cmd_type == CommandType.BUILTIN
    assert path is None


def test_resolve_command_executable():
    shell = Shell()
    cmd_type, path = shell._ctx.resolve_command("ls")
    assert cmd_type == CommandType.EXECUTABLE
    assert path is not None


def test_resolve_command_invalid():
    shell = Shell()
    cmd_type, path = shell._ctx.resolve_command("notarealcommand")
    assert cmd_type == CommandType.INVALID
    assert path is None


def test_type_handler_builtin():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["type", "echo"]))
    assert result.value == "echo is a shell builtin"


def test_type_handler_executable():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["type", "ls"]))
    assert result.value is not None
    assert "ls is" in result.value


def test_type_handler_invalid():
    shell = Shell()
    result = shell.execute(ParsedInput(tokens=["type", "notarealcommand"]))
    assert result.value is not None
    assert "not found" in result.value


def test_known_commands_includes_builtins():
    shell = Shell()
    assert "echo" in shell.known_commands
    assert "cd" in shell.known_commands


def test_known_commands_includes_executables():
    shell = Shell()
    assert "ls" in shell.known_commands


def test_register_builtin():
    shell = Shell()
    from app.models import Result

    shell.register_builtin("greet", lambda ctx, *args: Result(value="hi"))
    result = shell.execute(ParsedInput(tokens=["greet"]))
    assert result.value == "hi"
    assert "greet" in shell.known_commands
