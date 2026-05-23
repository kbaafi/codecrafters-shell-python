import os
import pytest
from app.handlers import Result
from app.common import output_result


def test_value_printed_to_stdout(capsys):
    output_result(Result(value="hello"), None, None)
    assert capsys.readouterr().out == "hello\n"

def test_value_with_newline_not_doubled(capsys):
    output_result(Result(value="hello\n"), None, None)
    assert capsys.readouterr().out == "hello\n"

def test_no_output_when_value_and_error_none(capsys):
    output_result(Result(), None, None)
    assert capsys.readouterr().out == ""

def test_stdout_redirect_writes_file(tmp_path):
    out = tmp_path / "out.txt"
    output_result(Result(value="hello"), str(out), None)
    assert out.read_text() == "hello"

def test_stdout_redirect_creates_empty_file_when_no_value(tmp_path):
    out = tmp_path / "out.txt"
    output_result(Result(), str(out), None)
    assert out.exists()
    assert out.read_text() == ""

def test_stdout_redirect_prints_error_to_screen(capsys, tmp_path):
    out = tmp_path / "out.txt"
    output_result(Result(value="out", error="err"), str(out), None)
    assert out.read_text() == "out"
    assert capsys.readouterr().out == "err\n"

def test_stderr_redirect_writes_file(tmp_path):
    err = tmp_path / "err.txt"
    output_result(Result(error="oops"), None, str(err))
    assert err.read_text() == "oops"

def test_stderr_redirect_creates_empty_file_when_no_error(tmp_path):
    err = tmp_path / "err.txt"
    output_result(Result(value="hello"), None, str(err))
    assert err.exists()
    assert err.read_text() == ""

def test_stderr_redirect_prints_value_to_screen(capsys, tmp_path):
    err = tmp_path / "err.txt"
    output_result(Result(value="out", error="err"), None, str(err))
    assert err.read_text() == "err"
    assert capsys.readouterr().out == "out\n"

def test_error_only_prints_to_stdout(capsys):
    output_result(Result(error="cat: no such file\n"), None, None)
    assert capsys.readouterr().out == "cat: no such file\n"
