# OAuth Compass — know the path to connecting any app

A developer building an AI agent needs their users to connect apps (Slack, Gmail, Salesforce…).
Before that can happen, **they** must register an OAuth app with each provider — and often wait
for approval. That journey is opaque: is it 20 minutes or 3 weeks? What will block you?

**OAuth Compass** answers it two ways:

1. **Guide library** — independently verified (agent verification crew, human-supervised),
   deeply structured setup guides for 8 apps spanning the
   difficulty spectrum (instant → nuanced caps → weeks-long review).
2. **Live generation** — submit *any* app name or website and watch an agent (CrewAI + NVIDIA NIM)
   research the provider's official docs and generate the same quality of guide in ~2 minutes,
   versioned and instantly shareable.

Every claim in every guide is evidence-tagged (`verified_from_docs` / `reported` / `unknown`),
sourced to the provider's own documentation, and separated into **hands-on setup time** vs
**approval wait** — and every step says whether an **agent can automate it or a human must do it**.

**🔗 Demo video (end-to-end walkthrough):** [Watch on Google Drive](https://drive.google.com/drive/folders/1RCfMPoHquCkhmJYZpY1YFoV-fCnUwgaM?usp=sharing)
**🔗 Live experience:** [oauth-compass-frontend.vercel.app](https://oauth-compass-frontend.vercel.app) · API health: [oauth-compass-4guz.onrender.com/api/health](https://oauth-compass-4guz.onrender.com/api/health)
**👤 Author:** Sachin Goyal · sachingoyal9274@gmail.com

## Quick start

```bash
# 1. Python 3.11+ (3.13 tested)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

# 2. Configure keys (see .env.example)
copy .env.example .env        # then fill in your keys
#   NVIDIA_API_KEY    — build.nvidia.com (live generation LLM)
#   COMPOSIO_API_KEY  — dashboard.composio.dev → Settings (platform API key)

# 3. Sync the Composio toolkit catalog (once; cache is committed, app runs without keys)
.venv\Scripts\python scripts\sync_toolkits.py

# 4. Run
.venv\Scripts\python -m app.run        # http://127.0.0.1:8000
```

> The catalog cache (`app/data/toolkits_cache.json`) ships committed, so the app runs with **no
> keys at all** for browsing; keys are needed only for live generation (NVIDIA) and catalog
> refresh / Composio Search tools (Composio).

## Architecture

```
FastAPI ── templates + vanilla JS (no build step, no DB)
  ├── Part 1: OKF guide records (knowledge/guides/*.md)
  │      governance: draft → verified (agent:verification-crew, human-supervised) → stable  (stale_after guards doc drift)
  │      home: featured grid (8) + full Composio catalog toggle (~400)
  │      search resolves 3 cases: library hit / catalog profile / unknown → generate
  ├── Part 2: CrewAI pipeline (NVIDIA NIM, nemotron-3-ultra-550b-a55b)
  │      [1] Resolver crew   — name/URL → app identity (no tools)
  │      [2] Researcher      — Composio-managed search session ONLY:
  │                           COMPOSIO_SEARCH_WEB + COMPOSIO_SEARCH_FETCH_URL_CONTENT
  │                           (no fallback search exists — if Composio is down, generation
  │                           fails loudly; fixed procedure, ≤6 (fast) / ≤12 (deep) official pages)
  │      [3] Writer crew     — structured guide JSON, per-claim evidence tags
  │      [4] Code gate       — Pydantic validation + 1 repair round; no LLM output trusted
  │      → versioned draft (v1, v2, …) → instant permalink → user picks active version
```

Full plan with decisions: [plan.md](plan.md). Evidence journal: [VERIFICATION.md](VERIFICATION.md).

## Key decisions

- **Provider docs are the substance; Composio is the research engine.** Every web search and page
  read goes through Composio's managed `composio_search` session — no third-party search keys, no
  fallback path. The guides cite the provider's own pages.
- **Time split** (`hands_on` vs `approval_wait`) is the product's core answer: it's the exact
  thing developers can't find out up front.
- **Agent-drafted, agent-verified library.** The same crew that generates live also drafted the
  8 library guides; an independent verification agent then re-checked every claim against
  official provider docs under human supervision —
  **~100 claims confirmed, 87 corrections applied** (see VERIFICATION.md).
- **Versioned generations, user picks the active one.** Regenerating never overwrites.
- **No dead ends.** Unknown apps flow straight into live generation.
- **Swap-friendly LLM.** All model access lives in one module (`app/services/nim.py`) on LiteLLM —
  any OpenAI-compatible provider works by changing 3 env values.

## Limitations (honest ones)

- No provider accounts were created and no approvals were actually filed — timelines come from
  official docs and community reports, tagged accordingly (`reported`).
- Live-generated guides are drafts: strong on well-documented providers, weaker where the
  provider documents little — those say so in their "could not verify" list.
- NVIDIA's hosted NIM free tier rate-limits: many consecutive generations can return 429 — the UI
  surfaces it as a clean error and the same generation succeeds later.