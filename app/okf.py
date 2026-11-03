"""Open Knowledge Format for OAuth setup guides.

Adapted from the Portfolio-Agent OKF module (D:\\Portfolio-Agent\\backend\\app\\okf.py):
markdown records with YAML frontmatter, Pydantic-validated, governed by a
draft -> human-verified -> stable lifecycle. A guide is publicly retrievable
only when it is visible, stable, current (not stale), and human-verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

EvidenceLevel = Literal["verified_from_docs", "reported", "unknown"]
DifficultyTier = Literal["Instant", "Light", "Moderate", "Heavy review", "Weeks"]
GuideBadge = Literal["library", "live_generated"]

COMPOSIO_REDIRECT_URI = "https://backend.composio.dev/api/v3/toolkits/auth/callback"


class GeneratedBy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    by: str = Field(min_length=3, max_length=160)
    at: datetime


class VerifiedBy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    by: str = Field(pattern=r"^human:[A-Za-z0-9_.-]+$")
    at: datetime


class GuidePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    visible: bool = True
    priority: Literal["primary", "supporting"] = "supporting"


class EvidenceSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(pattern=r"^https?://")
    title: str = Field(min_length=3, max_length=240)
    what_it_supports: str = Field(min_length=3, max_length=600)


class Prerequisite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item: str = Field(min_length=3, max_length=240)
    detail: str = Field(default="", max_length=600)
    blocking: bool = True
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n: int = Field(ge=1, le=40)
    title: str = Field(min_length=3, max_length=240)
    where: str = Field(default="", max_length=400, description="Console page / deep link where this happens")
    action: str = Field(min_length=3, max_length=2000)
    duration: str = Field(default="", max_length=80)
    agent_automatable: bool = False
    human_because: str = Field(default="", max_length=400, description="Why a human must do this, when not automatable")
    nuances: str = Field(default="", max_length=1200)
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class Gotcha(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=3, max_length=240)
    why_it_matters: str = Field(min_length=3, max_length=1200)
    how_to_handle: str = Field(default="", max_length=1200)
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class Blocker(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue: str = Field(min_length=3, max_length=300)
    how_to_resolve: str = Field(min_length=3, max_length=1200)
    escalation: str = Field(default="", max_length=600)
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class Difficulty(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level: int = Field(ge=1, le=5)
    tier: DifficultyTier
    verdict: str = Field(min_length=3, max_length=700)
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class TimeEstimate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hands_on: str = Field(min_length=1, max_length=120)
    approval_wait: str = Field(min_length=1, max_length=240)
    verdict: str = Field(min_length=3, max_length=300)
    evidence: EvidenceLevel = "reported"
    source_url: str = Field(default="", max_length=400)


class ComposioNext(BaseModel):
    """What to do with the finished OAuth app, via Composio: register the
    redirect URI, create the auth config, connect users, use via MCP."""

    model_config = ConfigDict(extra="forbid")
    managed: bool | None = Field(default=None, description="True when Composio provides the OAuth app itself")
    managed_note: str = Field(default="", max_length=600)
    redirect_uri_to_register: str = Field(default=COMPOSIO_REDIRECT_URI, max_length=300)
    auth_config_fields: list[str] = Field(default_factory=list, max_length=15)
    auth_config_snippet: str = Field(default="", max_length=2000)
    mcp_note: str = Field(default="", max_length=800)


class AgentVsHuman(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_can: list[str] = Field(default_factory=list, max_length=12)
    human_must: list[str] = Field(default_factory=list, max_length=12)


class GuideContent(BaseModel):
    """The structured, machine-readable guide payload stored in frontmatter."""

    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=10, max_length=2000)
    app_website: str = Field(default="", max_length=300)
    developer_console: str = Field(default="", max_length=300)
    oauth_docs: str = Field(default="", max_length=300)
    evidence: EvidenceLevel | None = None
    source_url: str = Field(default="", max_length=400)
    difficulty: Difficulty
    time: TimeEstimate
    prerequisites: list[Prerequisite] = Field(default_factory=list, max_length=12)
    steps: list[Step] = Field(min_length=1, max_length=40)
    gotchas: list[Gotcha] = Field(default_factory=list, max_length=12)
    blockers: list[Blocker] = Field(default_factory=list, max_length=10)
    agent_vs_human: AgentVsHuman = Field(default_factory=AgentVsHuman)
    composio_next: ComposioNext = Field(default_factory=ComposioNext)


class GuideFrontmatter(BaseModel):
    """Frontmatter governing one OAuth guide record."""

    model_config = ConfigDict(extra="forbid")
    type: Literal["oauth_guide"]
    okf_version: str = "0.2"
    resource: str = Field(min_length=3, max_length=240, description="Stable slug, e.g. google-gmail")
    title: str = Field(min_length=3, max_length=200)
    tags: list[str] = Field(default_factory=list, max_length=30)
    status: Literal["draft", "stable", "deprecated"] = "draft"
    stale_after: date | None = None
    generated: GeneratedBy | None = None
    verified: VerifiedBy | None = None
    chatbot: GuidePolicy = Field(default_factory=GuidePolicy)
    badge: GuideBadge = "live_generated"
    last_checked: date | None = None
    unverified: list[str] = Field(default_factory=list, max_length=15, description="Claims we could not confirm")
    sources: list[EvidenceSource] = Field(default_factory=list, max_length=20)
    guide: GuideContent

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized = []
        for tag in tags:
            cleaned = tag.strip().lower()
            if cleaned and len(cleaned) <= 60:
                normalized.append(cleaned)
        return sorted(set(normalized))

    @property
    def is_human_verified(self) -> bool:
        return self.verified is not None

    @property
    def is_current(self) -> bool:
        return self.stale_after is None or self.stale_after >= date.today()

    @property
    def is_published(self) -> bool:
        """Published library guide: stable, current, human-verified, visible."""
        return self.chatbot.visible and self.status == "stable" and self.is_current and self.is_human_verified

    @property
    def is_reviewed(self) -> bool:
        return self.verified is not None


@dataclass(frozen=True)
class OkfGuide:
    path: Path
    frontmatter: GuideFrontmatter
    body: str

    @property
    def slug(self) -> str:
        return self.frontmatter.resource


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---\n"):
        raise ValueError("OKF records must start with a YAML frontmatter block")
    parts = raw.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("OKF frontmatter must end with a closing --- line")
    parsed = yaml.safe_load(parts[0].removeprefix("---\n"))
    if not isinstance(parsed, dict):
        raise ValueError("OKF frontmatter must be a YAML mapping")
    return parsed, parts[1].strip()


def load_okf_guide(path: Path) -> OkfGuide:
    raw = path.read_text(encoding="utf-8")
    data, body = split_frontmatter(raw)
    try:
        frontmatter = GuideFrontmatter.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"{path}: invalid guide frontmatter: {exc}") from exc
    if not body:
        raise ValueError(f"{path}: OKF body cannot be empty")
    return OkfGuide(path=path, frontmatter=frontmatter, body=body)


def list_okf_guides(guides_root: Path) -> tuple[list[OkfGuide], list[str]]:
    """Load every guide record under guides_root (drafts included)."""
    guides: list[OkfGuide] = []
    errors: list[str] = []
    for path in sorted(guides_root.rglob("*.md")):
        if path.name in {"index.md", "log.md"}:
            continue
        try:
            guides.append(load_okf_guide(path))
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    return guides, errors


def guide_body_markdown(fm: GuideFrontmatter) -> str:
    """Render the human-readable markdown body mirroring the structured guide."""
    g = fm.guide
    lines: list[str] = [f"# {fm.title}", "", g.summary, ""]

    lines += ["## Difficulty & time", "", g.difficulty.verdict, "",
              f"- **Difficulty:** {g.difficulty.tier} ({g.difficulty.level}/5)",
              f"- **Hands-on setup:** {g.time.hands_on}",
              f"- **Approval wait:** {g.time.approval_wait}", ""]

    if g.prerequisites:
        lines += ["## Prerequisites", ""]
        for p in g.prerequisites:
            prefix = "**Required:** " if p.blocking else "Optional: "
            detail = f" — {p.detail}" if p.detail else ""
            lines.append(f"- {prefix}{p.item}{detail}")
        lines.append("")

    lines += ["## Step-by-step", ""]
    for s in g.steps:
        where = f" ({s.where})" if s.where else ""
        lines.append(f"### {s.n}. {s.title}{where}")
        lines.append(s.action)
        extras: list[str] = []
        if s.duration:
            extras.append(f"~{s.duration}")
        extras.append("agent-automatable" if s.agent_automatable else "human step")
        lines.append(f"*[{', '.join(extras)}; evidence: {s.evidence}]*")
        if s.nuances:
            lines.append(f"> {s.nuances}")
        lines.append("")

    if g.gotchas:
        lines += ["## Gotchas", ""]
        for got in g.gotchas:
            lines.append(f"- **{got.title}** — {got.why_it_matters}")
            if got.how_to_handle:
                lines.append(f"  - Handle: {got.how_to_handle}")
        lines.append("")

    if g.blockers:
        lines += ["## Common blockers", ""]
        for b in g.blockers:
            lines.append(f"- **{b.issue}** — {b.how_to_resolve}")
            if b.escalation:
                lines.append(f"  - Escalation: {b.escalation}")
        lines.append("")

    avh = g.agent_vs_human
    if avh.agent_can or avh.human_must:
        lines += ["## What the agent can do vs. you", ""]
        if avh.agent_can:
            lines.append("**An agent can:** " + "; ".join(avh.agent_can) + ".")
        if avh.human_must:
            lines.append("**You must:** " + "; ".join(avh.human_must) + ".")
        lines.append("")

    cn = g.composio_next
    lines += ["## Connect it via Composio", ""]
    if cn.managed:
        lines.append(cn.managed_note or "Composio provides the OAuth app for this toolkit — no registration needed.")
    else:
        lines.append(f"Register this redirect URI in the provider console: `{cn.redirect_uri_to_register}`")
        if cn.auth_config_fields:
            lines.append(f"Then create the auth config with: {', '.join(cn.auth_config_fields)}.")
        if cn.auth_config_snippet:
            lines.extend(["", "```python", cn.auth_config_snippet, "```"])
    if cn.mcp_note:
        lines.append("")
        lines.append(cn.mcp_note)
    lines.append("")

    lines += ["## Evidence", ""]
    for src in fm.sources:
        lines.append(f"- [{src.title}]({src.url}) — {src.what_it_supports}")
    if fm.unverified:
        lines.append("")
        lines.append("**Could not verify:**")
        for item in fm.unverified:
            lines.append(f"- {item}")
    lines.append("")
    lines.append(f"*Last checked: {fm.last_checked or 'not recorded'} · Status: `{fm.status}` · "
                 f"Generated by {fm.generated.by if fm.generated else 'unknown'}"
                 + (f" · Verified by {fm.verified.by}" if fm.verified else " · Not yet human-verified") + "*")
    return "\n".join(lines)


def write_okf_guide(path: Path, fm: GuideFrontmatter) -> Path:
    """Write a guide record (frontmatter + rendered body)."""
    body = guide_body_markdown(fm)
    payload = fm.model_dump(mode="json", exclude_none=True)
    yaml_fm = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{yaml_fm}---\n\n{body}", encoding="utf-8")
    return path


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
