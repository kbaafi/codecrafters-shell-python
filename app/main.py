import sys
from .handlers import exit_handler, echo_handler


PROMPT = "$ "
dispatch = {
    "exit": exit_handler,
    "echo": echo_handler,
}


def main():
    while True:
        user_input = input(PROMPT)
        command = user_input.strip().split()[0]
        args = user_input.strip().split()[1:]

        if command not in dispatch:
            print(f"{command}: command not found")
        else:
            result = dispatch[command](*args)
            if result == -1:
                break


if __name__ == "__main__":
    main()
