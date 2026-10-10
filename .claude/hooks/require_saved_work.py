#!/usr/bin/env python3
"""Stop hook: don't let a turn end with research work that is not committed and pushed.

Blocks (once per stop attempt) when the repo has uncommitted changes or local commits
that are on no remote, and tells Claude to save them per CLAUDE.md. If the hook already
blocked this stop (stop_hook_active), it lets the turn end so it can never loop forever.
"""
import json
import os
import subprocess
import sys


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if data.get("stop_hook_active"):
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        return 0
    root = top.stdout.strip()
    dirty = [l for l in git(root, "status", "--porcelain").stdout.splitlines() if l.strip()]
    ahead = git(root, "rev-list", "--count", "HEAD", "--not", "--remotes")
    unpushed = int(ahead.stdout.strip() or 0) if ahead.returncode == 0 else 0
    if not dirty and not unpushed:
        return 0
    parts = []
    if dirty:
        shown = ", ".join(l[3:] for l in dirty[:8]) + (" ..." if len(dirty) > 8 else "")
        parts.append(f"{len(dirty)} uncommitted change(s): {shown}")
    if unpushed:
        parts.append(f"{unpushed} commit(s) not pushed to any remote")
    reason = ("Work is not saved yet (" + "; ".join(parts) + "). Per CLAUDE.md: make sure every "
              "calculation is a research/rNN script with results and figures, the LAB_NOTEBOOK.md "
              "entry is written, then commit and push to the working branch before finishing.")
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
