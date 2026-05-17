import os
from typing import Union

PROMPT = "$ "


def is_executable_command(command) -> tuple[bool, Union[str, None]]:
    path = os.environ["PATH"]
    dirs = path.split(os.pathsep)

    for dir in dirs:
        full_path = os.path.join(dir, command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return True, full_path
    return False, None


def clean_up_quotes(str_list: list[str]) -> list[str]:
    # print(str_list)
    single_quote = "'"
    double_quote = '"'
    results = []
    for item in str_list:
        results.append((
            item.strip(single_quote)
            .strip(double_quote)
            .replace(single_quote, '')
            .replace(double_quote, '')
        ))
    return results
