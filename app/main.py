from enum import Enum
import sys
from .common import PROMPT, ParsedInput, tokenize_user_input, output_result
from .command_handlers import run_executable, CommandType
from .shell_context import ShellContext
import readline








def main():
    shell_context = ShellContext()

    def completer(text, state):
        known_cmds = list(shell_context.built_ins) + list(shell_context.executables)
        options = [f'{cmd} ' for cmd in known_cmds if cmd.startswith(text)]
        return options[state] if state < len(options) else None
    
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        user_input = input(f'{PROMPT}')
        if len(user_input) == 0 or not user_input:
            continue

        parsed_input: ParsedInput = tokenize_user_input(user_input)
        command = parsed_input.tokens[0] if len(parsed_input.tokens) > 0 else ""
        args = parsed_input.tokens[1:] if len(parsed_input.tokens) > 1 else []

        if command == "":
            continue

        # command_type, _ = resolve_command(command)

        # match command_type:
        #     case CommandType.BUILTIN:
        #         result = built_ins[command](shell_context, *args)
        #     case CommandType.EXECUTABLE:
        #         result = run_executable(command, *args)
        #     case _:
        #         sys.stdout.write(f"{command}: command not found\n")
        #         continue
        shell_context.execute(command, *args)

        # Handle results
        if shell_context.curr_result.interrupt:
            break
        else:
            output_result(shell_context.curr_result, parsed_input)
        
        

if __name__ == "__main__":
    main()
