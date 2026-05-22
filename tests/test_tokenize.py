import pytest
from app.common import tokenize_user_input


def tokens(s):
    return tokenize_user_input(s)[0]

def stdout_redirect(s):
    return tokenize_user_input(s)[1]

def stderr_redirect(s):
    return tokenize_user_input(s)[2]


def test_simple_args():
    assert tokens("foo bar baz") == ["foo", "bar", "baz"]

def test_single_quoted_spaces():
    assert tokens("'hello world' foo") == ["hello world", "foo"]

def test_double_quoted_spaces():
    assert tokens('"hello world" foo') == ["hello world", "foo"]

def test_adjacent_quoted_segments():
    assert tokens("'script''example'") == ["scriptexample"]

def test_unquoted_and_quoted_adjacent():
    assert tokens("shell''test") == ["shelltest"]

def test_escape_space():
    assert tokens(r"hello\ world") == ["hello world"]

def test_empty_string():
    assert tokens("") == []

def test_single_token():
    assert tokens("foo") == ["foo"]

def test_mixed_quotes():
    assert tokens('"it\'s fine"') == ["it's fine"]

def test_escape_quote_inside_double_quotes():
    assert tokens(r'"hello\"world"') == ['hello"world']

def test_escape_backslash_inside_double_quotes():
    assert tokens(r'"hello\\world"') == ['hello\\world']

def test_backslash_inside_single_quotes_is_literal():
    assert tokens(r"'hello\world'") == ['hello\\world']

def test_escape_outside_quotes_keeps_char():
    assert tokens(r"hello\nworld") == ["hellonworld"]

def test_no_stdout_redirect():
    assert stdout_redirect("foo bar") is None

def test_no_stderr_redirect():
    assert stderr_redirect("foo bar") is None

def test_stdout_redirect_basic():
    assert tokens("echo hello > out.txt") == ["echo", "hello"]
    assert stdout_redirect("echo hello > out.txt") == "out.txt"

def test_stdout_redirect_explicit():
    assert tokens("echo hello 1> out.txt") == ["echo", "hello"]
    assert stdout_redirect("echo hello 1> out.txt") == "out.txt"

def test_stderr_redirect_basic():
    assert tokens("echo hello 2> err.txt") == ["echo", "hello"]
    assert stderr_redirect("echo hello 2> err.txt") == "err.txt"

def test_stderr_redirect_no_space():
    assert tokens("echo hello 2>err.txt") == ["echo", "hello"]
    assert stderr_redirect("echo hello 2>err.txt") == "err.txt"

def test_both_redirects():
    assert tokens("cmd 1> out.txt 2> err.txt") == ["cmd"]
    assert stdout_redirect("cmd 1> out.txt 2> err.txt") == "out.txt"
    assert stderr_redirect("cmd 1> out.txt 2> err.txt") == "err.txt"
