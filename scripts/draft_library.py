"""Batch-draft the 8 library guides with the generation crew.

Usage:
    python scripts/draft_library.py            # all 8, deep research (best quality)
    python scripts/draft_library.py --fast     # all 8, fast mode
    python scripts/draft_library.py GitHub     # single app by name

Drafts land in knowledge/guides/drafts/{slug}/vN.md and are NOT published —
the human verification pass promotes them (status=stable + verified).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.generator import generate_guide  # noqa: E402

LIBRARY_APPS = [
    "GitHub",
    "Slack",
    "Notion",
    "Google Gmail",
    "Microsoft",
    "Salesforce",
    "Meta Facebook",
    "Shopify",
]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    deep = "--fast" not in sys.argv
    apps = args or LIBRARY_APPS

    ok, failed = [], []
    for name in apps:
        print(f"\n=== drafting: {name} (deep={deep}) ===", flush=True)
        try:
            fm = generate_guide(
                name,
                deep=deep,
                badge="library",
                progress=lambda e: print(f"  [{e.get('stage','?')}] {e.get('message','')}", flush=True),
            )
            print(f"  -> saved: {fm.resource}", flush=True)
            ok.append(fm.resource)
        except Exception as exc:  # noqa: BLE001 - keep batching on failures
            print(f"  !! FAILED: {name}: {exc}", flush=True)
            failed.append(name)

    print(f"\nDone. ok={len(ok)} failed={len(failed)}")
    if ok:
        print("  drafted:", ", ".join(ok))
    if failed:
        print("  failed:", ", ".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
