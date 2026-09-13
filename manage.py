#!/usr/bin/env python3
"""Cross-platform management utility for FastKanban."""
import sys
import subprocess


def run_cmd(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(0)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "help"

    if command == "dev":
        run_cmd(["uv", "run", "uvicorn", "app.main:app", "--reload", "--port", "8000"])
    elif command == "test":
        run_cmd(["uv", "run", "pytest"])
    elif command == "sync":
        run_cmd(["uv", "sync"])
    elif command == "up":
        run_cmd(["docker", "compose", "up", "--build", "-d"])
    elif command == "down":
        run_cmd(["docker", "compose", "down"])
    elif command == "status":
        run_cmd(["docker", "compose", "ps"])
    elif command == "logs":
        run_cmd(["docker", "compose", "logs", "-f"])
    else:
        print("FastKanban Management Commands:")
        print("  python manage.py dev     - Run local development server")
        print("  python manage.py test    - Run pytest test suite")
        print("  python manage.py sync    - Sync dependencies via uv")
        print("  python manage.py up      - Build and launch Docker Compose")
        print("  python manage.py down    - Stop Docker Compose containers")
        print("  python manage.py status  - View Docker container status & health")
        print("  python manage.py logs    - Stream container logs")


if __name__ == "__main__":
    main()
