from .handlers import exit_handler, echo_handler, type_handler

PROMPT = "$ "
built_ins = {
    "exit": exit_handler,
    "echo": echo_handler,
    "type": type_handler,
}