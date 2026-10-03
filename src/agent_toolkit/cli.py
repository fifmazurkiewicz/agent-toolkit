from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import ToolkitError, check, init, install, update


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-toolkit")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init", help="Create desired-state manifest")
    initialize.add_argument("--profile", choices=["web", "backend"], default="web")
    commands.add_parser("install", help="Vendor skills and generate client instructions and lock")
    commands.add_parser("check", help="Report drift without changing files")
    commands.add_parser("update", help="Refresh vendored files and lock from installed toolkit")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    try:
        if args.command == "init":
            init(root, args.profile)
        elif args.command == "install":
            install(root)
        elif args.command == "update":
            update(root)
        else:
            problems = check(root)
            for problem in problems:
                print(problem, file=sys.stderr)
            if problems:
                return 1
            print("agent-toolkit: clean")
        return 0
    except ToolkitError as exc:
        print(f"agent-toolkit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
