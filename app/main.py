import sys
from .handlers import exit_handler, echo_handler, BaseResult


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
            result: BaseResult = dispatch[command](*args)
            if result.interrupt:
                break
            else:
                print(result.result, end='')


if __name__ == "__main__":
    main()
