"""Build wheel and source distribution into the project's dist directory."""

import os
import subprocess
import sys


def main():
    if sys.version_info < (3, 7):
        sys.stderr.write("Python 3.7 or newer is required.\n")
        return 1

    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    if not os.path.isdir(dist_dir):
        os.makedirs(dist_dir)

    # Build the project using the build module, which creates both wheel and source distributions.
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "build",
            "--outdir",
            dist_dir,
        ],
        cwd=project_dir,
    )


    sys.stdout.write("Wheel and source distribution created in: {}\n".format(dist_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
