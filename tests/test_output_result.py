from app.models import ParsedInput, Result
from app.shell import Shell


def run(
    result,
    stdout_redirect=None,
    stderr_redirect=None,
    stdout_append=False,
    stderr_append=False,
):
    shell = Shell()
    shell._ctx.curr_result = result
    parsed = ParsedInput(
        stdout_redirect=stdout_redirect,
        stderr_redirect=stderr_redirect,
        stdout_append=stdout_append,
        stderr_append=stderr_append,
    )
    shell.output_results(parsed)


def test_value_printed_to_stdout(capsys):
    run(Result(value="hello"))
    assert capsys.readouterr().out == "hello\n"


def test_value_with_newline_not_doubled(capsys):
    run(Result(value="hello\n"))
    assert capsys.readouterr().out == "hello\n"


def test_no_output_when_value_and_error_none(capsys):
    run(Result())
    assert capsys.readouterr().out == ""


def test_error_only_prints_to_stdout(capsys):
    run(Result(error="cat: no such file\n"))
    assert capsys.readouterr().out == "cat: no such file\n"


def test_stdout_redirect_writes_file(tmp_path):
    out = tmp_path / "out.txt"
    run(Result(value="hello"), stdout_redirect=str(out))
    assert out.read_text() == "hello"


def test_stdout_redirect_creates_empty_file_when_no_value(tmp_path):
    out = tmp_path / "out.txt"
    run(Result(), stdout_redirect=str(out))
    assert out.exists()
    assert out.read_text() == ""


def test_stdout_redirect_prints_error_to_screen(capsys, tmp_path):
    out = tmp_path / "out.txt"
    run(Result(value="out", error="err"), stdout_redirect=str(out))
    assert out.read_text() == "out"
    assert capsys.readouterr().out == "err\n"


def test_stderr_redirect_writes_file(tmp_path):
    err = tmp_path / "err.txt"
    run(Result(error="oops"), stderr_redirect=str(err))
    assert err.read_text() == "oops"


def test_stderr_redirect_creates_empty_file_when_no_error(tmp_path):
    err = tmp_path / "err.txt"
    run(Result(value="hello"), stderr_redirect=str(err))
    assert err.exists()
    assert err.read_text() == ""


def test_stderr_redirect_prints_value_to_screen(capsys, tmp_path):
    err = tmp_path / "err.txt"
    run(Result(value="out", error="err"), stderr_redirect=str(err))
    assert err.read_text() == "err"
    assert capsys.readouterr().out == "out\n"


def test_stdout_append_with_trailing_newline(tmp_path):
    out = tmp_path / "out.txt"
    out.write_text("existing\n")
    run(Result(value="new"), stdout_redirect=str(out), stdout_append=True)
    assert out.read_text() == "existing\nnew"


def test_stdout_append_without_trailing_newline(tmp_path):
    out = tmp_path / "out.txt"
    out.write_text("existing")
    run(Result(value="new"), stdout_redirect=str(out), stdout_append=True)
    assert out.read_text() == "existing\nnew"


def test_stdout_append_to_empty_file(tmp_path):
    out = tmp_path / "out.txt"
    out.write_text("")
    run(Result(value="new"), stdout_redirect=str(out), stdout_append=True)
    assert out.read_text() == "new"


def test_stderr_append_with_trailing_newline(tmp_path):
    err = tmp_path / "err.txt"
    err.write_text("existing\n")
    run(Result(error="new"), stderr_redirect=str(err), stderr_append=True)
    assert err.read_text() == "existing\nnew"


def test_stderr_append_without_trailing_newline(tmp_path):
    err = tmp_path / "err.txt"
    err.write_text("existing")
    run(Result(error="new"), stderr_redirect=str(err), stderr_append=True)
    assert err.read_text() == "existing\nnew"


def test_stderr_append_to_empty_file(tmp_path):
    err = tmp_path / "err.txt"
    err.write_text("")
    run(Result(error="new"), stderr_redirect=str(err), stderr_append=True)
    assert err.read_text() == "new"
