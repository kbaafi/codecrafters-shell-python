import pytest
from app.common import tokenize_args


def test_simple_args():
    assert tokenize_args("foo bar baz") == ["foo", "bar", "baz"]

def test_single_quoted_spaces():
    assert tokenize_args("'hello world' foo") == ["hello world", "foo"]

def test_double_quoted_spaces():
    assert tokenize_args('"hello world" foo') == ["hello world", "foo"]

def test_adjacent_quoted_segments():
    assert tokenize_args("'script''example'") == ["scriptexample"]

def test_unquoted_and_quoted_adjacent():
    assert tokenize_args("shell''test") == ["shelltest"]

def test_escape_space():
    assert tokenize_args(r"hello\ world") == ["hello world"]

def test_empty_string():
    assert tokenize_args("") == []

def test_single_token():
    assert tokenize_args("foo") == ["foo"]

def test_mixed_quotes():
    assert tokenize_args('"it\'s fine"') == ["it's fine"]

def test_escape_quote_inside_double_quotes():
    assert tokenize_args(r'"hello\"world"') == ['hello"world']

def test_escape_backslash_inside_double_quotes():
    assert tokenize_args(r'"hello\\world"') == ['hello\\world']

def test_backslash_inside_single_quotes_is_literal():
    assert tokenize_args(r"'hello\world'") == ['hello\\world']

def test_escape_outside_quotes_keeps_char():
    assert tokenize_args(r"hello\nworld") == ["hellonworld"]
