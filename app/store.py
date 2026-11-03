"""Guide store: in-memory index over OKF guide records.

- Published library guides: knowledge/guides/*.md (stable, human-verified)
- Draft / live-generated guides: knowledge/guides/drafts/{slug}/v{N}.md, versioned,
  with active.json recording which version is live (default: newest)
- Catalogue: knowledge/guides/index.md, regenerated on every write
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.config import settings
from app.okf import OkfGuide, load_okf_guide
from app.services import composio

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DraftVersion:
    slug: str
    version: str
    path: Path
    guide: OkfGuide


VERSION_RE = re.compile(r"^v(\d+)$")


class GuideStore:
    """Rescans the knowledge tree; cheap enough to call after every write."""

    def __init__(self) -> None:
        self.published: dict[str, OkfGuide] = {}
        self.drafts: dict[str, dict[str, OkfGuide]] = {}
        self.active: dict[str, str] = {}
        self.errors: list[str] = []

    # -- scanning -----------------------------------------------------------

    def refresh(self) -> "GuideStore":
        self.published, self.drafts, self.active, self.errors = {}, {}, {}, []
        guides_root = settings.guides_dir
        if not guides_root.exists():
            return self
        for path in sorted(guides_root.glob("*.md")):
            if path.name == "index.md":
                continue
            try:
                guide = load_okf_guide(path)
                self.published[guide.slug] = guide
            except (OSError, ValueError) as exc:
                self.errors.append(str(exc))
        drafts_root = settings.drafts_dir
        if drafts_root.exists():
            for slug_dir in sorted(p for p in drafts_root.iterdir() if p.is_dir()):
                versions: dict[str, OkfGuide] = {}
                for path in sorted(slug_dir.glob("v*.md")):
                    if not VERSION_RE.match(path.stem):
                        continue
                    try:
                        versions[path.stem] = load_okf_guide(path)
                    except (OSError, ValueError) as exc:
                        self.errors.append(str(exc))
                if versions:
                    slug = slug_dir.name
        self.drafts[slug] = versions
        self.active[slug] = self._read_active(slug_dir) or max(
            versions, key=lambda v: int(VERSION_RE.match(v).group(1))  # type: ignore[union-attr]
        )
        return self

    def _read_active(self, slug_dir: Path) -> str | None:
        pointer = slug_dir / "active.json"
        if pointer.exists():
            try:
                data = json.loads(pointer.read_text(encoding="utf-8"))
                return data.get("active")
            except (OSError, json.JSONDecodeError):
                return None
        return None

    # -- queries -------------------------------------------------------------

    def published_list(self) -> list[OkfGuide]:
        return sorted(self.published.values(), key=lambda g: g.frontmatter.title.lower())

    def get_published(self, slug: str) -> OkfGuide | None:
        return self.published.get(slug)

    def get_active(self, slug: str) -> OkfGuide | None:
        if slug in self.published:
            return self.published[slug]
        versions = self.drafts.get(slug)
        if versions:
            return versions.get(self.active.get(slug, ""), None) or max(
                versions.values(), key=lambda g: g.path.stat().st_mtime
            )
        return None

    def list_versions(self, slug: str) -> list[DraftVersion]:
        versions = self.drafts.get(slug, {})
        ordered = sorted(versions.items(), key=lambda kv: int(VERSION_RE.match(kv[0]).group(1)))  # type: ignore[union-attr]
        return [DraftVersion(slug=slug, version=v, path=g.path, guide=g) for v, g in ordered]

    def next_version_number(self, slug: str) -> int:
        existing = self.list_versions(slug)
        return (max(int(VERSION_RE.match(v.version).group(1)) for v in existing) + 1) if existing else 1

    def draft_dir(self, slug: str) -> Path:
        return settings.drafts_dir / slug

    def activate(self, slug: str, version: str) -> bool:
        if version not in self.drafts.get(slug, {}):
            return False
        (self.draft_dir(slug) / "active.json").write_text(
            json.dumps({"active": version}, indent=2), encoding="utf-8"
        )
        self.active[slug] = version
        return True

    # -- search ---------------------------------------------------------------

    ALIASES: dict[str, tuple[str, ...]] = {
        "google-gmail": ("gmail", "google mail", "google workspace", "google"),
        "microsoft": ("entra", "azure ad", "azure", "microsoft graph", "outlook", "office 365", "teams"),
        "meta-facebook": ("facebook", "meta", "instagram", "facebook login"),
        "google-gmail-oauth": ("gmail",),
    }

    def search_published(self, query: str) -> list[OkfGuide]:
        q = query.strip().lower().replace(" ", "")
        if not q:
            return []
        scored: list[tuple[int, OkfGuide]] = []
        for guide in self.published.values():
            slug = guide.slug.lower()
            title = guide.frontmatter.title.lower()
            haystacks = [slug, title.replace(" ", "")]
            for alias in self.ALIASES.get(slug, ()):
                haystacks.extend([alias, alias.replace(" ", "")])
            best = 3
            for h in haystacks:
                if h == q:
                    best = min(best, 0)
                elif h.startswith(q):
                    best = min(best, 1)
                elif q in h:
                    best = min(best, 2)
            if best < 3:
                scored.append((best, guide))
        scored.sort(key=lambda pair: (pair[0], pair[1].slug))
        return [g for _, g in scored[:6]]

    # -- catalogue ------------------------------------------------------------

    def write_catalogue(self) -> Path:
        """Regenerate knowledge/guides/index.md (human-readable map, drives the grid)."""
        published = self.published_list()
        lines = [
            "---",
            'okf_version: "0.2"',
            "generated_catalogue: true",
            "---",
            "",
            "# OAuth Guide Catalogue",
            "",
            "Generated on every guide write. Featured grid data source; excluded from retrieval.",
            "",
            "## Published library guides",
            "",
            "| Guide | Tier | Hands-on | Approval wait | Composio | Sections |",
            "|---|---|---|---|---|---|",
        ]
        for g in published:
            fm = g.frontmatter
            gc = fm.guide
            managed = {True: "managed", False: "BYO"}.get(gc.composio_next.managed, "—")
            sections = "; ".join(
                line.removeprefix("## ").strip() for line in g.body.splitlines() if line.startswith("## ")
            )
            rel = g.path.relative_to(settings.guides_dir).as_posix()
            lines.append(
                f"| [{fm.title}]({rel}) | {gc.difficulty.tier} | {gc.time.hands_on} | "
                f"{gc.time.approval_wait} | {managed} | {sections} |"
            )
        if self.drafts:
            lines += ["", "## Generated drafts (not published)", "", "| Guide | Versions | Active |", "|---|---|---|"]
            for slug, versions in sorted(self.drafts.items()):
                guide = versions.get(self.active.get(slug, ""), next(iter(versions.values())))
                lines.append(f"| {guide.frontmatter.title} | {', '.join(sorted(versions))} | {self.active.get(slug, '—')} |")
        lines += [
            "",
            "## Governance summary",
            "",
            f"- **Published guides:** {len(published)}",
            f"- **Generated draft apps:** {len(self.drafts)}",
            f"- **Load errors:** {len(self.errors)}",
            "",
        ]
        path = settings.guides_dir / "index.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


def resolve_query(store: GuideStore, query: str) -> dict:
    """Resolve a search query into the 3 cases: library / catalog / none."""
    hits = store.search_published(query)
    if hits:
        return {
            "case": "library",
            "query": query,
            "library": [
                {
                    "slug": g.slug,
                    "title": g.frontmatter.title,
                    "tier": g.frontmatter.guide.difficulty.tier,
                    "hands_on": g.frontmatter.guide.time.hands_on,
                    "approval_wait": g.frontmatter.guide.time.approval_wait,
                    "managed": g.frontmatter.guide.composio_next.managed,
                    "url": f"/guide/{g.slug}",
                }
                for g in hits
            ],
            "catalog": [],
        }
    # A live-generated draft exists for this app even though no published guide does —
    # surface it instead of pretending we know nothing (slug-shadowing fix).
    qn = query.strip().lower().replace(" ", "")
    for slug, versions in store.drafts.items():
        if slug not in store.published and (slug.lower() == qn or slug.lower().startswith(qn) or qn in slug.lower()):
            return {
                "case": "draft",
                "query": query,
                "library": [],
                "catalog": [],
                "draft": {
                    "slug": slug,
                    "title": (store.get_active(slug) or list(versions.values())[0]).frontmatter.title,
                    "active": store.active.get(slug, ""),
                    "url": f"/guide/{slug}",
                },
                "generate_url": f"/generate?app={query}",
            }
    try:
        catalog = composio.search_catalog(query)
    except FileNotFoundError:
        catalog = []
    if catalog:
        return {
            "case": "catalog",
            "query": query,
            "library": [],
            "catalog": [
                {
                    "slug": p.slug,
                    "name": p.name,
                    "logo": p.logo,
                    "oauth": p.supports_oauth,
                    "managed": p.composio_managed,
                    "auth_schemes": p.auth_schemes,
                    "auth_guide_url": p.auth_guide_url,
                    "generate_url": f"/generate?app={p.name}",
                }
                for p in catalog
            ],
        }
    return {
        "case": "none",
        "query": query,
        "library": [],
        "catalog": [],
        "generate_url": f"/generate?app={query}",
    }


def new_store() -> GuideStore:
    return GuideStore().refresh()
