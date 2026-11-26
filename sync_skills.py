#!/usr/bin/env python3
"""Use the sibling shared skill library, preserving every project's own rules."""
from pathlib import Path
import subprocess
import sys

URL = "https://github.com/sxy3481841323-ship-it/agent-skills.git"
MASTER = Path(__file__).resolve().parent.parent / "agent-skills"

if __name__ == "__main__":
    if not MASTER.exists():
        subprocess.run(["git", "clone", URL, str(MASTER)], check=True)
    if not (MASTER / ".git").exists():
        raise SystemExit("The sibling agent-skills directory is not a Git checkout; it was left unchanged.")
    origin = subprocess.check_output(["git", "-C", str(MASTER), "remote", "get-url", "origin"], text=True).strip().removesuffix(".git")
    if origin not in {URL.removesuffix(".git"), "git@github.com:sxy3481841323-ship-it/agent-skills"}:
        raise SystemExit("The sibling directory belongs to another repository; it was left unchanged.")
    entry = MASTER / "sync_skills.py"
    if not entry.is_file():
        raise SystemExit("Shared skill entry point is missing; update the shared checkout first.")
    raise SystemExit(subprocess.call([sys.executable, str(entry), *sys.argv[1:]]))
