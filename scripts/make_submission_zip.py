"""Build the submission zip: source + knowledge + caches, NO secrets.

Usage: python scripts/make_submission_zip.py
Output: dist/oauth-compass-submission.zip
"""
from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "dist" / f"oauth-compass-submission-{datetime.now():%Y%m%d-%H%M}.zip"

INCLUDE_DIRS = ["app", "templates", "static", "scripts", "knowledge", "corrections"]
INCLUDE_FILES = [
    "README.md",
    "VERIFICATION.md",
    "plan.md",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "assignment.md",
]
EXCLUDE_PARTS = {"__pycache__", ".venv", ".idea", ".vscode", ".pytest_cache", ".zcode"}
EXCLUDE_NAMES = {".env"}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in INCLUDE_DIRS:
            root = BASE / d
            if not root.exists():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_dir() or any(part in EXCLUDE_PARTS for part in path.parts):
                    continue
                if path.name in EXCLUDE_NAMES:
                    continue
                zf.write(path, path.relative_to(BASE))
                count += 1
        for f in INCLUDE_FILES:
            path = BASE / f
            if path.exists():
                zf.write(path, f)
                count += 1
    print(f"wrote {OUT} ({count} files)")
    # paranoid double-check: no .env anywhere in the archive
    with zipfile.ZipFile(OUT) as zf:
        leaked = [n for n in zf.namelist() if n.endswith("/.env") or n == ".env"]
    if leaked:
        print("DANGER: .env leaked into the zip:", leaked)
        return 1
    print("verified: no .env in archive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
