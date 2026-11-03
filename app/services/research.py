"""Local research helpers used by the generation crew: page fetching and a
keyless DuckDuckGo fallback search. The Composio Search MCP tools are the
primary search/read path; these are the resilient local fallbacks."""
from __future__ import annotations

import logging
import re
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

MAX_PAGE_CHARS = 24_000


def fetch_url_text(url: str, max_chars: int = MAX_PAGE_CHARS) -> str:
    """Fetch a page and extract readable text (title + body, tags stripped)."""
    if not re.match(r"^https?://", url):
        raise ValueError("url must start with http(s)://")
    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "form"]):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else ""
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    header = f"[{title}]({url})\n\n" if title else f"[{url}]\n\n"
    return (header + text)[:max_chars]


def ddg_search(query: str, max_results: int = 8) -> list[dict[str, str]]:
    """Keyless DuckDuckGo HTML search — fallback when Composio Search is unavailable."""
    try:
        with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get("https://html.duckduckgo.com/html/", params={"q": quote_plus(query)})
            resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.warning("DuckDuckGo fallback failed: %s", exc)
        return []
    soup = BeautifulSoup(resp.text, "lxml")
    results: list[dict[str, str]] = []
    for anchor in soup.select("a.result__a")[:max_results]:
        href = anchor.get("href", "")
        # DDG wraps outbound links in /l/?uddg=<urlencoded>
        match = re.search(r"uddg=([^&]+)", href)
        if match:
            from urllib.parse import unquote

            href = unquote(match.group(1))
        title = anchor.get_text(strip=True)
        if href.startswith("http") and title:
            results.append({"title": title, "url": href})
    return results


def guess_doc_urls(app_name: str, website: str = "") -> list[str]:
    """Heuristic developer-portal/doc URLs for an app, tried by the crew via fetch."""
    candidates: list[str] = []
    domain = ""
    if website:
        match = re.match(r"^https?://(?:www\.)?([^/]+)", website.strip())
        if match:
            domain = match.group(1)
    base = domain or f"{app_name.lower().replace(' ', '')}.com"
    candidates += [
        f"https://developers.{base}",
        f"https://{base}/developers",
        f"https://docs.{base}",
        f"https://developer.{base}",
        f"https://{base}/docs/oauth",
    ]
    seen: set[str] = set()
    return [c for c in candidates if not (c in seen or seen.add(c))]
