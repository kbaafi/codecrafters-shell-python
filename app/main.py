import sys


PROMPT = "$ "
ALLOWED_COMMANDS = []


def main():
    while True:
        user_input = input(PROMPT)
        command = user_input.strip().split()[0]
        if command not in ALLOWED_COMMANDS:
            print(f"{command}: command not found")
        else:
            print(f"Executing command: {command}")


if __name__ == "__main__":
    main()
