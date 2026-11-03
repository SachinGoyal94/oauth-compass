"""FastAPI application: OAuth setup guide product."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.routes import api, pages
from app.store import new_store


@asynccontextmanager
async def lifespan(application: FastAPI):
    store = new_store()
    try:
        store.write_catalogue()
    except OSError as exc:
        print(f"[startup] catalogue write failed: {exc}")
    application.state.store = store
    print(f"[startup] guides loaded: published={len(store.published)} drafts={len(store.drafts)} errors={len(store.errors)}")
    yield


app = FastAPI(title="OAuth Compass — OAuth app setup guides", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")
