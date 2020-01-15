import copy

POSSIBLE_COMMANDS=(
    "check",
    "run",
    "help",
)

def check(options):
    return "checking the runs"

def run(options):
    return "Starting Training"

def help(options):
    help_text=\
    """
    This is the set of avaiable commands and their use

    check -- To check the status of already running Training(s)
    run -- To run a new Traiing on you local machine
    """
    return help_text

def execute_command(command):
    command, *options = command.split(" ", 1)
    return globals()[command](options)

for command in POSSIBLE_COMMANDS:
    if command not in globals():
        raise NotImplementedError("The function correspondin to the command '%s' is missing" % command)
