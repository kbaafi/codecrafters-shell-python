import os

from app.models import CommandType
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
    shell.execute("echo", "hello", "world")
    assert shell._ctx.curr_result.value == "hello world"


def test_execute_builtin_pwd():
    shell = Shell()
    shell.execute("pwd")
    assert shell._ctx.curr_result.value == shell._ctx.cwd


def test_execute_builtin_cd(tmp_path):
    shell = Shell()
    shell.execute("cd", str(tmp_path))
    assert shell._ctx.cwd == str(tmp_path)


def test_execute_cd_invalid_path():
    shell = Shell()
    shell.execute("cd", "/nonexistent/path/xyz")
    assert shell._ctx.curr_result.value is not None
    assert "No such file or directory" in shell._ctx.curr_result.value


def test_execute_exit():
    shell = Shell()
    shell.execute("exit")
    assert shell._ctx.curr_result.interrupt is True


def test_execute_unknown_command():
    shell = Shell()
    shell.execute("notarealcommand")
    assert shell._ctx.curr_result.error is not None
    assert "command not found" in shell._ctx.curr_result.error


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
    shell.execute("type", "echo")
    assert shell._ctx.curr_result.value == "echo is a shell builtin"


def test_type_handler_executable():
    shell = Shell()
    shell.execute("type", "ls")
    assert shell._ctx.curr_result.value is not None
    assert "ls is" in shell._ctx.curr_result.value


def test_type_handler_invalid():
    shell = Shell()
    shell.execute("type", "notarealcommand")
    assert shell._ctx.curr_result.value is not None
    assert "not found" in shell._ctx.curr_result.value


def test_known_commands_includes_builtins():
    shell = Shell()
    assert "echo" in shell.known_commands
    assert "cd" in shell.known_commands


def test_known_commands_includes_executables():
    shell = Shell()
    assert "ls" in shell.known_commands
