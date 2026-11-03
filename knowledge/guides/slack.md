---
type: oauth_guide
okf_version: '0.2'
resource: slack
title: Slack OAuth App Setup Guide
tags:
- marketplace
- multi-workspace
- oauth2
- slack
- v2-oauth
status: stable
stale_after: '2027-05-02'
generated:
  by: agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b
  at: '2026-11-03T17:25:34.638480Z'
verified:
  by: human:verification-pass
  at: '2026-11-03T17:53:07.341381Z'
chatbot:
  visible: true
  priority: primary
badge: library
last_checked: '2026-11-03'
unverified:
- Rate limit for the oauth/v2/authorize endpoint (oauth.v2.access documents 600 requests/minute; the authorize
  endpoint has no published limit)
- Classic Slack app (V1 OAuth) deprecation schedule
- Whether the Client Secret is shown only once at creation (not documented; Basic Information lists the
  credentials and 'Change secret' resets them)
- Composio claim that Slack is not in the Composio catalog / has no managed OAuth (outside official Slack
  documentation; verify against Composio directly)
sources:
- url: https://docs.slack.dev/authentication/installing-with-oauth
  title: Installing with OAuth (redirects from api.slack.com/authentication/oauth-v2)
  what_it_supports: OAuth V2 endpoints, redirect_uri match/subdirectory rules, HTTPS requirement, no fragments,
    first-URL fallback, same redirect_uri in Authorize+Access, 10-minute code expiry, xoxb/xoxp tokens,
    state validation, SIWS scope conflict, optional scopes, scope downgrade prohibition, org-level installs
    needing Org Owner/Admin
- url: https://docs.slack.dev/app-management/distribution
  title: App lifecycle & distribution
  what_it_supports: Three distribution options (single workspace, unlisted public distribution, Slack
    Marketplace); unlisted distribution via 'Activate Public Distribution' needs NO review; Marketplace
    listing is reviewed; distribution checklist (OAuth flow, SSL URLs)
- url: https://docs.slack.dev/slack-marketplace/slack-marketplace-review-guide
  title: Slack Marketplace review process
  what_it_supports: Submission from 'Submit to the Slack Marketplace' section; 10+ active workspaces prerequisite;
    preliminary review up to 10 business days; functional review up to 10 weeks (new) / 6 weeks (resubmit);
    video demo; publish-after-approval; live app locked; return-and-resubmit process
- url: https://docs.slack.dev/slack-marketplace/slack-marketplace-app-guidelines-and-requirements
  title: Submission guidelines and requirements
  what_it_supports: Privacy policy, public support page (2-business-day response), scope justifications,
    10 active workspaces / 20 MAU suitability threshold, ToS agreements for Marketplace distribution,
    no formal appeal described, resubmission after substantial changes
- url: https://docs.slack.dev/changelog/2026/09/01/slack-marketplace-install-requirement
  title: Updated installation requirement for Slack Marketplace apps
  what_it_supports: As of July 2026 apps need at least 10 installations on active workspaces, maintained
    throughout the entire review
- url: https://docs.slack.dev/app-management/quickstart-app-settings
  title: Creating an app from app settings
  what_it_supports: 'Console creation flow: api.slack.com/apps?new_app=1, ''Blank app'' → Continue, App
    Name, workspace selection, Create'
- url: https://docs.slack.dev/tools/bolt-python/creating-an-app
  title: Creating an app with Bolt for Python
  what_it_supports: Scopes added under OAuth & Permissions before install; 'Install App to Workspace'
    button; Bot User OAuth Access Token display after install; Basic Information holds app credentials;
    sandbox workspace advice
- url: https://docs.slack.dev/reference/app-manifest
  title: App manifest reference
  what_it_supports: oauth_config.token_management_enabled, settings.token_rotation_enabled, oauth_config.scopes.bot/user/bot_optional/user_optional,
    oauth_config.redirect_urls, YAML/JSON formats
- url: https://docs.slack.dev/app-manifests/configuring-apps-with-app-manifests
  title: Configuring apps with app manifests (redirects from api.slack.com/reference/manifests)
  what_it_supports: YAML/JSON manifests, creating apps from a manifest, scope additions only take effect
    for existing installs after workspaces reinstall
- url: https://docs.slack.dev/authentication/using-token-rotation
  title: Using token rotation (redirects from api.slack.com/authentication/rotation)
  what_it_supports: 'Rotation optional but irreversible; settings.token_rotation_enabled: true; OAuth
    & Permissions toggle; expires_in 43200 (12 hours); xoxe. prefix; single-use refresh tokens with grace
    period; 2-active-token limit; oauth.v2.exchange and grant_type=refresh_token'
- url: https://docs.slack.dev/authentication/tokens
  title: Tokens (redirects from api.slack.com/authentication/token-types)
  what_it_supports: Bot tokens begin with xoxb-, user tokens with xoxp-, app-level tokens with xapp-
- url: https://docs.slack.dev/reference/scopes
  title: Scopes reference (redirects from api.slack.com/scopes)
  what_it_supports: chat:write, commands, channels:history, openid, email, profile definitions
- url: https://docs.slack.dev/authentication/best-practices-for-security
  title: Best practices for security (redirects from api.slack.com/authentication/best-practices)
  what_it_supports: Never hardcode credentials; secrets managers in production; do not distribute client
    secrets; limit redirect URIs to domains in your control
- url: https://docs.slack.dev/reference/methods/oauth.v2.access
  title: oauth.v2.access method reference
  what_it_supports: 600-per-minute rate limit (t5) for oauth.v2.access; redirect_uri required only if
    sent in the authorize step; Basic auth recommendation for client_id/client_secret; xoxb/xoxp and xoxe.
    rotated token examples
- url: https://docs.slack.dev/enterprise/developing-for-enterprise-orgs
  title: Developing apps for Enterprise orgs
  what_it_supports: 'Org-wide installs require Org Admin approval (Slack DM review); admin installs to
    org then selects workspaces; org_deploy_enabled: true; org install does not auto-add to workspaces'
- url: https://docs.slack.dev/faq
  title: Slack developer FAQ
  what_it_supports: Client secret reset via 'Change secret' button (no statement that the secret is shown
    only once)
- url: https://docs.slack.dev/tools/node-slack-sdk/oauth/
  title: Node Slack SDK OAuth guide
  what_it_supports: State verification strongly recommended (CSRF mitigation); InstallationStore/StateStore
    — and confirms the page does NOT contain a manifest example or token_management_enabled (draft mis-citation)
- url: https://api.slack.com/apps
  title: Slack Developer Console (Your Apps)
  what_it_supports: Sign-in required to create an application; console entry point
guide:
  summary: Create a Slack app using V2 OAuth (multi-workspace) via the Slack developer console. Configure
    redirect URLs, bot/user scopes, and install to a development workspace. Sharing the app with other
    workspaces via the shareable install URL ('Activate Public Distribution' under Manage Distribution)
    requires NO Slack review; listing in the Slack Marketplace is a separate, optional review process
    (up to 10 business days preliminary feedback, then up to 10 weeks functional review for new submissions).
  app_website: https://slack.com
  developer_console: https://api.slack.com/apps
  oauth_docs: https://docs.slack.dev/authentication/installing-with-oauth/
  difficulty:
    level: 2
    tier: Light
    verdict: Standard OAuth 2.0 flow with Slack-specific redirect rules and scope separation; no formal
      review for development installs.
  time:
    hands_on: 30-60 minutes
    approval_wait: 'None for development workspace; Slack Marketplace review: up to 10 business days for
      preliminary feedback, then up to 10 weeks for functional review of new submissions (6 weeks for
      published apps resubmitting changes)'
    verdict: Quick for dev install; Marketplace review wait is officially published (up to 10 business
      days + up to 10 weeks), not unverified.
  prerequisites:
  - item: Slack account
    detail: Sign in at https://slack.com before accessing the developer console.
    blocking: true
  - item: Development workspace
    detail: A Slack workspace where you can install the app for testing.
    blocking: true
  - item: HTTPS redirect endpoint
    detail: Redirect URI must use HTTPS (no HTTP, no localhost without TLS). Use a tunnel (ngrok, cloudflared)
      for local testing.
    blocking: true
  steps:
  - n: 1
    title: Sign in to Slack
    where: https://slack.com
    action: Create or sign in to your Slack account.
    duration: 2 minutes
    agent_automatable: false
    human_because: Requires interactive login and possible MFA.
    nuances: 'Account must have access to a workspace for development. The ''Your Apps'' console states:
      ''You''ll need to sign in to your Slack account to create an application.'''
    evidence: verified_from_docs
    source_url: https://api.slack.com/apps
  - n: 2
    title: Open the Slack developer console
    where: https://api.slack.com/apps
    action: Navigate to 'Your Apps' and click 'Create an app' (it links to api.slack.com/apps?new_app=1).
    duration: 1 minute
    agent_automatable: false
    human_because: Console requires authenticated session.
    nuances: Current docs say to select 'Blank app' then 'Continue' (not 'From scratch'); 'From a manifest'
      is the alternative if you have a YAML/JSON manifest.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/app-management/quickstart-app-settings
  - n: 3
    title: Create the app and select development workspace
    where: https://api.slack.com/apps (app creation flow)
    action: Enter your App Name, select the development workspace, and click 'Create'.
    duration: 2 minutes
    agent_automatable: false
    human_because: Workspace selection and app naming are manual console steps.
    nuances: This workspace will be used for initial install and testing. Slack suggests a workspace 'where
      you won't disrupt real work getting done, like a developer sandbox'.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/app-management/quickstart-app-settings
  - n: 4
    title: Record Client ID and Client Secret
    where: App settings → Basic Information
    action: Copy the Client ID and Client Secret from the Basic Information page, which contains 'important
      credentials you'll need later'. Store the secret securely; if it leaks, reset it with the 'Change
      secret' button.
    duration: 2 minutes
    agent_automatable: false
    human_because: Credentials are displayed only in the authenticated console.
    nuances: Also note the Signing Secret for request verification. The draft's 'shown once' claim is
      not documented anywhere and should be dropped — Slack documents a 'Change secret' reset flow, implying
      the secret is not one-time-displayed.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/tools/bolt-python/creating-an-app
  - n: 5
    title: Configure Redirect URL(s)
    where: App settings → OAuth & Permissions → Redirect URLs
    action: Add one or more HTTPS redirect URLs. Your redirect_uri must match or be a subdirectory of
      a Redirect URL configured under App Management. If multiple URLs are added, the same redirect_uri
      must be sent in both the Authorize and Access steps (otherwise bad_redirect_uri).
    duration: 5 minutes
    agent_automatable: false
    human_because: Console form requires manual entry and save.
    nuances: 'No HTTP, no fragments (#), no wildcards. If multiple Redirect URLs are configured but no
      redirect_uri is sent, ''the OAuth flow will use the first Redirect URL listed on the App Management
      page''. Example: https://example.com/callback or https://backend.composio.dev/api/v3/toolkits/auth/callback'
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - n: 6
    title: Add Bot Token Scopes and User Token Scopes
    where: App settings → OAuth & Permissions → Scopes
    action: Add required bot scopes (e.g., chat:write, commands) under 'Bot Token Scopes' and user scopes
      (e.g., channels:history) under 'User Token Scopes'. Add all needed scopes BEFORE installing; mark
      scopes optional via the app settings or bot_optional/user_optional in the manifest.
    duration: 10 minutes
    agent_automatable: false
    human_because: Scope selection is a manual console action.
    nuances: SIWS scopes (openid, email, profile) must be requested in a separate OAuth flow. Users may
      deselect optional scopes during install; handle missing_scope errors gracefully. There is no per-scope
      'Required' checkbox in the manifest — optional scopes are declared via bot_optional/user_optional
      arrays, which 'must also be listed in the corresponding bot/user fields'.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - n: 7
    title: Install app to development workspace
    where: App settings → OAuth & Permissions → Install App to Workspace
    action: Click 'Install App to Workspace', authorize the requested scopes, and capture the initial
      bot/user tokens for testing.
    duration: 5 minutes
    agent_automatable: false
    human_because: Requires interactive authorization in the workspace.
    nuances: Generates xoxb- (bot) and xoxp- (user) tokens; after authorizing you land back on OAuth &
      Permissions to see the Bot User OAuth Access Token. No formal review needed for your own workspace
      (undistributed apps live on a single workspace). Scope changes require a reinstall to take effect
      on existing installs.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/tools/bolt-python/creating-an-app
  - n: 8
    title: (Optional) Define App Manifest for version control
    where: App settings → App Manifest
    action: Create or import a YAML/JSON manifest containing scopes (oauth_config.scopes.bot/user plus
      bot_optional/user_optional), redirect URLs (oauth_config.redirect_urls), and token rotation settings.
      Enables easy replication and CI/CD.
    duration: 10 minutes
    agent_automatable: true
    human_because: Manifest can be drafted by agent; human only needs to paste/save in console.
    nuances: 'Enable token rotation with settings.token_rotation_enabled: true (or the OAuth & Permissions
      toggle) — the draft''s ''token_management_enabled: true'' is a different oauth_config field. Rotation
      cannot be turned off once enabled. The Node SDK OAuth guide cited by the draft contains no manifest
      example; use the app manifest reference instead.'
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/reference/app-manifest
  - n: 9
    title: Implement OAuth 2.0 authorization code flow (for multi-workspace distribution)
    where: Your application code
    action: Direct users to https://slack.com/oauth/v2/authorize with client_id, scope, user_scope (optional),
      redirect_uri, state. Exchange the returned code (10-min lifetime) at https://slack.com/api/oauth.v2.access
      with client_id, client_secret, code, and redirect_uri (send the same value in both Authorize and
      Access steps when multiple redirect URLs are configured). Validate state — a mismatch means 'consider
      the authorization a forgery'. Store per-workspace/enterprise installation data (team.id, enterprise.id,
      is_enterprise_install, tokens).
    duration: 30-60 minutes
    agent_automatable: true
    human_because: Code implementation can be automated; human reviews and deploys.
    nuances: If no redirect_uri is sent, Slack uses the first Redirect URL listed under App Management;
      redirect_uri is required in the token exchange only if it was sent in the authorize step. SIWS scopes
      require a separate flow. Token rotation uses refresh tokens when enabled (access tokens then expire
      every 12 hours and carry an xoxe. prefix).
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - n: 10
    title: (Optional) Share the app for public install — no review needed
    where: App settings → Manage Distribution → Activate Public Distribution
    action: Complete the distribution checklist (working OAuth 2.0 flow, SSL for all request URLs, only
      the permissions you need) and activate public distribution to get a shareable install URL and an
      embeddable 'Add to Slack' button.
    duration: 5 minutes
    agent_automatable: false
    human_because: Checklist sign-off and activation are manual console actions.
    nuances: Unlisted distribution does NOT require Slack review — Slack calls it 'perfect for when you
      want to test out your app by running a pilot for early customers'. Slack review applies only to
      Slack Marketplace listing (directory presence).
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/app-management/distribution
  - n: 11
    title: (Optional) Submit to Slack Marketplace for directory listing
    where: App settings → 'Submit to the Slack Marketplace' section
    action: Meet the prerequisites (app installed on 10+ active workspaces, fully tested including uninstalling
      it, privacy policy, publicly accessible support page, per-scope justifications, video demo of the
      full install/OAuth flow), then submit for review.
    duration: Variable (preparation 1-2 hours)
    agent_automatable: false
    human_because: Legal documents, scope justification, and submission require human decisions.
    nuances: Apps under 10 installed active workspaces 'will be blocked from submitting'. Preliminary
      review feedback 'generally takes up to 10 business days'; functional review takes 'up to 10 weeks
      for new submissions and 6 weeks for published apps resubmitting changes'. After approval you publish
      at a time of your choosing; the live version is locked until changes are resubmitted.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/slack-marketplace/slack-marketplace-review-guide
  gotchas:
  - title: Redirect URI strict matching
    why_it_matters: Slack requires the redirect_uri to match or be a subdirectory of a configured Redirect
      URL; no wildcards, no HTTP, no fragments (#). Mismatch causes a bad_redirect_uri error.
    how_to_handle: Register the precise HTTPS callback URL (e.g., https://backend.composio.dev/api/v3/toolkits/auth/callback).
      If multiple URLs, send identical redirect_uri in both Authorize and Access requests. If none is
      sent, Slack falls back to the first Redirect URL listed under App Management.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - title: Authorization code expires in 10 minutes
    why_it_matters: The code returned from the authorization redirect is 'your temporary authorization
      code, which expires after ten minutes' and must be exchanged at oauth.v2.access within that window.
    how_to_handle: Exchange the code immediately in your callback handler; implement retry/queue if needed.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - title: SIWS scopes cannot be mixed with bot/user scopes
    why_it_matters: '''A scope conflict occurs when attempting to combine Sign in with Slack (SIWS) user
      scopes with non-Sign in with Slack scopes in the same OAuth flow'' and ''Each set of scopes must
      be requested in a separate OAuth flow'' (invalid_scope error).'
    how_to_handle: Run a separate OAuth flow for Sign in with Slack using only SIWS scopes (openid, email,
      profile).
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - title: Optional scopes may be deselected by user
    why_it_matters: Optional scopes (bot_optional/user_optional in the manifest) are presented to the
      installer, 'who can choose which ones to grant'; your app must handle missing scopes gracefully.
    how_to_handle: Check the scope field in the token response to see which scopes were granted; gate
      features accordingly and handle missing_scope errors.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - title: Token rotation requires secure refresh token storage
    why_it_matters: When token rotation is enabled, access tokens expire every 12 hours (expires_in is
      always 43,200 seconds) and carry an xoxe. prefix; refresh tokens are single-use and 'revoked after
      a short grace period'; Slack enforces a limit of 2 active tokens. Rotation 'may not be turned off
      once it's turned on'.
    how_to_handle: 'Enable via settings.token_rotation_enabled: true in the manifest or the OAuth & Permissions
      toggle. Store refresh tokens encrypted; refresh via oauth.v2.access with grant_type=refresh_token
      (initial conversion of a legacy token uses oauth.v2.exchange).'
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/using-token-rotation
  - title: Localhost testing requires HTTPS
    why_it_matters: The current OAuth V2 docs state 'The redirect_uri must use HTTPS' with no localhost
      exception; only the legacy Sign-in-with-Slack docs allowed plain-http localhost redirects.
    how_to_handle: Use ngrok, cloudflared, or a local HTTPS proxy (e.g., mkcert) to expose https://localhost:port.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/authentication/installing-with-oauth
  - title: Scope changes require reinstall; scopes can be added but never downgraded
    why_it_matters: '''Some manifest changes, such as adding scopes, only take effect for existing installs
      after workspaces reinstall your app.'' Scopes cannot be removed from a live token: ''It is not possible
      to downgrade an access token''s scopes'' — removal requires revoking the token.'
    how_to_handle: Finalize scopes before install. After adding scopes, reinstall in each workspace. Read
      the granted scopes from the token response and gate features rather than assuming all requested
      scopes are live.
    evidence: verified_from_docs
    source_url: https://docs.slack.dev/app-manifests/configuring-apps-with-app-manifests
  blockers:
  - issue: Marketplace review wait is long and now officially published (no longer unknown)
    how_to_resolve: Plan for up to 10 business days of preliminary feedback plus up to 10 weeks of functional
      review for new submissions (6 weeks for resubmissions). The app must be installed on 10 or more
      active workspaces before submitting or it 'will be blocked from submitting'; prepare the video demo,
      privacy policy, public support page, and per-scope justifications first.
    escalation: Feedback arrives in the submission flow and via email; address all feedback and resubmit.
      Note that resubmitting during preliminary review resets your queue position.
  - issue: OAuth endpoint rate limits are only partially documented
    how_to_resolve: oauth.v2.access documents a rate limit of 600 requests per minute (tier t5, 'Special
      rate limits apply'); no published limit exists for the oauth/v2/authorize endpoint. Implement exponential
      backoff and respect Retry-After headers; monitor for 429 responses.
    escalation: File a support ticket if consistent rate limiting blocks legitimate traffic.
  agent_vs_human:
    agent_can:
    - Research Slack OAuth docs and scope lists
    - Draft App Manifest YAML/JSON
    - Prepare scope justification and privacy policy templates
    - Generate authorization URL with correct parameters
    - Implement token exchange and storage logic
    - Configure Composio auth config with credentials
    human_must:
    - Sign in to Slack and access developer console
    - Create the app and select development workspace
    - Enter redirect URLs and scopes in the console UI
    - Click 'Install to Workspace' and authorize
    - Accept Slack API Terms of Service
    - Submit to Marketplace and provide legal URLs
    - Store client_secret and signing_secret securely
  composio_next:
    managed: false
    managed_note: Slack is not in the Composio catalog; no managed OAuth available.
    redirect_uri_to_register: https://backend.composio.dev/api/v3/toolkits/auth/callback
    auth_config_fields:
    - client_id
    - client_secret
    - redirect_uri
    - scopes
    - user_scopes
    - auth_url
    - token_url
    auth_config_snippet: "from composio import Composio\n\ncomposio = Composio()\nauth_config = composio.auth_configs.create(\n\
      \    name=\"slack-oauth\",\n    auth_scheme=\"OAUTH2\",\n    credentials={\n        \"client_id\"\
      : \"{{CLIENT_ID}}\",\n        \"client_secret\": \"{{CLIENT_SECRET}}\",\n        \"redirect_uri\"\
      : \"https://backend.composio.dev/api/v3/toolkits/auth/callback\",\n        \"scopes\": [\"chat:write\"\
      , \"commands\"],\n        \"user_scopes\": [\"channels:history\"],\n        \"auth_url\": \"https://slack.com/oauth/v2/authorize\"\
      ,\n        \"token_url\": \"https://slack.com/api/oauth.v2.access\"\n    },\n    options={\"type\"\
      : \"use_custom_auth\"}\n)"
    mcp_note: Use the created auth_config ID when setting up Slack toolkit connections via Composio MCP.
---

# Slack OAuth App Setup Guide

Create a Slack app using V2 OAuth (multi-workspace) via the Slack developer console. Configure redirect URLs, bot/user scopes, and install to a development workspace. Sharing the app with other workspaces via the shareable install URL ('Activate Public Distribution' under Manage Distribution) requires NO Slack review; listing in the Slack Marketplace is a separate, optional review process (up to 10 business days preliminary feedback, then up to 10 weeks functional review for new submissions).

## Difficulty & time

Standard OAuth 2.0 flow with Slack-specific redirect rules and scope separation; no formal review for development installs.

- **Difficulty:** Light (2/5)
- **Hands-on setup:** 30-60 minutes
- **Approval wait:** None for development workspace; Slack Marketplace review: up to 10 business days for preliminary feedback, then up to 10 weeks for functional review of new submissions (6 weeks for published apps resubmitting changes)

## Prerequisites

- **Required:** Slack account — Sign in at https://slack.com before accessing the developer console.
- **Required:** Development workspace — A Slack workspace where you can install the app for testing.
- **Required:** HTTPS redirect endpoint — Redirect URI must use HTTPS (no HTTP, no localhost without TLS). Use a tunnel (ngrok, cloudflared) for local testing.

## Step-by-step

### 1. Sign in to Slack (https://slack.com)
Create or sign in to your Slack account.
*[~2 minutes, human step; evidence: verified_from_docs]*
> Account must have access to a workspace for development. The 'Your Apps' console states: 'You'll need to sign in to your Slack account to create an application.'

### 2. Open the Slack developer console (https://api.slack.com/apps)
Navigate to 'Your Apps' and click 'Create an app' (it links to api.slack.com/apps?new_app=1).
*[~1 minute, human step; evidence: verified_from_docs]*
> Current docs say to select 'Blank app' then 'Continue' (not 'From scratch'); 'From a manifest' is the alternative if you have a YAML/JSON manifest.

### 3. Create the app and select development workspace (https://api.slack.com/apps (app creation flow))
Enter your App Name, select the development workspace, and click 'Create'.
*[~2 minutes, human step; evidence: verified_from_docs]*
> This workspace will be used for initial install and testing. Slack suggests a workspace 'where you won't disrupt real work getting done, like a developer sandbox'.

### 4. Record Client ID and Client Secret (App settings → Basic Information)
Copy the Client ID and Client Secret from the Basic Information page, which contains 'important credentials you'll need later'. Store the secret securely; if it leaks, reset it with the 'Change secret' button.
*[~2 minutes, human step; evidence: verified_from_docs]*
> Also note the Signing Secret for request verification. The draft's 'shown once' claim is not documented anywhere and should be dropped — Slack documents a 'Change secret' reset flow, implying the secret is not one-time-displayed.

### 5. Configure Redirect URL(s) (App settings → OAuth & Permissions → Redirect URLs)
Add one or more HTTPS redirect URLs. Your redirect_uri must match or be a subdirectory of a Redirect URL configured under App Management. If multiple URLs are added, the same redirect_uri must be sent in both the Authorize and Access steps (otherwise bad_redirect_uri).
*[~5 minutes, human step; evidence: verified_from_docs]*
> No HTTP, no fragments (#), no wildcards. If multiple Redirect URLs are configured but no redirect_uri is sent, 'the OAuth flow will use the first Redirect URL listed on the App Management page'. Example: https://example.com/callback or https://backend.composio.dev/api/v3/toolkits/auth/callback

### 6. Add Bot Token Scopes and User Token Scopes (App settings → OAuth & Permissions → Scopes)
Add required bot scopes (e.g., chat:write, commands) under 'Bot Token Scopes' and user scopes (e.g., channels:history) under 'User Token Scopes'. Add all needed scopes BEFORE installing; mark scopes optional via the app settings or bot_optional/user_optional in the manifest.
*[~10 minutes, human step; evidence: verified_from_docs]*
> SIWS scopes (openid, email, profile) must be requested in a separate OAuth flow. Users may deselect optional scopes during install; handle missing_scope errors gracefully. There is no per-scope 'Required' checkbox in the manifest — optional scopes are declared via bot_optional/user_optional arrays, which 'must also be listed in the corresponding bot/user fields'.

### 7. Install app to development workspace (App settings → OAuth & Permissions → Install App to Workspace)
Click 'Install App to Workspace', authorize the requested scopes, and capture the initial bot/user tokens for testing.
*[~5 minutes, human step; evidence: verified_from_docs]*
> Generates xoxb- (bot) and xoxp- (user) tokens; after authorizing you land back on OAuth & Permissions to see the Bot User OAuth Access Token. No formal review needed for your own workspace (undistributed apps live on a single workspace). Scope changes require a reinstall to take effect on existing installs.

### 8. (Optional) Define App Manifest for version control (App settings → App Manifest)
Create or import a YAML/JSON manifest containing scopes (oauth_config.scopes.bot/user plus bot_optional/user_optional), redirect URLs (oauth_config.redirect_urls), and token rotation settings. Enables easy replication and CI/CD.
*[~10 minutes, agent-automatable; evidence: verified_from_docs]*
> Enable token rotation with settings.token_rotation_enabled: true (or the OAuth & Permissions toggle) — the draft's 'token_management_enabled: true' is a different oauth_config field. Rotation cannot be turned off once enabled. The Node SDK OAuth guide cited by the draft contains no manifest example; use the app manifest reference instead.

### 9. Implement OAuth 2.0 authorization code flow (for multi-workspace distribution) (Your application code)
Direct users to https://slack.com/oauth/v2/authorize with client_id, scope, user_scope (optional), redirect_uri, state. Exchange the returned code (10-min lifetime) at https://slack.com/api/oauth.v2.access with client_id, client_secret, code, and redirect_uri (send the same value in both Authorize and Access steps when multiple redirect URLs are configured). Validate state — a mismatch means 'consider the authorization a forgery'. Store per-workspace/enterprise installation data (team.id, enterprise.id, is_enterprise_install, tokens).
*[~30-60 minutes, agent-automatable; evidence: verified_from_docs]*
> If no redirect_uri is sent, Slack uses the first Redirect URL listed under App Management; redirect_uri is required in the token exchange only if it was sent in the authorize step. SIWS scopes require a separate flow. Token rotation uses refresh tokens when enabled (access tokens then expire every 12 hours and carry an xoxe. prefix).

### 10. (Optional) Share the app for public install — no review needed (App settings → Manage Distribution → Activate Public Distribution)
Complete the distribution checklist (working OAuth 2.0 flow, SSL for all request URLs, only the permissions you need) and activate public distribution to get a shareable install URL and an embeddable 'Add to Slack' button.
*[~5 minutes, human step; evidence: verified_from_docs]*
> Unlisted distribution does NOT require Slack review — Slack calls it 'perfect for when you want to test out your app by running a pilot for early customers'. Slack review applies only to Slack Marketplace listing (directory presence).

### 11. (Optional) Submit to Slack Marketplace for directory listing (App settings → 'Submit to the Slack Marketplace' section)
Meet the prerequisites (app installed on 10+ active workspaces, fully tested including uninstalling it, privacy policy, publicly accessible support page, per-scope justifications, video demo of the full install/OAuth flow), then submit for review.
*[~Variable (preparation 1-2 hours), human step; evidence: verified_from_docs]*
> Apps under 10 installed active workspaces 'will be blocked from submitting'. Preliminary review feedback 'generally takes up to 10 business days'; functional review takes 'up to 10 weeks for new submissions and 6 weeks for published apps resubmitting changes'. After approval you publish at a time of your choosing; the live version is locked until changes are resubmitted.

## Gotchas

- **Redirect URI strict matching** — Slack requires the redirect_uri to match or be a subdirectory of a configured Redirect URL; no wildcards, no HTTP, no fragments (#). Mismatch causes a bad_redirect_uri error.
  - Handle: Register the precise HTTPS callback URL (e.g., https://backend.composio.dev/api/v3/toolkits/auth/callback). If multiple URLs, send identical redirect_uri in both Authorize and Access requests. If none is sent, Slack falls back to the first Redirect URL listed under App Management.
- **Authorization code expires in 10 minutes** — The code returned from the authorization redirect is 'your temporary authorization code, which expires after ten minutes' and must be exchanged at oauth.v2.access within that window.
  - Handle: Exchange the code immediately in your callback handler; implement retry/queue if needed.
- **SIWS scopes cannot be mixed with bot/user scopes** — 'A scope conflict occurs when attempting to combine Sign in with Slack (SIWS) user scopes with non-Sign in with Slack scopes in the same OAuth flow' and 'Each set of scopes must be requested in a separate OAuth flow' (invalid_scope error).
  - Handle: Run a separate OAuth flow for Sign in with Slack using only SIWS scopes (openid, email, profile).
- **Optional scopes may be deselected by user** — Optional scopes (bot_optional/user_optional in the manifest) are presented to the installer, 'who can choose which ones to grant'; your app must handle missing scopes gracefully.
  - Handle: Check the scope field in the token response to see which scopes were granted; gate features accordingly and handle missing_scope errors.
- **Token rotation requires secure refresh token storage** — When token rotation is enabled, access tokens expire every 12 hours (expires_in is always 43,200 seconds) and carry an xoxe. prefix; refresh tokens are single-use and 'revoked after a short grace period'; Slack enforces a limit of 2 active tokens. Rotation 'may not be turned off once it's turned on'.
  - Handle: Enable via settings.token_rotation_enabled: true in the manifest or the OAuth & Permissions toggle. Store refresh tokens encrypted; refresh via oauth.v2.access with grant_type=refresh_token (initial conversion of a legacy token uses oauth.v2.exchange).
- **Localhost testing requires HTTPS** — The current OAuth V2 docs state 'The redirect_uri must use HTTPS' with no localhost exception; only the legacy Sign-in-with-Slack docs allowed plain-http localhost redirects.
  - Handle: Use ngrok, cloudflared, or a local HTTPS proxy (e.g., mkcert) to expose https://localhost:port.
- **Scope changes require reinstall; scopes can be added but never downgraded** — 'Some manifest changes, such as adding scopes, only take effect for existing installs after workspaces reinstall your app.' Scopes cannot be removed from a live token: 'It is not possible to downgrade an access token's scopes' — removal requires revoking the token.
  - Handle: Finalize scopes before install. After adding scopes, reinstall in each workspace. Read the granted scopes from the token response and gate features rather than assuming all requested scopes are live.

## Common blockers

- **Marketplace review wait is long and now officially published (no longer unknown)** — Plan for up to 10 business days of preliminary feedback plus up to 10 weeks of functional review for new submissions (6 weeks for resubmissions). The app must be installed on 10 or more active workspaces before submitting or it 'will be blocked from submitting'; prepare the video demo, privacy policy, public support page, and per-scope justifications first.
  - Escalation: Feedback arrives in the submission flow and via email; address all feedback and resubmit. Note that resubmitting during preliminary review resets your queue position.
- **OAuth endpoint rate limits are only partially documented** — oauth.v2.access documents a rate limit of 600 requests per minute (tier t5, 'Special rate limits apply'); no published limit exists for the oauth/v2/authorize endpoint. Implement exponential backoff and respect Retry-After headers; monitor for 429 responses.
  - Escalation: File a support ticket if consistent rate limiting blocks legitimate traffic.

## What the agent can do vs. you

**An agent can:** Research Slack OAuth docs and scope lists; Draft App Manifest YAML/JSON; Prepare scope justification and privacy policy templates; Generate authorization URL with correct parameters; Implement token exchange and storage logic; Configure Composio auth config with credentials.
**You must:** Sign in to Slack and access developer console; Create the app and select development workspace; Enter redirect URLs and scopes in the console UI; Click 'Install to Workspace' and authorize; Accept Slack API Terms of Service; Submit to Marketplace and provide legal URLs; Store client_secret and signing_secret securely.

## Connect it via Composio

Register this redirect URI in the provider console: `https://backend.composio.dev/api/v3/toolkits/auth/callback`
Then create the auth config with: client_id, client_secret, redirect_uri, scopes, user_scopes, auth_url, token_url.

```python
from composio import Composio

composio = Composio()
auth_config = composio.auth_configs.create(
    name="slack-oauth",
    auth_scheme="OAUTH2",
    credentials={
        "client_id": "{{CLIENT_ID}}",
        "client_secret": "{{CLIENT_SECRET}}",
        "redirect_uri": "https://backend.composio.dev/api/v3/toolkits/auth/callback",
        "scopes": ["chat:write", "commands"],
        "user_scopes": ["channels:history"],
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access"
    },
    options={"type": "use_custom_auth"}
)
```

Use the created auth_config ID when setting up Slack toolkit connections via Composio MCP.

## Evidence

- [Installing with OAuth (redirects from api.slack.com/authentication/oauth-v2)](https://docs.slack.dev/authentication/installing-with-oauth) — OAuth V2 endpoints, redirect_uri match/subdirectory rules, HTTPS requirement, no fragments, first-URL fallback, same redirect_uri in Authorize+Access, 10-minute code expiry, xoxb/xoxp tokens, state validation, SIWS scope conflict, optional scopes, scope downgrade prohibition, org-level installs needing Org Owner/Admin
- [App lifecycle & distribution](https://docs.slack.dev/app-management/distribution) — Three distribution options (single workspace, unlisted public distribution, Slack Marketplace); unlisted distribution via 'Activate Public Distribution' needs NO review; Marketplace listing is reviewed; distribution checklist (OAuth flow, SSL URLs)
- [Slack Marketplace review process](https://docs.slack.dev/slack-marketplace/slack-marketplace-review-guide) — Submission from 'Submit to the Slack Marketplace' section; 10+ active workspaces prerequisite; preliminary review up to 10 business days; functional review up to 10 weeks (new) / 6 weeks (resubmit); video demo; publish-after-approval; live app locked; return-and-resubmit process
- [Submission guidelines and requirements](https://docs.slack.dev/slack-marketplace/slack-marketplace-app-guidelines-and-requirements) — Privacy policy, public support page (2-business-day response), scope justifications, 10 active workspaces / 20 MAU suitability threshold, ToS agreements for Marketplace distribution, no formal appeal described, resubmission after substantial changes
- [Updated installation requirement for Slack Marketplace apps](https://docs.slack.dev/changelog/2026/09/01/slack-marketplace-install-requirement) — As of July 2026 apps need at least 10 installations on active workspaces, maintained throughout the entire review
- [Creating an app from app settings](https://docs.slack.dev/app-management/quickstart-app-settings) — Console creation flow: api.slack.com/apps?new_app=1, 'Blank app' → Continue, App Name, workspace selection, Create
- [Creating an app with Bolt for Python](https://docs.slack.dev/tools/bolt-python/creating-an-app) — Scopes added under OAuth & Permissions before install; 'Install App to Workspace' button; Bot User OAuth Access Token display after install; Basic Information holds app credentials; sandbox workspace advice
- [App manifest reference](https://docs.slack.dev/reference/app-manifest) — oauth_config.token_management_enabled, settings.token_rotation_enabled, oauth_config.scopes.bot/user/bot_optional/user_optional, oauth_config.redirect_urls, YAML/JSON formats
- [Configuring apps with app manifests (redirects from api.slack.com/reference/manifests)](https://docs.slack.dev/app-manifests/configuring-apps-with-app-manifests) — YAML/JSON manifests, creating apps from a manifest, scope additions only take effect for existing installs after workspaces reinstall
- [Using token rotation (redirects from api.slack.com/authentication/rotation)](https://docs.slack.dev/authentication/using-token-rotation) — Rotation optional but irreversible; settings.token_rotation_enabled: true; OAuth & Permissions toggle; expires_in 43200 (12 hours); xoxe. prefix; single-use refresh tokens with grace period; 2-active-token limit; oauth.v2.exchange and grant_type=refresh_token
- [Tokens (redirects from api.slack.com/authentication/token-types)](https://docs.slack.dev/authentication/tokens) — Bot tokens begin with xoxb-, user tokens with xoxp-, app-level tokens with xapp-
- [Scopes reference (redirects from api.slack.com/scopes)](https://docs.slack.dev/reference/scopes) — chat:write, commands, channels:history, openid, email, profile definitions
- [Best practices for security (redirects from api.slack.com/authentication/best-practices)](https://docs.slack.dev/authentication/best-practices-for-security) — Never hardcode credentials; secrets managers in production; do not distribute client secrets; limit redirect URIs to domains in your control
- [oauth.v2.access method reference](https://docs.slack.dev/reference/methods/oauth.v2.access) — 600-per-minute rate limit (t5) for oauth.v2.access; redirect_uri required only if sent in the authorize step; Basic auth recommendation for client_id/client_secret; xoxb/xoxp and xoxe. rotated token examples
- [Developing apps for Enterprise orgs](https://docs.slack.dev/enterprise/developing-for-enterprise-orgs) — Org-wide installs require Org Admin approval (Slack DM review); admin installs to org then selects workspaces; org_deploy_enabled: true; org install does not auto-add to workspaces
- [Slack developer FAQ](https://docs.slack.dev/faq) — Client secret reset via 'Change secret' button (no statement that the secret is shown only once)
- [Node Slack SDK OAuth guide](https://docs.slack.dev/tools/node-slack-sdk/oauth/) — State verification strongly recommended (CSRF mitigation); InstallationStore/StateStore — and confirms the page does NOT contain a manifest example or token_management_enabled (draft mis-citation)
- [Slack Developer Console (Your Apps)](https://api.slack.com/apps) — Sign-in required to create an application; console entry point

**Could not verify:**
- Rate limit for the oauth/v2/authorize endpoint (oauth.v2.access documents 600 requests/minute; the authorize endpoint has no published limit)
- Classic Slack app (V1 OAuth) deprecation schedule
- Whether the Client Secret is shown only once at creation (not documented; Basic Information lists the credentials and 'Change secret' resets them)
- Composio claim that Slack is not in the Composio catalog / has no managed OAuth (outside official Slack documentation; verify against Composio directly)

*Last checked: 2026-11-03 · Status: `stable` · Generated by agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b · Verified by human:verification-pass*