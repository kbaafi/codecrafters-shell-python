import sys
from .results import BaseResult
from .common import PROMPT
from .handlers import built_ins

def main():
    while True:
        user_input = input(PROMPT)
        command = user_input.strip().split()[0]
        args = user_input.strip().split()[1:]

        if command not in built_ins:
            print(f"{command}: command not found")
        else:
            result: BaseResult = built_ins[command](*args)
            if result.interrupt:
                break
            else:
                print(result.result)


if __name__ == "__main__":
    main()
