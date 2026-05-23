from unittest.mock import MagicMock, patch

from app.main import make_completer


def make_shell(commands=None, cwd="/tmp", files=None):
    shell = MagicMock()
    shell.known_commands = commands or []
    shell._ctx.cwd = cwd
    return shell


def complete_all(completer, text):
    results = []
    state = 0
    while (match := completer(text, state)) is not None:
        results.append(match)
        state += 1
    return results


# --- command completion ---


def test_completes_command_prefix():
    shell = make_shell(commands=["echo", "exit", "env"])
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="ec"):
        assert complete_all(completer, "ec") == ["echo "]


def test_completes_multiple_commands():
    shell = make_shell(commands=["echo", "exit", "env"])
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="e"):
        assert complete_all(completer, "e") == ["echo ", "exit ", "env "]


def test_no_match_returns_empty():
    shell = make_shell(commands=["echo", "exit"])
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="xyz"):
        assert complete_all(completer, "xyz") == []


def test_empty_line_returns_all_commands():
    shell = make_shell(commands=["echo", "ls"])
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value=""):
        assert complete_all(completer, "") == ["echo ", "ls "]


def test_state_indexes_into_options():
    shell = make_shell(commands=["echo", "exit", "env"])
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="e"):
        assert completer("e", 0) == "echo "
        assert completer("e", 1) == "exit "
        assert completer("e", 2) == "env "
        assert completer("e", 3) is None


# --- file completion ---


def test_completes_file_after_command(tmp_path):
    (tmp_path / "banana.txt").write_text("")
    (tmp_path / "cherry.txt").write_text("")
    shell = make_shell(commands=["cat"], cwd=str(tmp_path))
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="cat ban"):
        assert complete_all(completer, "ban") == ["banana.txt "]


def test_completes_multiple_files(tmp_path):
    (tmp_path / "alpha.txt").write_text("")
    (tmp_path / "alpha2.txt").write_text("")
    (tmp_path / "beta.txt").write_text("")
    shell = make_shell(commands=["cat"], cwd=str(tmp_path))
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="cat al"):
        matches = complete_all(completer, "al")
    assert set(matches) == {"alpha.txt ", "alpha2.txt "}


def test_file_completion_after_trailing_space(tmp_path):
    (tmp_path / "foo.txt").write_text("")
    shell = make_shell(commands=["cat"], cwd=str(tmp_path))
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="cat "):
        matches = complete_all(completer, "")
    assert "foo.txt " in matches


def test_no_file_match_returns_empty(tmp_path):
    (tmp_path / "foo.txt").write_text("")
    shell = make_shell(commands=["cat"], cwd=str(tmp_path))
    completer = make_completer(shell)
    with patch("readline.get_line_buffer", return_value="cat zzz"):
        assert complete_all(completer, "zzz") == []


# --- path completion ---


def test_completes_absolute_path(tmp_path):
    (tmp_path / "notes.txt").write_text("")
    shell = make_shell(commands=["cat"])
    completer = make_completer(shell)
    partial = f"{tmp_path}/no"
    with patch("readline.get_line_buffer", return_value=f"cat {partial}"):
        matches = complete_all(completer, partial)
    assert f"{tmp_path}/notes.txt " in matches


def test_completes_absolute_path_trailing_slash(tmp_path):
    (tmp_path / "data.csv").write_text("")
    shell = make_shell(commands=["cat"])
    completer = make_completer(shell)
    partial = f"{tmp_path}/"
    with patch("readline.get_line_buffer", return_value=f"cat {partial}"):
        matches = complete_all(completer, partial)
    assert f"{tmp_path}/data.csv " in matches


def test_invalid_path_returns_empty():
    shell = make_shell(commands=["cat"])
    completer = make_completer(shell)
    partial = "/nonexistent_dir_xyz/foo"
    with patch("readline.get_line_buffer", return_value=f"cat {partial}"):
        assert complete_all(completer, partial) == []
