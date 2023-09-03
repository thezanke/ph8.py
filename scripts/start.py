import subprocess


def watch():
    cmd = [
        "watchmedo",
        "auto-restart",
        "--directory=.",
        "--pattern=*.py",
        "--recursive",
        "--",
        "python",
        "src/ph8.py",
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nWatchmedo process terminated by user. Exiting.")
