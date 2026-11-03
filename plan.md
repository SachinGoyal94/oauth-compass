# Implementation Plan — OAuth Setup Guide Product

> The assignment: developers building AI agents must register OAuth apps with providers
> (sometimes waiting weeks for approval) and can't tell up front how hard it is.
> We build a FastAPI web app where a developer searches a library of pre-built guides
> **or** submits any app name/website and watches an agent generate the same quality of
> guide live — with honest evidence about what is verified, reported, or unknown.

## Stack (locked)

| Layer | Choice |
|---|---|
| Backend | **FastAPI** (Jinja2 templates + vanilla JS, no build step, no database) |
| Agentic framework | **CrewAI** (sequential small crews, code-side validation of every agent decision) |
| LLM | **NVIDIA NIM** — `nvidia/nemotron-3-ultra-550b-a55b` @ `https://integrate.api.nvidia.com/v1` (OpenAI-compatible via LiteLLM `openai/` prefix) |
| Tools / data platform | **Composio** — toolkit catalog API (managed-vs-BYO, required fields) + **Composio Search** MCP toolkit (keyless web search, URL content fetch) + auth-config story for "what to do next" |
| Knowledge format | **OKF** (Open Knowledge Format, adapted from Portfolio-Agent): markdown + YAML frontmatter, Pydantic-validated, draft → human-verified → stable governance |
| Keys | `.env` only: `NVIDIA_API_KEY`, `COMPOSIO_API_KEY` (+ `COMPOSIO_USER_ID`). Never committed; `.env.example` documents them |

## Project structure

```
D:\Product_ops\
├── app\
│   ├── main.py            FastAPI app (lifespan, CORS, /api/health)
│   ├── config.py          settings from .env
│   ├── okf.py             oauth_guide OKF record type + loaders + catalogue writer
│   ├── routes\pages.py    HTML: home, guide page, generate page
│   ├── routes\api.py      JSON + SSE: search, catalog, generate (stream), versions
│   ├── services\
│   │   ├── composio.py    catalog cache read/search + auth details fetch
│   │   ├── nim.py         CrewAI LLM factory + direct client + connectivity check
│   │   └── generator.py   the 3-crew generation pipeline
│   └── data\toolkits_cache.json   synced from Composio, committed
├── knowledge\guides\
│   ├── index.md           generated catalogue (drives home grid)
│   ├── *.md               the 8 published library guides
│   └── drafts\{slug}\     live generations, versioned: v1.md, v2.md… + active.json
├── scripts\sync_toolkits.py   Composio catalog → cache (run once, needs key)
├── scripts\draft_library.py   batch-run crew on the 8 apps → drafts
├── templates\  static\    frontend
├── VERIFICATION.md        what was verified / corrected / could-not-verify (per app)
└── README.md              setup, key decisions, limitations
```

---

# PART 1 — Pre-built Guide Library

## 1.1 Knowledge layer — OKF `oauth_guide` records

One record = markdown file with YAML frontmatter (Pydantic-validated) + prose body mirror.

**Frontmatter blocks**

| Block | Fields |
|---|---|
| Governance | `type: oauth_guide`, `resource` (slug), `title`, `tags[]`, `status` (draft/stable/deprecated), `stale_after` (today+180d), `generated {by, at}` (agent provenance), `verified {by, at}` (human pass), `last_checked` |
| Evidence | `sources[] {url, title, what_it_supports}` · `unverified[]` (claims we could not confirm) |
| Structured guide | `summary`, `app_website`, `developer_console`, `oauth_docs` · `difficulty {level 1-5, tier: Instant/Light/Moderate/Heavy review/Weeks, verdict}` · `time {hands_on, approval_wait, verdict}` ← **the core split** · `prerequisites[] {item, detail, blocking}` · `steps[] {n, title, where (console deep-link), action, duration, agent_automatable, human_because, nuances, evidence: verified_from_docs/reported/unknown, source_url}` · `gotchas[] {title, why_it_matters, how_to_handle, evidence, source_url}` · `blockers[] {issue, how_to_resolve, escalation}` · `agent_vs_human {agent_can[], human_must[]}` · `composio_next {managed, managed_note, redirect_uri_to_register, auth_config_fields[], auth_config_snippet, mcp_note}` |

**Governance rules (Portfolio-Agent model):**
- Published-to-grid requires `status=="stable" ∧ human-verified ∧ not stale ∧ visible`
- Agent drafts and live generations live in `drafts/` — reachable by permalink, never in the featured grid
- `knowledge/guides/index.md` catalogue is regenerated on every write (drives the home grid)

**Sources of truth:** provider official docs = guide substance (steps, rules, timelines, gotchas);
Composio = metadata grounding (OAuth scheme, managed-vs-BYO, required credential fields, `auth_guide_url`).
Every claim carries evidence tag + source URL. No fabricated numbers — approval waits state what sources
support or go to `unverified[]`.

## 1.2 Composio catalog layer

- `scripts/sync_toolkits.py` → `app/data/toolkits_cache.json` (committed) — app runs **without any key**; key only refreshes
- Per app: slug, name, logo, auth schemes, **managed-vs-BYO** (`composio_managed_auth_schemes`), `auth_guide_url`, categories
- On demand (key present): single-toolkit `auth_config_details` → required credential fields (client_id, client_secret, redirect URI…)
- Spot-checks on sync: gmail=managed ✓ · slack=managed ✓ · shopify=BYO ✓

## 1.3 Producing the 8 library guides

**Apps (spanning the difficulty spectrum):**

| Tier | Apps | What it demonstrates |
|---|---|---|
| Instant, no review | GitHub · Slack · Notion | Form-filling → client ID/secret in minutes |
| Nuanced / caps | Google-Gmail · Microsoft | Testing-mode refresh-token expiry (7 days), unverified 100-user cap, restricted scopes + CASA, consent-screen rules |
| Heavy review | Salesforce · Meta-Facebook · Shopify | Security review (weeks), App Review + business verification, distribution review |

**Pipeline:** crew first → `scripts/draft_library.py` batch-runs the crew on the 8 → drafts in
`knowledge/guides/drafts/` → **human verification pass** (line-by-line vs official docs: confirm /
correct / flag-unverifiable) → publish (`status: stable`, `verified` set) → `VERIFICATION.md` logs
per app: confirmed / corrected / could-not-verify, with links.

## 1.4 Web experience (Part 1 surface)

- **Home `/`:** search box · featured grid of the 8 (tier badge, time verdict, managed/BYO chip) ·
  toggle → browse all ~400 catalog (`Guide ready ✓` / `Generatable` chips)
- **Search → 3 cases, no dead ends:**
  - **A · Library hit** → instant `/guide/{slug}` (no LLM, renders from OKF record)
  - **B · Catalog hit** → profile card (OAuth? managed/BYO? required fields) + "Generate guide" button
  - **C · Unknown** → straight to live generation
- **Guide page `/guide/{slug}`:** full structured guide + evidence panel (sources, per-claim tags,
  last-checked) + provenance footer (+ version switcher when versions exist)
- Search: in-memory, aliases (gmail/google mail/google workspace → one slug), no DB

**Acceptance checks:** sync spot-checks pass · 8 published guides render · 3-case search correct ·
drafts never appear in the featured grid · no keys anywhere in repo/zip.

---

# PART 2 — Live Generation

## 2.1 Crew architecture — three small crews, fixed procedure, code gates

```
[1] RESOLVER — no tools, max_iter=1, temp 0.1
      "airtable" or URL → JSON {app_name, website, note}
      code validates JSON shape

[2] RESEARCHER — fixed procedure, max_iter 10 (fast) / 14 (deep), temp 0.3
      tools: Composio Search MCP (Composio Web Search/Exa, Fetch URL Content,
               session-managed) via MCPServerAdapter (streamable-http + x-api-key)
             + lookup_composio_toolkit (local catalog cache + auth details)
             + local fetch_url (resilience if Composio is down)
      fixed order:
        ① toolkit lookup → record full output
        ② find OFFICIAL OAuth/developer docs (search tools)
        ③ read ≤6 pages (fast) / ≤12 (deep): OAuth overview, app creation guide,
           scopes, redirect URI rules, verification/review policy, rate/pricing notes
        ④ if search misses: direct-try developer-domain URL patterns
      output: RESEARCH DIGEST — identity · Composio metadata · registration path ·
      requirements · review/approval (+ timeline sources) · limits & gotchas · sources —
      every fact carries its source URL or is marked UNVERIFIED

[3] WRITER — no tools, max_iter=1, temp 0.2
      digest + Composio profile → ONE JSON per guide schema
      evidence tags mandatory · approval_wait only what sources support ·
      anything unconfirmed → unverified[] · never fabricate

[4] CODE GATE — no LLM trust
      Pydantic validation → 1 repair round (fixer agent fed validation errors)
      → still invalid → honest error surfaced
```

Conventions (Portfolio-Agent): `OTEL_SDK_DISABLED=true` before imports · `Process.sequential`,
`memory=False, tracing=False`, `allow_delegation=False` · custom errors
(`ProviderConfigurationError`, `GuideWorkflowError`) · provider-failure retry classification.

## 2.2 Versioning

- Every generation writes `knowledge/guides/drafts/{slug}/v{N}.md` — **never overwrites**
- `active.json` per slug records the live version; default = newest
- Guide page serves the active version + a **version switcher** (v1, v2 … with timestamps);
  user activates any version they want to go with
- Regenerating = new version alongside old ones

## 2.3 Output & governance

- Result = OKF draft record → **instant shareable permalink** `/guide/{slug}`
- **No unverified badge** — the evidence panel (sources + per-claim evidence tags + last-checked)
  is the provenance surface, on every guide (library and generated alike)
- The 8 library guides use the same crew; they differ only by `status: stable` + `verified`
  after the human pass (visible in the provenance footer)

## 2.4 Live UX — SSE progress stream

`POST /api/generate {input, deep}` → `text/event-stream` (StreamingResponse, `Cache-Control: no-cache`,
`X-Accel-Buffering: no`; generation in a worker thread, events via queue):

> `resolve` Resolving app identity… → `ground` Composio: BYO OAuth — client_id/secret/redirect_uri
> → `search` Searching official docs… → `search` Reading developers.airtable.com… (per tool call)
> → `synthesize` Writing structured guide… → `validate` ✓ → `save` vN saved → `done` Guide ready → [open]

Fast (~2 min) default · **Deep research** toggle.

## 2.5 Failure modes — all explicit, never fabricated

| Failure | Behavior |
|---|---|
| Composio MCP down | generation fails loudly — no fallback search, by design |
| App not in Composio catalog | researcher proceeds on official docs alone (noted in digest) |
| Docs unreachable | low-confidence guide; `unverified[]` lists the gaps |
| NIM error / timeout | clear error in the stream; no guide written |
| Schema fails after repair | error surfaced with validation details |

## 2.6 API surface (Part 2)

- `POST /api/generate` — SSE stream
- `GET /api/guides/{slug}/versions` · `POST /api/guides/{slug}/activate {version}` ·
  `POST /api/guides/{slug}/regenerate`
- Part 1: `GET /api/health` (incl. NIM probe) · `GET /api/guides` · `GET /api/search?q=` ·
  `GET /api/catalog?q=`

## 2.7 Scope boundaries

Out of scope: browser automation of provider consoles (docs research only) · real approvals /
paid accounts · all 100 guides · multi-user auth/white-labeling. Cloud deploy comes later —
local-first, zip-ready submission.

---

# BUILD ORDER

1. Finalize scaffold + OKF module + NIM connectivity check
2. Crew pipeline (resolver → researcher → writer → code gate) + version store
3. `sync_toolkits.py` with key → cache committed
4. Batch-draft the 8 → verification pass → publish + VERIFICATION.md
5. Frontend: home (grid/toggle/search) · guide page (+ version switcher) · generate page (SSE)
6. E2E: live-generate **Airtable, Zoom, Figma** (outside library) → guides render with evidence · browser screenshot pass
7. README (setup / key decisions / limitations) · submission zip (`.env`, `.venv` excluded)

---

# KEY DECISIONS LOG

| # | Decision | Why |
|---|---|---|
| 1 | Two knowledge layers: 8 deep guides + ~400 shallow Composio profiles | Assignment asks for a library AND live generation; deep≠broad |
| 2 | Library guides = agent drafts → human verification → published | Real product pipeline; corrections become the evidence story (VERIFICATION.md) |
| 3 | Composio = metadata + search tools; provider docs = substance | Composio catalog is a directory, not documentation; evidence must cite the enforcer |
| 4 | Composio Search toolkit for web search/reading (keyless) | No third-party keys; "built on Composio" story; local fallbacks keep it resilient |
| 5 | Time split: hands-on vs approval-wait in every guide | The exact confusion the assignment names ("an hour vs weeks of waiting") |
| 6 | agent_vs_human on every step | "What an agent can do for them and where they need to take over" — literal assignment line |
| 7 | Evidence tags verified_from_docs / reported / unknown + sources panel | "Sound judgment about evidence" is a graded criterion |
| 8 | Small crews with fixed procedures + code-side gates | Predictable live demos; no LLM output trusted without validation (portfolio pattern) |
| 9 | Versioned generations, user picks active | User decision: compare regenerations, keep the one they want |
| 10 | No unverified badge; evidence panel carries provenance | User decision: everything is extracted+sourced; avoid scary labels |
| 11 | OKF with draft→verified→stable governance | Reuses proven Portfolio-Agent knowledge governance; stale_after handles doc drift |
