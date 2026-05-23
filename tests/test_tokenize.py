import pytest
from app.common import tokenize_user_input


def parsed(s):
    return tokenize_user_input(s)


def test_simple_args():
    assert parsed("foo bar baz").tokens == ["foo", "bar", "baz"]

def test_single_quoted_spaces():
    assert parsed("'hello world' foo").tokens == ["hello world", "foo"]

def test_double_quoted_spaces():
    assert parsed('"hello world" foo').tokens == ["hello world", "foo"]

def test_adjacent_quoted_segments():
    assert parsed("'script''example'").tokens == ["scriptexample"]

def test_unquoted_and_quoted_adjacent():
    assert parsed("shell''test").tokens == ["shelltest"]

def test_escape_space():
    assert parsed(r"hello\ world").tokens == ["hello world"]

def test_empty_string():
    assert parsed("").tokens == []

def test_single_token():
    assert parsed("foo").tokens == ["foo"]

def test_mixed_quotes():
    assert parsed('"it\'s fine"').tokens == ["it's fine"]

def test_escape_quote_inside_double_quotes():
    assert parsed(r'"hello\"world"').tokens == ['hello"world']

def test_escape_backslash_inside_double_quotes():
    assert parsed(r'"hello\\world"').tokens == ['hello\\world']

def test_backslash_inside_single_quotes_is_literal():
    assert parsed(r"'hello\world'").tokens == ['hello\\world']

def test_escape_outside_quotes_keeps_char():
    assert parsed(r"hello\nworld").tokens == ["hellonworld"]

def test_no_stdout_redirect():
    assert parsed("foo bar").stdout_redirect is None

def test_no_stderr_redirect():
    assert parsed("foo bar").stderr_redirect is None

def test_stdout_redirect_basic():
    p = parsed("echo hello > out.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stdout_redirect == "out.txt"
    assert p.stdout_append is False

def test_stdout_redirect_explicit():
    p = parsed("echo hello 1> out.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stdout_redirect == "out.txt"
    assert p.stdout_append is False

def test_stderr_redirect_basic():
    p = parsed("echo hello 2> err.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stderr_redirect == "err.txt"
    assert p.stderr_append is False

def test_stderr_redirect_no_space():
    p = parsed("echo hello 2>err.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stderr_redirect == "err.txt"

def test_both_redirects():
    p = parsed("cmd 1> out.txt 2> err.txt")
    assert p.tokens == ["cmd"]
    assert p.stdout_redirect == "out.txt"
    assert p.stderr_redirect == "err.txt"

def test_stdout_append():
    p = parsed("echo hello >> out.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stdout_redirect == "out.txt"
    assert p.stdout_append is True

def test_stdout_append_explicit():
    p = parsed("echo hello 1>> out.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stdout_redirect == "out.txt"
    assert p.stdout_append is True

def test_stderr_append():
    p = parsed("echo hello 2>> err.txt")
    assert p.tokens == ["echo", "hello"]
    assert p.stderr_redirect == "err.txt"
    assert p.stderr_append is True
