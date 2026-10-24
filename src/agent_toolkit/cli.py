from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import ToolkitError, check, init, install, update
from .local import build_graft, setup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-toolkit")
    parser.add_argument("--project", type=Path, default=Path.cwd(), help="Project root (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    initialize = commands.add_parser("init", help="Create desired-state manifest")
    initialize.add_argument("--profile", choices=["web", "backend"], default="web")
    for name, text in (
        ("install", "Vendor skills and generate client instructions and lock"),
        ("update", "Refresh vendored files and lock from installed toolkit"),
    ):
        command = commands.add_parser(name, help=f"{text}, then build the local Graft index")
        command.add_argument("--no-graft-build", action="store_true", help="Skip the local Graft index build")
    commands.add_parser("check", help="Report drift without changing files")
    commands.add_parser("setup", help="Approve the project's Graft MCP server for each client on this machine")
    args = parser.parse_args(argv)
    root = args.project.resolve()
    try:
        if args.command == "init":
            init(root, args.profile)
        elif args.command in ("install", "update"):
            install(root) if args.command == "install" else update(root)
            if not args.no_graft_build:
                print(f"agent-toolkit: {build_graft(root)}")
        elif args.command == "setup":
            for step in setup(root):
                print(f"agent-toolkit: {step}")
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
