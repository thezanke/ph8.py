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
        "ph8:main"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nWatchmedo process terminated by user. Exiting.")
