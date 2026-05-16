import sys


PROMPT = "$ "
ALLOWED_COMMANDS = []


def main():
    user_input = input(PROMPT)
    command = user_input.strip().split()[0]
    if command not in ALLOWED_COMMANDS:
        print(f"{command}: command not found")
        sys.exit(1)
    else:
        print(f"Executing command: {command}")
        # Here you would add the logic to execute the allowed command


if __name__ == "__main__":
    main()
