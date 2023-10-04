import subprocess


def watch():
    cmd = [
        "watchmedo",
        "auto-restart",
        "--directory=.",
        "--pattern=*.py",
        "--recursive",
        "--",
        "poetry",
        "run",
        "start"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nWatchmedo process terminated by user. Exiting.")
