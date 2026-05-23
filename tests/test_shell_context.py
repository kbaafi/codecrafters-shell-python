import os
import pytest
from app.shell_context import ShellContext
from app.models import Result


def test_cwd_initialized_to_current_dir():
    ctx = ShellContext()
    assert ctx.cwd == os.getcwd()

def test_built_ins_registered():
    ctx = ShellContext()
    assert "echo" in ctx.built_ins
    assert "exit" in ctx.built_ins
    assert "type" in ctx.built_ins
    assert "pwd" in ctx.built_ins
    assert "cd" in ctx.built_ins

def test_executables_populated():
    ctx = ShellContext()
    assert len(ctx.executables) > 0

def test_execute_builtin_echo():
    ctx = ShellContext()
    ctx.execute("echo", "hello", "world")
    assert ctx.curr_result.value == "hello world"

def test_execute_builtin_pwd():
    ctx = ShellContext()
    ctx.execute("pwd")
    assert ctx.curr_result.value == ctx.cwd

def test_execute_builtin_cd(tmp_path):
    ctx = ShellContext()
    ctx.execute("cd", str(tmp_path))
    assert ctx.cwd == str(tmp_path)

def test_execute_cd_invalid_path():
    ctx = ShellContext()
    ctx.execute("cd", "/nonexistent/path/xyz")
    assert ctx.curr_result.error is None
    assert "No such file or directory" in ctx.curr_result.value

def test_execute_exit():
    ctx = ShellContext()
    ctx.execute("exit")
    assert ctx.curr_result.interrupt is True

def test_execute_unknown_command():
    ctx = ShellContext()
    ctx.execute("notarealcommand")
    assert "command not found" in ctx.curr_result.error

def test_execute_executable():
    ctx = ShellContext()
    ctx.execute("echo", "from executable")
    assert ctx.curr_result.value is not None

def test_resolve_command_builtin():
    from app.models import CommandType
    ctx = ShellContext()
    cmd_type, path = ctx.resolve_command("echo")
    assert cmd_type == CommandType.BUILTIN
    assert path is None

def test_resolve_command_executable():
    from app.models import CommandType
    ctx = ShellContext()
    cmd_type, path = ctx.resolve_command("ls")
    assert cmd_type == CommandType.EXECUTABLE
    assert path is not None

def test_resolve_command_invalid():
    from app.models import CommandType
    ctx = ShellContext()
    cmd_type, path = ctx.resolve_command("notarealcommand")
    assert cmd_type == CommandType.INVALID
    assert path is None

def test_type_handler_builtin():
    ctx = ShellContext()
    ctx.execute("type", "echo")
    assert ctx.curr_result.value == "echo is a shell builtin"

def test_type_handler_executable():
    ctx = ShellContext()
    ctx.execute("type", "ls")
    assert "ls is" in ctx.curr_result.value

def test_type_handler_invalid():
    ctx = ShellContext()
    ctx.execute("type", "notarealcommand")
    assert "not found" in ctx.curr_result.value
