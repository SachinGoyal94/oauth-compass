"""Publish a verified draft guide to the library.

The human verification pass produces a corrections JSON (any frontmatter field
to replace; `guide.*` keys replace that sub-object wholesale). This script
applies them, sets the governance fields (verified / stable / fresh), validates,
and writes knowledge/guides/{slug}.md.

Usage:
    python scripts/publish_guide.py drafts/github/v1.md --corrections corrections/github.json
    python scripts/publish_guide.py drafts/github/v1.md            # publish as-is
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.okf import GuideFrontmatter, load_okf_guide, write_okf_guide  # noqa: E402


# Defensive clamps for fields verification passes tend to over-write.
CLAMPS = {
    ("guide", "summary"): 2000,
    ("guide", "difficulty", "verdict"): 700,
    ("guide", "time", "hands_on"): 120,
    ("guide", "time", "approval_wait"): 240,
    ("guide", "time", "verdict"): 300,
    ("guide", "composio_next", "managed_note"): 600,
    ("guide", "composio_next", "mcp_note"): 800,
    ("guide", "composio_next", "auth_config_snippet"): 2000,
}


def _clamp(data: dict) -> None:
    g = data.get("guide", {})
    for path, limit in CLAMPS.items():
        node: any = g
        for key in path[1:-1]:
            node = node.get(key, {}) if isinstance(node, dict) else {}
        last = path[-1]
        if isinstance(node, dict) and isinstance(node.get(last), str) and len(node[last]) > limit:
            node[last] = node[last][: limit - 1] + "…"
    for step in g.get("steps", []):
        for key, limit in (("action", 2000), ("nuances", 1200), ("where", 400), ("human_because", 400), ("duration", 80)):
            if isinstance(step.get(key), str) and len(step[key]) > limit:
                step[key] = step[key][: limit - 1] + "…"
    for item in g.get("gotchas", []):
        for key, limit in (("why_it_matters", 1200), ("how_to_handle", 1200), ("title", 240)):
            if isinstance(item.get(key), str) and len(item[key]) > limit:
                item[key] = item[key][: limit - 1] + "…"
    for item in g.get("blockers", []):
        for key, limit in (("issue", 300), ("how_to_resolve", 1200), ("escalation", 600)):
            if isinstance(item.get(key), str) and len(item[key]) > limit:
                item[key] = item[key][: limit - 1] + "…"
    for src in data.get("sources", []):
        if isinstance(src, dict) and len(src.get("what_it_supports", "")) > 600:
            src["what_it_supports"] = src["what_it_supports"][:597] + "…"
    for i, u in enumerate(data.get("unverified", [])):
        if isinstance(u, str) and len(u) > 400:
            data["unverified"][i] = u[:397] + "…"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", help="Path to the draft guide .md")
    parser.add_argument("--corrections", help="JSON file with frontmatter overrides", default="")
    parser.add_argument("--keep-draft", action="store_true", help="Do not delete the draft after publishing")
    args = parser.parse_args()

    draft_path = Path(args.draft)
    guide = load_okf_guide(draft_path)
    data = guide.frontmatter.model_dump(mode="json", exclude_none=True)

    if args.corrections:
        corrections = json.loads(Path(args.corrections).read_text(encoding="utf-8"))
        guide_updates = corrections.pop("guide", {})
        data.update(corrections)
        if guide_updates:
            data["guide"].update(guide_updates)
    _clamp(data)

    now = datetime.now(timezone.utc)
    today = date.today()
    data.update(
        {
            "status": "stable",
            "badge": "library",
            "verified": {"by": "agent:verification-crew", "at": now.isoformat()},
            "last_checked": today.isoformat(),
            "stale_after": (today + timedelta(days=180)).isoformat(),
            "chatbot": {"visible": True, "priority": "primary"},
        }
    )

    fm = GuideFrontmatter.model_validate(data)
    out = settings.guides_dir / f"{fm.resource}.md"
    write_okf_guide(out, fm)
    print(f"published: {out}")

    if not args.keep_draft:
        import shutil

        shutil.rmtree(draft_path.parent, ignore_errors=True)
        print(f"removed draft: {draft_path.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
