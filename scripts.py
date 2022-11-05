import subprocess

COMMANDS = ["flake8 --ignore=E501,F401,F403,F405,F841,W503,W504,W605,E302",
            "poetry run pytest -n auto --cov=gstui -vvv tests"]


def run_shell_command(command: str) -> int:
    return subprocess.call(command, shell=True)


def test():
    for cmd in COMMANDS:
        if run_shell_command(cmd) != 0:
            print("Failed to run command: {}".format(cmd))
            exit(1)
