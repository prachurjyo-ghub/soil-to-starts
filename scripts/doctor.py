#!/usr/bin/env python3
"""Read-only local onboarding diagnostics; never installs packages or contacts NASA."""
from pathlib import Path
import shutil
import subprocess


def main():
    root = Path(__file__).resolve().parents[1]
    failures = []
    for command in ("git", "python3", "node", "npm"):
        binary = shutil.which(command)
        if not binary:
            failures.append(command + " is missing")
            continue
        result = subprocess.run([binary, "--version"], capture_output=True, text=True)
        print(command + ": " + (result.stdout or result.stderr).strip())
        if result.returncode:
            failures.append(command + " version check failed")
        if command == "node" and result.returncode == 0:
            version = tuple(int(part) for part in result.stdout.strip().lstrip("v").split(".")[:2])
            if version < (20, 9):
                failures.append("Node must satisfy the locked Next.js engine >=20.9.0")
    for name in ("prototype/package-lock.json", "prototype/eslint.config.mjs", "AGENTS.md", "docs/PROGRESS.md", "docs/TEAM_PLAYBOOK.md"):
        if not (root / name).is_file():
            failures.append("Missing " + name)
    print("Frontend dependencies:", "installed" if (root / "prototype/node_modules").is_dir() else "run cd prototype && npm ci")
    print("Science/API: planned; no working backend, NASA fixture or enforced OFFLINE flag is inferred.")
    print("GitHub settings/CI publication: not checked; local files do not establish remote protection.")
    for issue in failures:
        print("ERROR:", issue)
    print("Local prerequisites:", "PASS" if not failures else "NEEDS ATTENTION")
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
