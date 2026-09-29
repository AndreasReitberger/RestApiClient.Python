"""Install the project and its pinned dependencies using the active Python."""

import os
import subprocess
import sys


def main():
    if sys.version_info < (3, 7):
        sys.stderr.write("Python 3.7 or newer is required.\n")
        return 1

    project_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(project_dir, "requirements.txt")

    commands = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip==24.0"],
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        [sys.executable, "-m", "pip", "install", "--no-build-isolation", "-e", project_dir],
    ]

    for command in commands:
        subprocess.check_call(command)

    sys.stdout.write("Dependencies installed for Python {}.{}.\n".format(
        sys.version_info[0], sys.version_info[1]
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
