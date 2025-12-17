#!/usr/bin/env python3
"""Run a command with a wall-clock timeout.

This is intentionally dependency-free and works on macOS where `timeout` may not exist.

Exit codes:
- If the child exits normally, propagate its exit code.
- On timeout, exit with 124 (matching GNU timeout).
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time


def _kill_process_group(proc: subprocess.Popen[object], sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        return


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--timeout-secs",
        type=float,
        default=None,
        help="Wall-clock timeout in seconds. If omitted, no timeout is enforced.",
    )
    parser.add_argument(
        "--kill-grace-secs",
        type=float,
        default=5.0,
        help="Seconds to wait after SIGTERM before SIGKILL.",
    )
    parser.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command to run (prefix with `--` to separate from wrapper args).",
    )

    args = parser.parse_args(argv)

    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        parser.error("missing command; use: run_with_timeout.py [opts] -- <cmd> [args...]")

    start = time.time()

    # start_new_session=True creates a new process group so we can kill the whole tree.
    proc = subprocess.Popen(cmd, start_new_session=True)
    try:
        if args.timeout_secs is None:
            return proc.wait()
        return proc.wait(timeout=args.timeout_secs)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(
            f"[timeout] exceeded {args.timeout_secs:.1f}s (elapsed {elapsed:.1f}s): {' '.join(cmd)}",
            file=sys.stderr,
        )

        _kill_process_group(proc, signal.SIGTERM)
        try:
            proc.wait(timeout=args.kill_grace_secs)
        except subprocess.TimeoutExpired:
            _kill_process_group(proc, signal.SIGKILL)
            proc.wait()

        return 124


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
