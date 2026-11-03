"""JSON + SSE API: health, search, catalog, generation stream, versions."""
from __future__ import annotations

import asyncio
import json
import queue
import threading
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.okf import GuideBadge
from app.services import composio, nim
from app.services.generator import GuideWorkflowError, generate_guide
from app.store import resolve_query

router = APIRouter()

SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"}


@router.get("/health")
async def health(request: Request):
    store = request.app.state.store
    catalog_count = 0
    catalog_error = None
    try:
        catalog_count = len(composio.load_catalog())
    except Exception as exc:  # noqa: BLE001
        catalog_error = str(exc)
    return {
        "ok": True,
        "nim": nim.check_nim(),
        "composio_key_present": settings.has_composio,
        "catalog_count": catalog_count,
        "catalog_error": catalog_error,
        "published_guides": len(store.published),
        "generated_draft_apps": len(store.drafts),
        "store_errors": store.errors[:5],
    }


@router.get("/search")
async def search(request: Request, q: str = ""):
    return resolve_query(request.app.state.store.refresh(), q)


@router.get("/catalog")
async def catalog(q: str = "", limit: int = 60):
    try:
        profiles = composio.search_catalog(q, limit=min(limit, 400)) if q else composio.load_catalog()[:limit]
    except FileNotFoundError as exc:
        return JSONResponse({"error": str(exc)}, status_code=503)
    return {
        "count": len(profiles),
        "items": [
            {
                "slug": p.slug,
                "name": p.name,
                "logo": p.logo,
                "oauth": p.supports_oauth,
                "managed": p.composio_managed,
                "auth_schemes": p.auth_schemes,
                "categories": p.categories[:3],
            }
            for p in profiles
        ],
    }


@router.get("/guides")
async def guides(request: Request):
    store = request.app.state.store.refresh()
    return {
        "published": [
            {
                "slug": g.slug,
                "title": g.frontmatter.title,
                "summary": g.frontmatter.guide.summary,
                "tier": g.frontmatter.guide.difficulty.tier,
                "level": g.frontmatter.guide.difficulty.level,
                "hands_on": g.frontmatter.guide.time.hands_on,
                "approval_wait": g.frontmatter.guide.time.approval_wait,
                "verdict": g.frontmatter.guide.time.verdict,
                "managed": g.frontmatter.guide.composio_next.managed,
            }
            for g in store.published_list()
        ],
        "drafts": sorted(store.drafts.keys()),
    }


@router.get("/guides/{slug}")
async def guide_detail(request: Request, slug: str, v: str | None = None):
    store = request.app.state.store.refresh()
    guide = None
    if v:
        guide = next((ver.guide for ver in store.list_versions(slug) if ver.version == v), None)
    if guide is None:
        guide = store.get_active(slug)
    if guide is None:
        return JSONResponse({"error": f"no guide for {slug}"}, status_code=404)
    fm, g = guide.frontmatter, guide.frontmatter.guide
    versions = store.list_versions(slug)
    return {
        "slug": fm.resource,
        "title": fm.title,
        "status": fm.status,
        "shown_version": v or (store.active.get(slug) if slug in store.drafts else None),
        "versions": [{"version": x.version} for x in versions],
        "active_version": store.active.get(slug),
        "difficulty": g.difficulty.model_dump(),
        "time": g.time.model_dump(),
        "summary": g.summary,
        "prerequisites": [p.model_dump() for p in g.prerequisites],
        "steps": [s.model_dump() for s in g.steps],
        "gotchas": [x.model_dump() for x in g.gotchas],
        "blockers": [b.model_dump() for b in g.blockers],
        "agent_vs_human": g.agent_vs_human.model_dump(),
        "composio_next": g.composio_next.model_dump(),
        "sources": [s.model_dump() for s in fm.sources],
        "unverified": fm.unverified,
        "provenance": {
            "generated_by": fm.generated.by if fm.generated else "unknown",
            "verified_by": fm.verified.by if fm.verified else None,
            "last_checked": str(fm.last_checked or ""),
            "stale_after": str(fm.stale_after or ""),
        },
    }


@router.get("/guides/{slug}/versions")
async def guide_versions(request: Request, slug: str):
    store = request.app.state.store.refresh()
    return {
        "slug": slug,
        "active": store.active.get(slug),
        "versions": [
            {"version": v.version, "path": str(v.path), "title": v.guide.frontmatter.title}
            for v in store.list_versions(slug)
        ],
    }


class ActivateRequest(BaseModel):
    version: str = Field(min_length=1, max_length=8)


@router.post("/guides/{slug}/activate")
async def activate_version(request: Request, slug: str, payload: ActivateRequest):
    store = request.app.state.store.refresh()
    if not store.activate(slug, payload.version):
        return JSONResponse({"error": f"version {payload.version} not found for {slug}"}, status_code=404)
    return {"ok": True, "slug": slug, "active": payload.version}


class GenerateRequest(BaseModel):
    input: str = Field(min_length=1, max_length=400)
    deep: bool = False


def _generation_stream(app: Any, user_input: str, deep: bool, badge: GuideBadge):
    """Run generate_guide in a worker thread; stream progress as SSE lines."""
    events: queue.Queue = queue.Queue()
    sentinel = object()

    def worker() -> None:
        try:
            fm = generate_guide(user_input, deep=deep, badge=badge, progress=events.put)
        except GuideWorkflowError as exc:
            events.put({"stage": "error", "message": str(exc)})
        except Exception as exc:  # noqa: BLE001
            events.put({"stage": "error", "message": f"{type(exc).__name__}: {exc}"})
        finally:
            events.put(sentinel)
            try:
                app.state.store.refresh().write_catalogue()
            except Exception:  # noqa: BLE001
                pass

    threading.Thread(target=worker, daemon=True).start()

    def event_stream():
        while True:
            try:
                event = events.get(timeout=90)
            except queue.Empty:
                yield ": keepalive\n\n"
                continue
            if event is sentinel:
                break
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return event_stream()


@router.post("/generate")
async def generate(request: Request, payload: GenerateRequest):
    stream = _generation_stream(request.app, payload.input, payload.deep, "live_generated")
    return StreamingResponse(stream, media_type="text/event-stream", headers=SSE_HEADERS)


class RegenerateRequest(BaseModel):
    deep: bool = False


@router.post("/guides/{slug}/regenerate")
async def regenerate(request: Request, slug: str, payload: RegenerateRequest):
    store = request.app.state.store.refresh()
    guide = store.get_active(slug)
    name = guide.frontmatter.title.split("—")[0].strip() if guide else slug
    stream = _generation_stream(request.app, name, payload.deep, "live_generated")
    return StreamingResponse(stream, media_type="text/event-stream", headers=SSE_HEADERS)
