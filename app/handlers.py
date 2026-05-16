def exit_handler(*args):
    _ = args
    return -1

def echo_handler(*args):
    print(" ".join(args))
    print("\n")