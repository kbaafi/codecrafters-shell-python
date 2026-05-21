import pytest
from app.common import tokenize_user_input


def tokens(s):
    return tokenize_user_input(s)[0]

def redirect(s):
    return tokenize_user_input(s)[1]


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

def test_no_redirect():
    assert redirect("foo bar") is None

def test_redirect_basic():
    assert tokens("echo hello > out.txt") == ["echo", "hello"]
    assert redirect("echo hello > out.txt") == "out.txt"

def test_redirect_no_space():
    assert tokens("echo hello>out.txt") == ["echo", "hello"]
    assert redirect("echo hello>out.txt") == "out.txt"

def test_redirect_strips_filename():
    assert redirect("echo hello >   out.txt  ") == "out.txt"
