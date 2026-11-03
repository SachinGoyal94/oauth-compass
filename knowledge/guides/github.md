---
type: oauth_guide
okf_version: '0.2'
resource: github
title: GitHub OAuth App Setup Guide
tags:
- developer-setup
- github
- oauth
- oauth-app
status: stable
stale_after: '2027-05-02'
generated:
  by: agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b
  at: '2026-11-03T17:21:42.800522Z'
verified:
  by: agent:verification-crew
  at: '2026-11-03T17:41:17.942169Z'
chatbot:
  visible: true
  priority: primary
badge: library
last_checked: '2026-11-03'
unverified:
- Exact Composio integration behavior for GitHub OAuth (snippet not verifiable from GitHub docs)
- Whether GitHub enforces any unpublished limits beyond documented ones
- Whether the OAuth app client secret can be viewed again after generation (docs never state 'shown only
  once'; that is UI behavior)
- Whether non-loopback plain-HTTP callback URLs are accepted (docs state no blanket HTTPS requirement
  — only the loopback port exception for redirect_uri matching is documented)
- An explicit official statement that OAuth apps undergo no review/approval (no OAuth docs page mentions
  a review process; organization-level OAuth app policies can still require owner approval before use)
sources:
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  title: Creating an OAuth app
  what_it_supports: Registration steps and navigation, required/optional form fields, "Enable Device Flow"
    checkbox, "Expire user access tokens" enabled by default, up to 10 callback URLs, up to 100 OAuth
    apps per user/organization, registration under personal account or organization with administrative
    access, avoid sensitive/internal URLs warning
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps
  title: Building OAuth apps (overview)
  what_it_supports: OAuth apps act on behalf of a user; scopes limit token access; GitHub Apps preferred
    for fine-grained permissions and short-lived tokens. Does not document any review process either way
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
  title: Authorizing OAuth apps
  what_it_supports: Authorization URL and parameters (client_id, redirect_uri, scope, state), PKCE S256
    (plain unsupported), 10-minute authorization code lifetime, POST /login/oauth/access_token, refresh_token
    grant and rotation, 8-hour access token / 6-month refresh token, offline_access scope, ten tokens
    per user/application/scope combination and ten created per hour, redirect_uri exact-match rule and
    loopback port exception
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
  title: Scopes for OAuth apps
  what_it_supports: Scope list (~35 including offline_access), scope normalization (user + user:email
    → user), users may grant fewer scopes than requested, offline_access behavior
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/rate-limits-for-oauth-apps
  title: Rate limits for OAuth apps
  what_it_supports: 2,000 access token requests/hour, 10 sign-ins per user/hour then re-authorization
    required, secondary rate limits, GitHub Apps limits scale while OAuth app limits are lower
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/best-practices-for-creating-an-oauth-app
  title: Best practices for creating an OAuth app
  what_it_supports: Wildcard callbacks only when necessary, device flow phishing risk, 8-hour/6-month
    token lifetimes, secure storage of client secret and tokens, SAML SSO check via GET /user/installations,
    GitHub Apps preferred
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
  title: Differences between GitHub Apps and OAuth apps
  what_it_supports: Granular permissions vs scopes, repository-level installation, ~1-hour installation
    tokens, OAuth apps use the user's 5,000 requests/hour limit, organization owner approval of OAuth
    app installs under org application policy
- url: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
  title: Rate limits for the REST API
  what_it_supports: 5,000 requests/hour personal rate limit for user access tokens, x-ratelimit-* headers
    as authoritative status, 5,000 requests/hour per OAuth app when fetching public data with client ID/secret
- url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app
  title: Authenticating to the REST API with an OAuth app
  what_it_supports: Every registered OAuth app is assigned a unique Client ID and Client Secret; do not
    leak the secret; store as environment variables
guide:
  summary: 'Register a GitHub OAuth App in minutes: GitHub runs no app review, and the app can be used
    as soon as you have its client ID and client secret (organizations can still require owner approval
    under an OAuth app policy before it is authorized). Supports up to 10 callback URLs, 100 apps per
    owner, and standard OAuth2 with PKCE (S256 only; plain is not supported). ''Expire user access tokens''
    is enabled by default, giving 8-hour access tokens and refresh tokens that expire after 6 months without
    use. GitHub recommends GitHub Apps for finer-grained permissions.'
  app_website: https://github.com
  developer_console: https://github.com/settings/developers
  oauth_docs: https://docs.github.com/en/apps/oauth-apps
  difficulty:
    level: 1
    tier: Instant
    verdict: No GitHub app review; client ID/secret are available immediately after registration — note
      that organizations can still require owner approval via an OAuth app policy before members can authorize
      the app
  time:
    hands_on: 5-10 minutes
    approval_wait: None
    verdict: No approval stage is documented; credentials are available right after registration
  prerequisites:
  - item: GitHub account
    detail: 'Personal account, or an organization where you have administrative access — docs: you can
      register an OAuth app under your personal account or under any organization you have administrative
      access to'
    blocking: true
  - item: Public homepage URL
    detail: A publicly accessible URL for your application; docs warn to avoid sensitive data such as
      internal URLs in your OAuth app
    blocking: true
  - item: Callback URL(s)
    detail: At least one redirect URI (e.g., https://backend.composio.dev/api/v3/toolkits/auth/callback);
      up to 10 allowed. The redirect_uri your app sends must exactly match a registered callback URL unless
      wildcard matching is enabled (loopback addresses supported for local development)
    blocking: true
  steps:
  - n: 1
    title: Sign in to GitHub
    where: https://github.com
    action: Log in with the personal account or organization that will own the OAuth app
    duration: 1 minute
    agent_automatable: false
    human_because: Requires interactive login and potential 2FA
    nuances: 'If creating under an organization, you need administrative access to that org (docs: apps
      can be registered under your personal account or any organization you have administrative access
      to)'
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - n: 2
    title: Open Developer Settings → OAuth Apps
    where: https://github.com/settings/developers
    action: Click profile picture → Settings → Developer settings → OAuth apps
    duration: 1 minute
    agent_automatable: false
    human_because: Navigation in GitHub UI requires human clicks
    nuances: Direct URL https://github.com/settings/developers works if already logged in
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - n: 3
    title: Create new OAuth App
    where: https://github.com/settings/developers
    action: Click "New OAuth App" (or "Register a new application" if first app)
    duration: 30 seconds
    agent_automatable: false
    human_because: Button click in provider console
    nuances: Owner can be your personal account or any organization where you have administrative access
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - n: 4
    title: Fill required registration fields
    where: GitHub OAuth App registration form
    action: Enter Application name, Homepage URL, Authorization callback URL (add up to 10 via "Add callback
      URL"). Optionally add description, enable Device Flow (only if CLI/IoT/headless), and keep "Expire
      user access tokens" checked (default). Click "Register application".
    duration: 3-5 minutes
    agent_automatable: false
    human_because: Form submission in provider console; legal acceptance of terms
    nuances: 'Docs do not impose a blanket HTTPS rule on callback URLs; avoid using sensitive data such
      as internal URLs in the app''s information. Device Flow carries phishing risk if not needed; prefer
      authorization code with PKCE. "Expire user access tokens" is enabled by default: 8-hour access token,
      6-month refresh token (lifetimes documented on the Authorizing OAuth apps page).'
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - n: 5
    title: Copy Client ID and generate Client Secret
    where: OAuth App details page (after registration)
    action: Copy the Client ID. Generate the Client Secret and copy it immediately (the UI displays it
      once — not stated in docs). Store both securely.
    duration: 1 minute
    agent_automatable: false
    human_because: Secret must be copied manually from the UI at generation time
    nuances: Every registered OAuth app is assigned a unique Client ID and Client Secret; never leak the
      secret and store it (e.g., environment variables or a key vault). If lost, generate a new one from
      the app settings (UI behavior — not documented). No app review — credentials work immediately.
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app
  - n: 6
    title: Configure scopes at authorization time
    where: Your application's OAuth authorization URL
    action: When building the authorization URL, include desired scopes (e.g., repo, user, admin:org,
      offline_access). Scopes are not set during registration; users may grant fewer than requested.
    duration: Development time
    agent_automatable: true
    human_because: ''
    nuances: Roughly 35 scopes documented (including offline_access); overlapping scopes normalized (user
      + user:email → user). offline_access yields an expiring access token + refresh token even if the
      app is not configured for expiring tokens. Users may grant fewer scopes than requested — handle
      reduced access gracefully.
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
  - n: 7
    title: Implement OAuth flow with PKCE and state
    where: Your application code
    action: Use authorization code grant with PKCE (code_challenge_method=S256; plain is not supported)
      and a random state parameter for CSRF protection. Exchange code for token within 10 minutes (code
      lifetime). Handle token refresh using refresh_token (if expiring tokens enabled); refresh rotates
      the token pair and scope cannot be changed on refresh.
    duration: Development time
    agent_automatable: true
    human_because: ''
    nuances: 'redirect_uri must exactly match a registered callback URL unless wildcard matching is enabled;
      loopback URLs may use a different port than the registered callback. Token limits: 2,000 access
      token requests/hour and ten tokens created per user/application/scope combination per hour (see
      Rate limits for OAuth apps page). SAML SSO: tokens do not access organizations where the user has
      not completed SSO; check GET /user/installations regularly (see Best practices page).'
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
  gotchas:
  - title: Token request and sign-in rate limits
    why_it_matters: OAuth apps are limited to 2,000 access token requests per hour; if an app signs the
      user in ten times within one hour, the next sign-in within the same hour requires re-authorization.
      There is also a limit of ten tokens issued per user/application/scope combination and a rate limit
      of ten tokens created per hour.
    how_to_handle: Cache tokens, implement exponential backoff, and avoid redundant token exchanges
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/rate-limits-for-oauth-apps
  - title: REST API rate limit is the user's 5,000 requests/hour
    why_it_matters: OAuth app tokens use the authenticated user's rate limit of 5,000 requests per hour,
      shared with other requests made on the user's behalf — GitHub Apps instead get limits that scale
      with users/repositories.
    how_to_handle: Monitor the x-ratelimit-* response headers (the authoritative rate limit status), honor
      x-ratelimit-reset before retrying, and back off on 403/429 responses
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
  - title: Token expiration default (8h access, 6-month refresh)
    why_it_matters: With "Expire user access tokens" enabled (the default), the access token expires after
      8 hours and the refresh token expires after 6 months without use; refresh rotates the pair (old
      access and refresh tokens stop working) and scope cannot be changed on refresh. Docs frame unchecking
      the option for apps not yet updated to support short-lived tokens; requesting the offline_access
      scope yields expiring tokens even when the app-level setting is off.
    how_to_handle: Implement refresh token flow; store refresh tokens securely (separately from access
      tokens); handle 401 by refreshing
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
  - title: 100 OAuth apps per owner limit
    why_it_matters: A single user or organization cannot own more than 100 OAuth apps
    how_to_handle: Audit existing apps; delete unused ones; consider GitHub Apps for new integrations
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - title: Maximum 10 callback URLs per app
    why_it_matters: Cannot add more than 10 redirect URIs; wildcard matching should only be enabled when
      necessary because it lets an attacker send authorization codes
    how_to_handle: Plan all environments (dev, staging, prod) upfront; use path-based differentiation
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app
  - title: Device Flow phishing risk
    why_it_matters: Enabling Device Flow without need exposes phishing risk; the device flow needs no
      redirect URIs, so an attacker can remotely impersonate your app. Prefer authorization code with
      PKCE.
    how_to_handle: Leave unchecked unless building a device-authorization-grant flow
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/best-practices-for-creating-an-oauth-app
  - title: SAML SSO restrictions
    why_it_matters: If an organization uses SAML SSO and the user has not performed SAML SSO, the user
      access token will not have access to that organization
    how_to_handle: Regularly check the GET /user/installations endpoint to verify which organizations
      a token can access; guide users to complete SSO for target orgs
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/best-practices-for-creating-an-oauth-app
  - title: Organization OAuth app policies can gate usage
    why_it_matters: 'There is no GitHub-run review of OAuth apps, but organizations can restrict them:
      when an organization application policy is active, a member''s request to install an OAuth app must
      be approved or denied by an organization owner before it can be used.'
    how_to_handle: Before rolling out inside an organization, check its OAuth app policy and have an owner
      approve the app
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
  - title: GitHub Apps preferred for new integrations
    why_it_matters: GitHub Apps offer fine-grained permissions, repository-level install, short-lived
      tokens (installation tokens expire after about 1 hour), and rate limits that scale with users/repositories;
      OAuth apps can only act as the authenticated user and use the user's 5,000 requests/hour limit
    how_to_handle: Evaluate GitHub App instead if you need repo-scoped access, higher limits, or organization-level
      installation
    evidence: verified_from_docs
    source_url: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps
  blockers:
  - issue: Owner has reached 100 OAuth app limit
    how_to_resolve: Delete unused OAuth apps under the same owner, or create the app under a different
      organization/account with available quota
    escalation: No GitHub support escalation; hard limit enforced by platform
  - issue: Token request rate limit exceeded (2,000/hour)
    how_to_resolve: Implement token caching, reduce redundant token exchanges, use refresh tokens instead
      of re-authorizing
    escalation: Wait for limit reset; no manual override
  - issue: Client secret lost
    how_to_resolve: Generate a new client secret in the OAuth app settings (invalidates the old one immediately)
    escalation: Self-service in developer console
  agent_vs_human:
    agent_can:
    - Research required scopes and permissions
    - Draft OAuth app manifest (name, homepage, callback URLs, description)
    - Prepare authorization URL with PKCE parameters and state
    - Implement token exchange and refresh logic
    - Monitor rate limit headers and handle backoff
    human_must:
    - Sign in to GitHub.com (interactive login, 2FA)
    - Navigate to Developer Settings and click "New OAuth App"
    - Fill and submit the registration form
    - Copy Client ID and generate/copy Client Secret at generation time
    - Complete SAML SSO for target organizations (tokens only access orgs where SSO is done)
  composio_next:
    managed: false
    managed_note: Not in Composio catalog; BYO credentials required
    redirect_uri_to_register: https://backend.composio.dev/api/v3/toolkits/auth/callback
    auth_config_fields:
    - client_id
    - client_secret
    - redirect_uri
    - scopes
    auth_config_snippet: "from composio import Composio\n\nconfig = Composio().auth_configs.create(\n\
      \    name=\"github-oauth\",\n    options={\n        \"type\": \"use_custom_auth\",\n        \"auth_scheme\"\
      : \"OAUTH2\",\n        \"credentials\": {\n            \"client_id\": \"{{CLIENT_ID}}\",\n     \
      \       \"client_secret\": \"{{CLIENT_SECRET}}\",\n            \"redirect_uri\": \"https://backend.composio.dev/api/v3/toolkits/auth/callback\"\
      ,\n            \"scopes\": [\"repo\", \"user\", \"offline_access\"]\n        }\n    }\n)"
    mcp_note: Use custom auth config with OAuth2 scheme; ensure redirect_uri matches one of the 10 registered
      callbacks. Scopes requested at authorization time; offline_access enables refresh tokens.
---

# GitHub OAuth App Setup Guide

Register a GitHub OAuth App in minutes: GitHub runs no app review, and the app can be used as soon as you have its client ID and client secret (organizations can still require owner approval under an OAuth app policy before it is authorized). Supports up to 10 callback URLs, 100 apps per owner, and standard OAuth2 with PKCE (S256 only; plain is not supported). 'Expire user access tokens' is enabled by default, giving 8-hour access tokens and refresh tokens that expire after 6 months without use. GitHub recommends GitHub Apps for finer-grained permissions.

## Difficulty & time

No GitHub app review; client ID/secret are available immediately after registration — note that organizations can still require owner approval via an OAuth app policy before members can authorize the app

- **Difficulty:** Instant (1/5)
- **Hands-on setup:** 5-10 minutes
- **Approval wait:** None

## Prerequisites

- **Required:** GitHub account — Personal account, or an organization where you have administrative access — docs: you can register an OAuth app under your personal account or under any organization you have administrative access to
- **Required:** Public homepage URL — A publicly accessible URL for your application; docs warn to avoid sensitive data such as internal URLs in your OAuth app
- **Required:** Callback URL(s) — At least one redirect URI (e.g., https://backend.composio.dev/api/v3/toolkits/auth/callback); up to 10 allowed. The redirect_uri your app sends must exactly match a registered callback URL unless wildcard matching is enabled (loopback addresses supported for local development)

## Step-by-step

### 1. Sign in to GitHub (https://github.com)
Log in with the personal account or organization that will own the OAuth app
*[~1 minute, human step; evidence: verified_from_docs]*
> If creating under an organization, you need administrative access to that org (docs: apps can be registered under your personal account or any organization you have administrative access to)

### 2. Open Developer Settings → OAuth Apps (https://github.com/settings/developers)
Click profile picture → Settings → Developer settings → OAuth apps
*[~1 minute, human step; evidence: verified_from_docs]*
> Direct URL https://github.com/settings/developers works if already logged in

### 3. Create new OAuth App (https://github.com/settings/developers)
Click "New OAuth App" (or "Register a new application" if first app)
*[~30 seconds, human step; evidence: verified_from_docs]*
> Owner can be your personal account or any organization where you have administrative access

### 4. Fill required registration fields (GitHub OAuth App registration form)
Enter Application name, Homepage URL, Authorization callback URL (add up to 10 via "Add callback URL"). Optionally add description, enable Device Flow (only if CLI/IoT/headless), and keep "Expire user access tokens" checked (default). Click "Register application".
*[~3-5 minutes, human step; evidence: verified_from_docs]*
> Docs do not impose a blanket HTTPS rule on callback URLs; avoid using sensitive data such as internal URLs in the app's information. Device Flow carries phishing risk if not needed; prefer authorization code with PKCE. "Expire user access tokens" is enabled by default: 8-hour access token, 6-month refresh token (lifetimes documented on the Authorizing OAuth apps page).

### 5. Copy Client ID and generate Client Secret (OAuth App details page (after registration))
Copy the Client ID. Generate the Client Secret and copy it immediately (the UI displays it once — not stated in docs). Store both securely.
*[~1 minute, human step; evidence: verified_from_docs]*
> Every registered OAuth app is assigned a unique Client ID and Client Secret; never leak the secret and store it (e.g., environment variables or a key vault). If lost, generate a new one from the app settings (UI behavior — not documented). No app review — credentials work immediately.

### 6. Configure scopes at authorization time (Your application's OAuth authorization URL)
When building the authorization URL, include desired scopes (e.g., repo, user, admin:org, offline_access). Scopes are not set during registration; users may grant fewer than requested.
*[~Development time, agent-automatable; evidence: verified_from_docs]*
> Roughly 35 scopes documented (including offline_access); overlapping scopes normalized (user + user:email → user). offline_access yields an expiring access token + refresh token even if the app is not configured for expiring tokens. Users may grant fewer scopes than requested — handle reduced access gracefully.

### 7. Implement OAuth flow with PKCE and state (Your application code)
Use authorization code grant with PKCE (code_challenge_method=S256; plain is not supported) and a random state parameter for CSRF protection. Exchange code for token within 10 minutes (code lifetime). Handle token refresh using refresh_token (if expiring tokens enabled); refresh rotates the token pair and scope cannot be changed on refresh.
*[~Development time, agent-automatable; evidence: verified_from_docs]*
> redirect_uri must exactly match a registered callback URL unless wildcard matching is enabled; loopback URLs may use a different port than the registered callback. Token limits: 2,000 access token requests/hour and ten tokens created per user/application/scope combination per hour (see Rate limits for OAuth apps page). SAML SSO: tokens do not access organizations where the user has not completed SSO; check GET /user/installations regularly (see Best practices page).

## Gotchas

- **Token request and sign-in rate limits** — OAuth apps are limited to 2,000 access token requests per hour; if an app signs the user in ten times within one hour, the next sign-in within the same hour requires re-authorization. There is also a limit of ten tokens issued per user/application/scope combination and a rate limit of ten tokens created per hour.
  - Handle: Cache tokens, implement exponential backoff, and avoid redundant token exchanges
- **REST API rate limit is the user's 5,000 requests/hour** — OAuth app tokens use the authenticated user's rate limit of 5,000 requests per hour, shared with other requests made on the user's behalf — GitHub Apps instead get limits that scale with users/repositories.
  - Handle: Monitor the x-ratelimit-* response headers (the authoritative rate limit status), honor x-ratelimit-reset before retrying, and back off on 403/429 responses
- **Token expiration default (8h access, 6-month refresh)** — With "Expire user access tokens" enabled (the default), the access token expires after 8 hours and the refresh token expires after 6 months without use; refresh rotates the pair (old access and refresh tokens stop working) and scope cannot be changed on refresh. Docs frame unchecking the option for apps not yet updated to support short-lived tokens; requesting the offline_access scope yields expiring tokens even when the app-level setting is off.
  - Handle: Implement refresh token flow; store refresh tokens securely (separately from access tokens); handle 401 by refreshing
- **100 OAuth apps per owner limit** — A single user or organization cannot own more than 100 OAuth apps
  - Handle: Audit existing apps; delete unused ones; consider GitHub Apps for new integrations
- **Maximum 10 callback URLs per app** — Cannot add more than 10 redirect URIs; wildcard matching should only be enabled when necessary because it lets an attacker send authorization codes
  - Handle: Plan all environments (dev, staging, prod) upfront; use path-based differentiation
- **Device Flow phishing risk** — Enabling Device Flow without need exposes phishing risk; the device flow needs no redirect URIs, so an attacker can remotely impersonate your app. Prefer authorization code with PKCE.
  - Handle: Leave unchecked unless building a device-authorization-grant flow
- **SAML SSO restrictions** — If an organization uses SAML SSO and the user has not performed SAML SSO, the user access token will not have access to that organization
  - Handle: Regularly check the GET /user/installations endpoint to verify which organizations a token can access; guide users to complete SSO for target orgs
- **Organization OAuth app policies can gate usage** — There is no GitHub-run review of OAuth apps, but organizations can restrict them: when an organization application policy is active, a member's request to install an OAuth app must be approved or denied by an organization owner before it can be used.
  - Handle: Before rolling out inside an organization, check its OAuth app policy and have an owner approve the app
- **GitHub Apps preferred for new integrations** — GitHub Apps offer fine-grained permissions, repository-level install, short-lived tokens (installation tokens expire after about 1 hour), and rate limits that scale with users/repositories; OAuth apps can only act as the authenticated user and use the user's 5,000 requests/hour limit
  - Handle: Evaluate GitHub App instead if you need repo-scoped access, higher limits, or organization-level installation

## Common blockers

- **Owner has reached 100 OAuth app limit** — Delete unused OAuth apps under the same owner, or create the app under a different organization/account with available quota
  - Escalation: No GitHub support escalation; hard limit enforced by platform
- **Token request rate limit exceeded (2,000/hour)** — Implement token caching, reduce redundant token exchanges, use refresh tokens instead of re-authorizing
  - Escalation: Wait for limit reset; no manual override
- **Client secret lost** — Generate a new client secret in the OAuth app settings (invalidates the old one immediately)
  - Escalation: Self-service in developer console

## What the agent can do vs. you

**An agent can:** Research required scopes and permissions; Draft OAuth app manifest (name, homepage, callback URLs, description); Prepare authorization URL with PKCE parameters and state; Implement token exchange and refresh logic; Monitor rate limit headers and handle backoff.
**You must:** Sign in to GitHub.com (interactive login, 2FA); Navigate to Developer Settings and click "New OAuth App"; Fill and submit the registration form; Copy Client ID and generate/copy Client Secret at generation time; Complete SAML SSO for target organizations (tokens only access orgs where SSO is done).

## Connect it via Composio

Register this redirect URI in the provider console: `https://backend.composio.dev/api/v3/toolkits/auth/callback`
Then create the auth config with: client_id, client_secret, redirect_uri, scopes.

```python
from composio import Composio

config = Composio().auth_configs.create(
    name="github-oauth",
    options={
        "type": "use_custom_auth",
        "auth_scheme": "OAUTH2",
        "credentials": {
            "client_id": "{{CLIENT_ID}}",
            "client_secret": "{{CLIENT_SECRET}}",
            "redirect_uri": "https://backend.composio.dev/api/v3/toolkits/auth/callback",
            "scopes": ["repo", "user", "offline_access"]
        }
    }
)
```

Use custom auth config with OAuth2 scheme; ensure redirect_uri matches one of the 10 registered callbacks. Scopes requested at authorization time; offline_access enables refresh tokens.

## Evidence

- [Creating an OAuth app](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) — Registration steps and navigation, required/optional form fields, "Enable Device Flow" checkbox, "Expire user access tokens" enabled by default, up to 10 callback URLs, up to 100 OAuth apps per user/organization, registration under personal account or organization with administrative access, avoid sensitive/internal URLs warning
- [Building OAuth apps (overview)](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps) — OAuth apps act on behalf of a user; scopes limit token access; GitHub Apps preferred for fine-grained permissions and short-lived tokens. Does not document any review process either way
- [Authorizing OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps) — Authorization URL and parameters (client_id, redirect_uri, scope, state), PKCE S256 (plain unsupported), 10-minute authorization code lifetime, POST /login/oauth/access_token, refresh_token grant and rotation, 8-hour access token / 6-month refresh token, offline_access scope, ten tokens per user/application/scope combination and ten created per hour, redirect_uri exact-match rule and loopback port exception
- [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps) — Scope list (~35 including offline_access), scope normalization (user + user:email → user), users may grant fewer scopes than requested, offline_access behavior
- [Rate limits for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/rate-limits-for-oauth-apps) — 2,000 access token requests/hour, 10 sign-ins per user/hour then re-authorization required, secondary rate limits, GitHub Apps limits scale while OAuth app limits are lower
- [Best practices for creating an OAuth app](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/best-practices-for-creating-an-oauth-app) — Wildcard callbacks only when necessary, device flow phishing risk, 8-hour/6-month token lifetimes, secure storage of client secret and tokens, SAML SSO check via GET /user/installations, GitHub Apps preferred
- [Differences between GitHub Apps and OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/differences-between-github-apps-and-oauth-apps) — Granular permissions vs scopes, repository-level installation, ~1-hour installation tokens, OAuth apps use the user's 5,000 requests/hour limit, organization owner approval of OAuth app installs under org application policy
- [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) — 5,000 requests/hour personal rate limit for user access tokens, x-ratelimit-* headers as authoritative status, 5,000 requests/hour per OAuth app when fetching public data with client ID/secret
- [Authenticating to the REST API with an OAuth app](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authenticating-to-the-rest-api-with-an-oauth-app) — Every registered OAuth app is assigned a unique Client ID and Client Secret; do not leak the secret; store as environment variables

**Could not verify:**
- Exact Composio integration behavior for GitHub OAuth (snippet not verifiable from GitHub docs)
- Whether GitHub enforces any unpublished limits beyond documented ones
- Whether the OAuth app client secret can be viewed again after generation (docs never state 'shown only once'; that is UI behavior)
- Whether non-loopback plain-HTTP callback URLs are accepted (docs state no blanket HTTPS requirement — only the loopback port exception for redirect_uri matching is documented)
- An explicit official statement that OAuth apps undergo no review/approval (no OAuth docs page mentions a review process; organization-level OAuth app policies can still require owner approval before use)

*Last checked: 2026-11-03 · Status: `stable` · Generated by agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b · Verified by human:verification-pass*