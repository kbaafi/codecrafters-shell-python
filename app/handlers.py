from .results import ExitResult, StringResult


def exit_handler(*args):
    _ = args
    return ExitResult(None)


def echo_handler(*args):
    result_msg = f'{" ".join(args)} \n'
    return StringResult(result_msg)


def type_handler(*args):
    queried_command = str(args[0])
    if queried_command in built_ins:
        return StringResult(f'{queried_command} is a shell builtin \n')


built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
    "type": type_handler,
}
