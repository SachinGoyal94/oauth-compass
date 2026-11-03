"""Application configuration loaded from environment variables (.env)."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    """Runtime settings. Secrets are read from the environment only."""

    # NVIDIA NIM (live generation LLM)
    nvidia_api_key: str = os.getenv("NVIDIA_API_KEY", "")
    nim_base_url: str = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
    nim_model: str = os.getenv("NIM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

    # Composio (toolkit catalog + Composio Search MCP tools)
    composio_api_key: str = os.getenv("COMPOSIO_API_KEY", "")
    composio_user_id: str = os.getenv("COMPOSIO_USER_ID", "oauth-guide-builder")
    composio_base_url: str = os.getenv("COMPOSIO_BASE_URL", "https://backend.composio.dev")
    composio_search_toolkit: str = "composio_search"

    # Server
    host: str = os.getenv("APP_HOST", "127.0.0.1")
    port: int = int(os.getenv("APP_PORT", "8000"))

    # Paths
    knowledge_dir: Path = BASE_DIR / "knowledge"
    guides_dir: Path = knowledge_dir / "guides"
    drafts_dir: Path = guides_dir / "drafts"
    data_dir: Path = BASE_DIR / "app" / "data"
    toolkits_cache: Path = data_dir / "toolkits_cache.json"

    # Agent behaviour
    max_doc_pages: int = int(os.getenv("MAX_DOC_PAGES", "8"))
    fast_mode_pages: int = int(os.getenv("FAST_MODE_PAGES", "6"))
    deep_mode_pages: int = int(os.getenv("DEEP_MODE_PAGES", "12"))

    @property
    def has_nvidia(self) -> bool:
        return bool(self.nvidia_api_key)

    @property
    def has_composio(self) -> bool:
        return bool(self.composio_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
