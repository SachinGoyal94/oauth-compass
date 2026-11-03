"""HTML pages: home, guide, generate."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    store = request.app.state.store
    published = [
        {
            "slug": g.slug,
            "title": g.frontmatter.title,
            "summary": g.frontmatter.guide.summary[:220],
            "tier": g.frontmatter.guide.difficulty.tier,
            "level": g.frontmatter.guide.difficulty.level,
            "hands_on": g.frontmatter.guide.time.hands_on,
            "approval_wait": g.frontmatter.guide.time.approval_wait,
            "verdict": g.frontmatter.guide.time.verdict,
            "managed": g.frontmatter.guide.composio_next.managed,
            "logo": "",
        }
        for g in store.published_list()
    ]
    ticker_names = (
        [g["title"].split("—")[0].split("(")[0].strip() for g in published]
        + [
            "Linear", "Airtable", "Zoom", "Figma", "Discord", "DocuSign", "Xero",
            "Spotify", "HubSpot", "Jira", "Dropbox", "Snowflake", "Trello", "Calendly",
            "+ 1,700 more in the catalog",
        ]
    )
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "published": published,
            "catalog_count": _catalog_count(),
            "ticker_names": ticker_names,
        },
    )


@router.get("/guide/{slug}", response_class=HTMLResponse)
async def guide_page(request: Request, slug: str, v: str | None = None):
    store = request.app.state.store
    guide = None
    if v:
        for version in store.list_versions(slug):
            if version.version == v:
                guide = version.guide
                break
    if guide is None:
        guide = store.get_active(slug)
    if guide is None:
        return templates.TemplateResponse(request, "not_found.html", {"slug": slug}, status_code=404)
    versions = store.list_versions(slug)
    active_version = store.active.get(slug) if slug in store.drafts else None
    return templates.TemplateResponse(
        request,
        "guide.html",
        {
            "guide": guide,
            "fm": guide.frontmatter,
            "g": guide.frontmatter.guide,
            "versions": versions,
            "active_version": active_version,
            "shown_version": v or active_version,
        },
    )


@router.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request, app_name: str = ""):
    return templates.TemplateResponse(request, "generate.html", {"prefill": app_name})


def _catalog_count() -> int:
    try:
        from app.services import composio

        return len(composio.load_catalog())
    except Exception:  # noqa: BLE001
        return 0
