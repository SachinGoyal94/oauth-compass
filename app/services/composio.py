"""Composio toolkit catalog: cached read access + optional live fetch.

The catalog (toolkits_cache.json) is synced once via scripts/sync_toolkits.py
and committed, so the app runs without a Composio key. A key is only needed
to refresh the cache or fetch per-toolkit auth details on demand.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OAUTH_SCHEMES = {"OAUTH2", "OAUTH1"}


@dataclass(frozen=True)
class ToolkitProfile:
    """Simplified per-app profile used by search + the generation crew."""

    slug: str
    name: str
    logo: str
    description: str
    categories: list[str]
    auth_schemes: list[str]
    managed_schemes: list[str]
    auth_guide_url: str
    app_url: str

    @property
    def supports_oauth(self) -> bool:
        return bool(OAUTH_SCHEMES & {s.upper() for s in self.auth_schemes})

    @property
    def composio_managed(self) -> bool:
        """True when Composio itself provides the OAuth app for this toolkit."""
        return bool(OAUTH_SCHEMES & {s.upper() for s in self.managed_schemes})


def fetch_catalog(api_key: str | None = None) -> list[dict[str, Any]]:
    """Fetch the full toolkit catalog from the Composio v3 API (paginated)."""
    api_key = api_key or settings.composio_api_key
    if not api_key:
        raise RuntimeError("COMPOSIO_API_KEY is not configured")

    items: list[dict[str, Any]] = []
    cursor: str | None = None
    with httpx.Client(timeout=60) as client:
        while True:
            params: dict[str, Any] = {"limit": 1000, "include_deprecated": "false"}
            if cursor:
                params["cursor"] = cursor
            resp = client.get(
                f"{settings.composio_base_url}/api/v3/toolkits",
                headers={"x-api-key": api_key},
                params=params,
            )
            resp.raise_for_status()
            payload = resp.json()
            page_items = payload.get("items") or []
            items.extend(page_items)
            cursor = payload.get("next_cursor")
            if not cursor or not page_items:
                break
    return items


def build_profiles(items: list[dict[str, Any]]) -> list[ToolkitProfile]:
    profiles: list[ToolkitProfile] = []
    for item in items:
        meta = item.get("meta") or {}
        profiles.append(
            ToolkitProfile(
                slug=item.get("slug") or "",
                name=item.get("name") or item.get("slug") or "",
                logo=meta.get("logo") or "",
                description=meta.get("description") or "",
                categories=meta.get("categories") or [],
                auth_schemes=item.get("auth_schemes") or [],
                managed_schemes=item.get("composio_managed_auth_schemes") or [],
                auth_guide_url=item.get("auth_guide_url") or "",
                app_url=meta.get("app_url") or "",
            )
        )
    return [p for p in profiles if p.slug]


def load_catalog() -> list[ToolkitProfile]:
    """Load the committed cache; raise a clear error if it is missing."""
    if not settings.toolkits_cache.exists():
        raise FileNotFoundError(
            "toolkits_cache.json not found — run `python scripts/sync_toolkits.py` first"
        )
    data = json.loads(settings.toolkits_cache.read_text(encoding="utf-8"))
    return build_profiles(data.get("items", []))


def search_catalog(query: str, catalog: list[ToolkitProfile] | None = None, limit: int = 12) -> list[ToolkitProfile]:
    """Prefix/substring match on slug and name for the home-page search."""
    catalog = catalog if catalog is not None else load_catalog()
    q = query.strip().lower().replace(" ", "")
    if not q:
        return []
    scored: list[tuple[int, ToolkitProfile]] = []
    for profile in catalog:
        slug = profile.slug.lower()
        name = profile.name.lower().replace(" ", "")
        if slug == q or name == q:
            scored.append((0, profile))
        elif slug.startswith(q) or name.startswith(q):
            scored.append((1, profile))
        elif q in slug or q in name:
            scored.append((2, profile))
    scored.sort(key=lambda pair: (pair[0], pair[1].slug))
    return [profile for _, profile in scored[:limit]]


def get_toolkit(slug_or_name: str, catalog: list[ToolkitProfile] | None = None) -> ToolkitProfile | None:
    try:
        catalog = catalog if catalog is not None else load_catalog()
    except FileNotFoundError:
        logger.warning("Composio catalog cache missing - toolkit lookup unavailable")
        return None
    matches = search_catalog(slug_or_name, catalog=catalog, limit=1)
    return matches[0] if matches else None


def fetch_toolkit_auth_details(slug: str, api_key: str | None = None) -> dict[str, Any]:
    """Fetch one toolkit's auth_config_details (required fields, scopes)."""
    api_key = api_key or settings.composio_api_key
    if not api_key:
        raise RuntimeError("COMPOSIO_API_KEY is not configured")
    with httpx.Client(timeout=60) as client:
        resp = client.get(
            f"{settings.composio_base_url}/api/v3/toolkits/{slug}",
            headers={"x-api-key": api_key},
        )
        resp.raise_for_status()
        return resp.json()
