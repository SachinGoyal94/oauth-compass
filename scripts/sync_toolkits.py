"""Sync the Composio toolkit catalog into app/data/toolkits_cache.json.

Run once during setup (needs COMPOSIO_API_KEY in .env):

    python scripts/sync_toolkits.py

The committed cache lets the app run without a Composio key; rerun anytime
to refresh (managed-auth flags change as providers onboard).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.services import composio  # noqa: E402


def main() -> int:
    if not settings.has_composio:
        print("ERROR: COMPOSIO_API_KEY is not set (add it to .env)")
        return 1

    print("Fetching Composio toolkit catalog...")
    items = composio.fetch_catalog()
    profiles = composio.build_profiles(items)
    oauth_capable = [p for p in profiles if p.supports_oauth]
    managed = [p for p in oauth_capable if p.composio_managed]

    settings.toolkits_cache.parent.mkdir(parents=True, exist_ok=True)
    settings.toolkits_cache.write_text(
        json.dumps(
            {
                "synced_at": datetime.now(timezone.utc).isoformat(),
                "total": len(items),
                "items": items,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Saved {len(items)} toolkits -> {settings.toolkits_cache}")
    print(f"  OAuth-capable: {len(oauth_capable)}")
    print(f"  Composio-managed OAuth: {len(managed)} (BYO OAuth app: {len(oauth_capable) - len(managed)})")

    # Spot-check the managed/BYO split against known toolkits.
    by_slug = {p.slug: p for p in profiles}
    for slug, expect_managed in (("gmail", True), ("shopify", False), ("slack", True)):
        profile = by_slug.get(slug)
        if profile is None:
            print(f"  spot-check: {slug} NOT FOUND in catalog")
            continue
        state = "managed" if profile.composio_managed else "BYO"
        marker = "OK" if profile.composio_managed == expect_managed else "UNEXPECTED"
        print(f"  spot-check: {slug} -> {state} [{marker}]  auth={profile.auth_schemes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
