---
type: oauth_guide
okf_version: '0.2'
resource: shopify
title: Shopify OAuth App Setup Guide
tags:
- app-store
- ecommerce
- oauth
- partner-dashboard
- shopify
status: stable
stale_after: '2027-05-03'
generated:
  by: agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b
  at: '2026-11-03T17:49:00.584448Z'
verified:
  by: human:verification-pass
  at: '2026-11-03T19:10:13.148394Z'
chatbot:
  visible: true
  priority: primary
badge: library
last_checked: '2026-11-04'
unverified:
- PKCE support for the authorization code grant - not documented in official OAuth pages (community threads
  mention it; no official statement found)
- App Store review timeline - no SLA in official docs (review-process page states no duration); the 5-10
  business days figure is community-reported and variable
- REST Admin API rate limit numbers - not checked in this pass; only GraphQL cost-based limits previously
  confirmed
- Python library name - only Node.js (@shopify/shopify-api) and Ruby (shopify-api-ruby) libraries confirmed
  in docs
- Whether Partner account signup is free - requirement of a Partner account is verified, but signup pricing
  was not on fetched pages
sources:
- url: https://shopify.dev/docs/apps/build/authentication-authorization
  title: Shopify Authentication and Authorization Overview
  what_it_supports: Grant types (authorization code, token exchange, client credentials), online vs offline
    token lifetimes, X-Shopify-Access-Token header, custom apps automatic protected-data access with plan
    variance for admin-created apps, client assertion for public-distribution client credentials
- url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  title: Authorization Code Grant
  what_it_supports: Exact authorization URL parameters (no expiring param), grant_options[]=per-user,
    HMAC/state/shop-domain validation with regex, token exchange with expiring='1', response fields (expires_in
    3600, refresh_token_expires_in 90 days), refresh-token rotation and 401 terminal semantics, write-scope-includes-read
- url: https://shopify.dev/docs/apps/build/authentication-authorization/authenticate-standalone-apps
  title: Authenticate a standalone or API-only app
  what_it_supports: redirect_uri must exactly match a URI configured in the Dev Dashboard or shopify.app.toml
    [auth] section
- url: https://shopify.dev/docs/apps/launch/distribution
  title: About app distribution
  what_it_supports: Public vs custom distribution (custom is current, not legacy), no review for custom,
    custom can't use Shopify billing, distribution can't be changed after selection, App Store registration
    one-time fee, in-admin custom apps deprecated
- url: https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
  title: App Store requirements
  what_it_supports: OAuth immediately on install, TLS certificate requirement, expiring offline tokens
    mandatory for public apps (3.1.2), Billing API required only for apps with charges, new public apps
    GraphQL-only since April 1 2025, listing/testing requirements
- url: https://shopify.dev/docs/apps/launch/app-store-review/review-process
  title: About the app review process
  what_it_supports: Review statuses Draft/Submitted/Reviewed/Published (plus Paused), no stated review
    duration or SLA, resubmission flow
- url: https://shopify.dev/docs/apps/build/compliance/privacy-law-compliance
  title: Privacy law compliance (mandatory compliance webhooks)
  what_it_supports: Mandatory customers/data_request, customers/redact, shop/redact webhooks for App Store
    apps, TOML registration, 200-series response, 401 on invalid HMAC, 30-day action window, rejection
    for missing webhooks
- url: https://shopify.dev/docs/api/usage/access-scopes
  title: Access scopes
  what_it_supports: Scope names (read_products, write_orders, read_customers), write scope grants matching
    read scope, scopes declared in [access_scopes], some scopes need Shopify approval before declaring,
    protected customer data review is separate from scope approval
- url: https://shopify.dev/docs/apps/launch/protected-customer-data
  title: Protected customer data access
  what_it_supports: Request via Partner Dashboard → API access requests before submission, Level 1/Level
    2 tiers, custom apps always available / admin-created varies by plan, dev stores exempt, unapproved
    responses are 200 with redacted fields and GraphQL errors (not 403)
- url: https://shopify.dev/docs/apps/build/stores/development-stores
  title: Development stores
  what_it_supports: Dev stores are free testing environments, 250-per-organization cap, no production
    conversion, no client transfer, test transactions only
- url: https://shopify.dev/docs/apps/build/cli-for-apps
  title: Shopify CLI for apps
  what_it_supports: shopify app init scaffolding, CLI 3.59+ bundles @shopify/app, deploy command, dev
    store preview
- url: https://shopify.dev/docs/apps/build/cli-for-apps/networking-options
  title: Select a networking option for local development
  what_it_supports: Cloudflare Quick Tunnels by default, ngrok via --tunnel-url, --use-localhost with
    self-signed HTTPS (mkcert), localhost mode limits (no webhooks/app proxy/Flow)
- url: https://shopify.dev/docs/apps/getting-started
  title: Getting started with Shopify apps
  what_it_supports: Dev Dashboard manages credentials/scopes/dev stores/logs; Shopify CLI and Dev Dashboard
    work against the same app record; distribution determines who can install (public needs review, custom
    needs none)
- url: https://shopify.dev/docs/api/shop/guides/creating-a-client
  title: Creating a client (Shop app / Dev Dashboard)
  what_it_supports: Partner account requirement, Dev Dashboard create app (name/description), Versions
    → Release with scopes and redirect URLs, fully-qualified https-only redirect URLs, Client ID/Secret
    on Settings page, shop_app:oauth must not be sent in the scope parameter (invalid_scope)
- url: https://shopify.dev/changelog/posts/update-to-shopifys-app-developer-revenue-share
  title: Update to Shopify's app developer revenue share (changelog, Apr 2025)
  what_it_supports: Revenue exemption on first $1M USD of LIFETIME revenue with 15% share above that;
    annual reset sunset (corrects the draft's 20%/15% after $1M-per-year claim)
- url: https://community.shopify.dev/t/longer-app-store-review-times-what-you-need-to-know/31728
  title: Longer App Store review times - what you need to know (Shopify community)
  what_it_supports: Community-reported evidence that App Store review times vary and can run long; basis
    for the 'reported' (not verified) review-wait estimate
guide:
  summary: Register a Shopify OAuth app via the Partner Dashboard Dev Dashboard, configure scopes and
    redirect URIs per version, implement the authorization code grant flow with mandatory HMAC and state
    validation, and optionally submit for App Store review if distributing publicly. Offline access tokens
    expire in 1 hour with 90-day refresh tokens; new public apps must use expiring=1.
  app_website: https://shopify.com
  developer_console: https://partners.shopify.com (Partner Dashboard) / https://shopify.dev/apps/dev-dashboard
    (Dev Dashboard)
  oauth_docs: https://shopify.dev/docs/apps/build/authentication-authorization
  source_url: ''
  difficulty:
    level: 2
    tier: Light
    verdict: Standard OAuth 2.0 authorization code grant with Shopify-specific requirements (HMAC validation,
      state, expiring tokens). Library support reduces implementation effort.
    evidence: reported
    source_url: ''
  time:
    hands_on: 30-60 minutes (add 10-15 minutes if scaffolding with Shopify CLI)
    approval_wait: None for custom distribution apps; App Store review has no officially documented SLA
      - community-reported around 5-10 business days but variable
    verdict: Quick console setup; public distribution adds review queue time.
    evidence: reported
    source_url: https://community.shopify.dev/t/longer-app-store-review-times-what-you-need-to-know/31728
  prerequisites:
  - item: Shopify Partner account
    detail: Register at partners.shopify.com; the Dev Dashboard requires signing in with a Partner account.
    blocking: true
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/api/shop/guides/creating-a-client
  - item: Development store
    detail: Free testing environments you own and control; organizations are limited to 250 dev stores,
      which cannot be converted to production stores or transferred to clients.
    blocking: true
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/stores/development-stores
  - item: HTTPS redirect URI endpoint
    detail: Redirect URIs must be fully-qualified HTTPS URLs that exactly match a URI configured in the
      Dev Dashboard or the [auth] section of shopify.app.toml. For local development, shopify app dev
      opens a Cloudflare Quick Tunnel by default; ngrok (--tunnel-url) or --use-localhost (self-signed
      HTTPS cert via mkcert) are alternatives.
    blocking: true
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/authenticate-standalone-apps
  steps:
  - n: 1
    title: Create Partner account and open Dev Dashboard
    where: https://partners.shopify.com → Dev Dashboard (https://dev.shopify.com)
    action: Sign up for a Partner account, then sign in to the Dev Dashboard to manage apps.
    duration: 5 minutes
    agent_automatable: false
    human_because: Requires human login, email verification, and acceptance of Partner terms.
    nuances: Partner account is distinct from a merchant store account. The Dev Dashboard manages the
      app's credentials, scopes, dev stores, and logs.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/api/shop/guides/creating-a-client
  - n: 2
    title: Create a new app and pick the distribution method
    where: Dev Dashboard → Create app
    action: 'Enter app name and description. Choose distribution: Public (App Store - any merchant can
      install after passing review) or Custom (a single store, a Plus organization''s stores, or dev stores
      - no listing and no review, but can''t charge merchants through Shopify billing).'
    duration: 5 minutes
    agent_automatable: false
    human_because: Requires clicking through console UI and naming decisions.
    nuances: You can't change the distribution method after you select it - decide on the production app.
      Custom distribution is current, not legacy; what is retired is in-admin custom apps with pre-generated
      tokens ('no longer available for new apps'). Shopify CLI and the Dev Dashboard both work against
      the same app record, so you can create the app in either one.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/distribution
  - n: 3
    title: Scaffold and run the app locally with Shopify CLI (optional, recommended)
    where: Your local terminal (shopify app init; npm init @shopify/app @latest also works)
    action: Run shopify app init to scaffold a complete app project (CLI 3.59+ bundles @shopify/app, so
      no separate package install is needed). Set scopes in the [access_scopes] section and redirect URLs
      in the [auth] section of shopify.app.toml. Run shopify app dev to build, open a tunnel, and preview
      against a dev store.
    duration: 10-15 minutes
    agent_automatable: true
    human_because: Commands and file edits are automatable; a human must log in and approve the browser/device
      auth that links the CLI to the Dev Dashboard.
    nuances: Apps built with Shopify CLI use managed installation by default, which is why they don't
      implement the authorization code grant by hand. shopify app dev uses a Cloudflare Quick Tunnel by
      default; ngrok via --tunnel-url or --use-localhost (localhost with a self-signed HTTPS certificate
      via mkcert) are alternatives. Localhost mode isn't compatible with features that directly invoke
      your app, such as webhooks, app proxy, and Flow actions.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/cli-for-apps
  - n: 4
    title: Release a version with scopes and redirect URLs
    where: Dev Dashboard → Versions → Release
    action: Click Versions → Release. Under Access → Select scopes, choose the Admin API scopes your app
      needs (e.g., read_products, write_orders). In the Redirect URLs section, add every fully-qualified
      HTTPS callback endpoint. Click Release. CLI apps instead run shopify app deploy to push the TOML
      config as a new version.
    duration: 10 minutes
    agent_automatable: true
    human_because: Console form-filling (or deploy confirmation) and scope choices require a logged-in
      human.
    nuances: 'Versions configure both the scopes and the redirect URLs for your app. Any write scope also
      grants its matching read scope. Some scopes require Shopify approval before you can declare them
      (declaring early raises an app_access validation error on scopes). shop_app:oauth is a Shop-app
      channel scope: never include it in the authorization request''s scope parameter or authorization
      fails with invalid_scope. Redirect URLs must be fully-qualified HTTPS.'
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/api/shop/guides/creating-a-client
  - n: 5
    title: Retrieve Client ID and Client Secret
    where: Dev Dashboard → App → Settings
    action: After releasing a version, copy the Client ID (public) and Client Secret from the app's Settings
      page (server-side only, store securely).
    duration: 2 minutes
    agent_automatable: false
    human_because: Credentials are displayed only in the authenticated console.
    nuances: Store your client secret securely; it must never be exposed client-side.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/api/shop/guides/creating-a-client
  - n: 6
    title: Implement authorization code grant flow
    where: Your application code (backend)
    action: 'Build the authorization URL: GET https://{shop}/admin/oauth/authorize?client_id={CLIENT_ID}&scope=read_products,write_orders&redirect_uri={REDIRECT_URI}&state={RANDOM_NONCE}
      (append &grant_options[]=per-user for an online token tied to a staff session). Redirect the merchant.
      On callback: validate state against the stored nonce (constant-time), verify the HMAC-SHA256 of
      all query params except hmac using the client secret (constant-time), and validate the shop domain
      against ^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$. Exchange the code: POST https://{shop}/admin/oauth/access_token
      with form fields client_id, client_secret, code, expiring=''1'' (new public apps must use expiring
      offline access tokens). Store access_token, scope, expires_in (example: 3600s), refresh_token, refresh_token_expires_in
      (90 days). Send X-Shopify-Access-Token on Admin API calls. Refresh via POST .../admin/oauth/access_token
      with grant_type=refresh_token.'
    duration: 30-60 minutes
    agent_automatable: true
    human_because: Code implementation can be automated; human needed for architecture decisions and testing.
    nuances: 'expiring=1 belongs in the token exchange request body only - the authorization URL takes
      client_id, scope, redirect_uri, state (plus optional grant_options[]). Merchants can modify requested
      scopes during authorization, so verify granted scopes before storing. Refresh rotates: each grant
      returns a NEW refresh token - store both and refresh from the new pair so Shopify retires the old
      one; a 401 means the pair is terminal (clear it and re-authorize), while ambiguous failures (timeout/5xx/429)
      should be retried with the token you still hold (it stays usable until you use the replacement;
      don''t rely on a fixed retry-window duration). Use @shopify/shopify-api (Node) or shopify-api-ruby
      to handle HMAC/state automatically. CLI-built apps use managed installation instead of this flow.
      PKCE support unverified.'
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  - n: 7
    title: Test on development store
    where: Development store admin → Apps → Install your app
    action: Install the app on a development store to verify OAuth flow, token exchange, and API calls
      work end-to-end.
    duration: 10 minutes
    agent_automatable: false
    human_because: Requires human interaction in Shopify admin to approve installation.
    nuances: Dev stores are free testing environments you own and control, but organizations are limited
      to 250 dev stores. They can't process real transactions, can't be converted to production stores,
      and can't be transferred to clients (use client transfer stores for hand-offs).
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/stores/development-stores
  - n: 8
    title: Request protected customer data access (if needed)
    where: Partner Dashboard → API access requests → Protected customer data access
    action: 'Select your distribution method first, then request access before App Store submission: select
      Protected customer data, provide reasons for each field you need (name, address, phone, email),
      and save. Level 1 (customer data excluding name/address/phone/email) and Level 2 (including those
      fields) require review for public apps; both levels are always available to custom-distribution
      apps.'
    duration: Varies
    agent_automatable: false
    human_because: Requires legal justification and Shopify review team interaction.
    nuances: 'Apps installed only on development stores are exempt - no request needed for testing. Admin-created
      custom apps vary by plan for Level 2. Without approval the API does not return 403: GraphQL requests
      return HTTP 200 with errors for unapproved objects, and unapproved fields are redacted/null - your
      app must handle that.'
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/protected-customer-data
  - n: 9
    title: Submit for App Store review (public distribution only)
    where: Dashboard → App → App Store submission
    action: 'Before submitting: subscribe to the mandatory compliance webhooks (customers/data_request,
      customers/redact, shop/redact) in shopify.app.toml and verify the endpoints respond 200 (401 on
      invalid HMAC). Complete the listing (description, screenshots, screencast, pricing, privacy policy,
      test credentials), register for the Shopify App Store (one-time fee), and ensure OAuth uses expiring
      offline tokens. Review moves the app through Draft → Submitted → Reviewed → Published (Paused if
      core requirements block review).'
    duration: 'Preparation: 1-2 hours; Review wait: no official SLA - community-reported 5-10 …'
    agent_automatable: false
    human_because: Legal acceptance, listing content, and review communication require human.
    nuances: 'Public apps must authenticate with OAuth immediately on install, must use expiring offline
      access tokens (non-expiring tokens aren''t permitted), and new public apps must be built exclusively
      with the GraphQL Admin API (since April 1, 2025). Revenue share: exemption on the first $1M USD
      of lifetime revenue and 15% on amounts above that (the annual reset was sunset in 2025). Built for
      Shopify is the badge for apps clearing the highest quality bars.'
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
  gotchas:
  - title: HMAC validation must use constant-time comparison
    why_it_matters: Prevents timing attacks that could leak the client secret. Shopify includes hmac parameter
      on every callback.
    how_to_handle: Use crypto.timingSafeEqual (Node) or hmac.compare_digest (Python). Remove the hmac
      parameter, sort the remaining parameters alphabetically, and compute HMAC-SHA256 of the message
      using the client secret as key.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  - title: State parameter required for CSRF protection
    why_it_matters: Without state validation, attackers can hijack OAuth flows. Shopify echoes the state
      value back on callback.
    how_to_handle: Generate cryptographically random nonce per auth request, store server-side, validate
      on callback with constant-time comparison; reject mismatches with 403.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  - title: expiring=1 goes in the token exchange, not the authorization URL
    why_it_matters: New public apps must use expiring offline access tokens; non-expiring tokens aren't
      permitted for public apps. But the authorization URL only accepts client_id, scope, redirect_uri,
      state (plus grant_options[]=per-user for online tokens) - putting expiring=1 there does nothing.
    how_to_handle: Include expiring:'1' as a form field in the POST to /admin/oauth/access_token. Store
      the refresh token (90-day lifetime) and refresh before expiry; each refresh returns a NEW refresh
      token, so persist the new pair.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  - title: Mandatory compliance webhooks for App Store apps
    why_it_matters: Any app distributed through the Shopify App Store must respond to data subject requests
      regardless of whether it collects personal data. Missing or broken compliance webhooks cause rejection
      before publishing.
    how_to_handle: Subscribe to customers/data_request, customers/redact, and shop/redact via [[webhooks.subscriptions]]
      with compliance_topics in shopify.app.toml (they cannot be created via the webhook API). Endpoints
      must accept POST with JSON bodies, respond with a 200-series status, return 401 Unauthorized on
      invalid HMAC, and complete the action within 30 days.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/compliance/privacy-law-compliance
  - title: Protected customer data needs separate approval - errors are redacted fields, not 403
    why_it_matters: Merchant consent alone is insufficient for customer PII on public apps. Level 1/Level
      2 access is reviewed via Partner Dashboard → API access requests before submission; approval is
      minimum-necessary.
    how_to_handle: Request access before App Store submission with per-field justification. Without approval,
      requests return HTTP 200 with unapproved fields redacted/null and GraphQL errors for unapproved
      objects - handle those paths in code. Custom-distribution apps get Level 1 and 2 automatically;
      admin-created custom apps vary by plan for Level 2.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/protected-customer-data
  - title: Redirect URIs must be fully-qualified HTTPS and match exactly
    why_it_matters: The redirect_uri must exactly match a redirect URI configured in the Dev Dashboard
      or the app's config TOML; any mismatch fails authorization. Only fully-qualified https URLs are
      supported.
    how_to_handle: 'Register all callback URLs (in the version release for console apps, or [auth] in
      shopify.app.toml for CLI apps) before authorizing. For local development use shopify app dev: Cloudflare
      Quick Tunnel by default, ngrok via --tunnel-url, or --use-localhost (self-signed HTTPS cert via
      mkcert; localhost mode can''t receive webhooks or app proxies).'
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/authenticate-standalone-apps
  - title: Shop domain validation regex must be anchored
    why_it_matters: Prevents open redirect and spoofing attacks. Shopify sends shop parameter on callback.
    how_to_handle: Validate against ^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$ (anchored at both ends).
      Without the trailing $, a value such as exampleshop.myshopify.com.attacker.example passes the check.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant
  blockers:
  - issue: Public App Store review queue
    how_to_resolve: 'Fix all issues flagged on the review page before submitting: OAuth immediately on
      install, expiring offline tokens, GraphQL Admin API only (new public apps), mandatory compliance
      webhooks responding correctly, complete listing with screencast and test credentials, valid TLS
      certificate, privacy policy. Submissions move Draft → Submitted → Reviewed → Published, with Paused
      used when core requirements block review; there is no officially documented review SLA.'
    escalation: Contact Shopify Partner Support via the dashboard if review stalls; withdraw and resubmit
      fixes from the status banner.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/app-store-review/review-process
  - issue: Protected customer data approval denied
    how_to_resolve: 'Approval is minimum-necessary: reduce requested fields (Level 1 vs Level 2), provide
      clear privacy handling documentation, and resubmit. Until approved, handle redacted fields and GraphQL
      errors in the app.'
    escalation: Reply to the reviewer via the dashboard review flow.
    evidence: verified_from_docs
    source_url: https://shopify.dev/docs/apps/launch/protected-customer-data
  - issue: Client secret compromised
    how_to_resolve: Immediately rotate the secret in Dev Dashboard Settings, update all server-side configurations,
      and audit access logs for unauthorized API calls.
    escalation: Report to Shopify Partner Support if misuse is detected.
    evidence: unknown
    source_url: ''
  agent_vs_human:
    agent_can:
    - Research scopes and OAuth parameters from official docs
    - Scaffold, configure, and run the app locally with Shopify CLI (shopify app init / shopify app dev
      / shopify app deploy)
    - Draft shopify.app.toml with [access_scopes], [auth] redirect URLs, and compliance webhook subscriptions
    - Generate authorization URL construction code
    - Implement HMAC/state/shop-domain validation logic using library helpers
    - Prepare App Store listing content drafts
    human_must:
    - Create and log into Shopify Partner account
    - Click through the Dev Dashboard to create the app, release versions, and retrieve Client ID/Secret
    - Accept Partner Program Agreement and App Store terms; complete App Store registration (one-time
      fee)
    - Provide legal/business info and listing content for the App Store
    - Approve installation on the development store
    - Communicate with the Shopify review team
  composio_next:
    managed: false
    managed_note: Shopify is not present in the Composio catalog. No managed auth config exists.
    redirect_uri_to_register: https://backend.composio.dev/api/v3/toolkits/auth/callback
    auth_config_fields:
    - client_id
    - client_secret
    - auth_url
    - token_url
    - scopes
    - redirect_uri
    auth_config_snippet: "from composio import Composio\n\ncomposio = Composio()\nauth_config = composio.auth_configs.create(\n\
      \    name=\"shopify-oauth\",\n    options={\n        \"type\": \"use_custom_auth\",\n        \"\
      auth_scheme\": \"OAUTH2\",\n        \"credentials\": {\n            \"client_id\": \"{{CLIENT_ID}}\"\
      ,\n            \"client_secret\": \"{{CLIENT_SECRET}}\",\n            \"auth_url\": \"https://{shop}.myshopify.com/admin/oauth/authorize\"\
      ,\n            \"token_url\": \"https://{shop}.myshopify.com/admin/oauth/access_token\",\n     \
      \       \"scopes\": [\"read_products\", \"write_orders\"],\n            \"redirect_uri\": \"https://backend.composio.dev/api/v3/toolkits/auth/callback\"\
      \n        }\n    }\n)"
    mcp_note: MCP server would need dynamic shop domain substitution in auth_url/token_url. Composio custom
      auth config can template {shop} at runtime if supported.
---

# Shopify OAuth App Setup Guide

Register a Shopify OAuth app via the Partner Dashboard Dev Dashboard, configure scopes and redirect URIs per version, implement the authorization code grant flow with mandatory HMAC and state validation, and optionally submit for App Store review if distributing publicly. Offline access tokens expire in 1 hour with 90-day refresh tokens; new public apps must use expiring=1.

## Difficulty & time

Standard OAuth 2.0 authorization code grant with Shopify-specific requirements (HMAC validation, state, expiring tokens). Library support reduces implementation effort.

- **Difficulty:** Light (2/5)
- **Hands-on setup:** 30-60 minutes (add 10-15 minutes if scaffolding with Shopify CLI)
- **Approval wait:** None for custom distribution apps; App Store review has no officially documented SLA - community-reported around 5-10 business days but variable

## Prerequisites

- **Required:** Shopify Partner account — Register at partners.shopify.com; the Dev Dashboard requires signing in with a Partner account.
- **Required:** Development store — Free testing environments you own and control; organizations are limited to 250 dev stores, which cannot be converted to production stores or transferred to clients.
- **Required:** HTTPS redirect URI endpoint — Redirect URIs must be fully-qualified HTTPS URLs that exactly match a URI configured in the Dev Dashboard or the [auth] section of shopify.app.toml. For local development, shopify app dev opens a Cloudflare Quick Tunnel by default; ngrok (--tunnel-url) or --use-localhost (self-signed HTTPS cert via mkcert) are alternatives.

## Step-by-step

### 1. Create Partner account and open Dev Dashboard (https://partners.shopify.com → Dev Dashboard (https://dev.shopify.com))
Sign up for a Partner account, then sign in to the Dev Dashboard to manage apps.
*[~5 minutes, human step; evidence: verified_from_docs]*
> Partner account is distinct from a merchant store account. The Dev Dashboard manages the app's credentials, scopes, dev stores, and logs.

### 2. Create a new app and pick the distribution method (Dev Dashboard → Create app)
Enter app name and description. Choose distribution: Public (App Store - any merchant can install after passing review) or Custom (a single store, a Plus organization's stores, or dev stores - no listing and no review, but can't charge merchants through Shopify billing).
*[~5 minutes, human step; evidence: verified_from_docs]*
> You can't change the distribution method after you select it - decide on the production app. Custom distribution is current, not legacy; what is retired is in-admin custom apps with pre-generated tokens ('no longer available for new apps'). Shopify CLI and the Dev Dashboard both work against the same app record, so you can create the app in either one.

### 3. Scaffold and run the app locally with Shopify CLI (optional, recommended) (Your local terminal (shopify app init; npm init @shopify/app @latest also works))
Run shopify app init to scaffold a complete app project (CLI 3.59+ bundles @shopify/app, so no separate package install is needed). Set scopes in the [access_scopes] section and redirect URLs in the [auth] section of shopify.app.toml. Run shopify app dev to build, open a tunnel, and preview against a dev store.
*[~10-15 minutes, agent-automatable; evidence: verified_from_docs]*
> Apps built with Shopify CLI use managed installation by default, which is why they don't implement the authorization code grant by hand. shopify app dev uses a Cloudflare Quick Tunnel by default; ngrok via --tunnel-url or --use-localhost (localhost with a self-signed HTTPS certificate via mkcert) are alternatives. Localhost mode isn't compatible with features that directly invoke your app, such as webhooks, app proxy, and Flow actions.

### 4. Release a version with scopes and redirect URLs (Dev Dashboard → Versions → Release)
Click Versions → Release. Under Access → Select scopes, choose the Admin API scopes your app needs (e.g., read_products, write_orders). In the Redirect URLs section, add every fully-qualified HTTPS callback endpoint. Click Release. CLI apps instead run shopify app deploy to push the TOML config as a new version.
*[~10 minutes, agent-automatable; evidence: verified_from_docs]*
> Versions configure both the scopes and the redirect URLs for your app. Any write scope also grants its matching read scope. Some scopes require Shopify approval before you can declare them (declaring early raises an app_access validation error on scopes). shop_app:oauth is a Shop-app channel scope: never include it in the authorization request's scope parameter or authorization fails with invalid_scope. Redirect URLs must be fully-qualified HTTPS.

### 5. Retrieve Client ID and Client Secret (Dev Dashboard → App → Settings)
After releasing a version, copy the Client ID (public) and Client Secret from the app's Settings page (server-side only, store securely).
*[~2 minutes, human step; evidence: verified_from_docs]*
> Store your client secret securely; it must never be exposed client-side.

### 6. Implement authorization code grant flow (Your application code (backend))
Build the authorization URL: GET https://{shop}/admin/oauth/authorize?client_id={CLIENT_ID}&scope=read_products,write_orders&redirect_uri={REDIRECT_URI}&state={RANDOM_NONCE} (append &grant_options[]=per-user for an online token tied to a staff session). Redirect the merchant. On callback: validate state against the stored nonce (constant-time), verify the HMAC-SHA256 of all query params except hmac using the client secret (constant-time), and validate the shop domain against ^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$. Exchange the code: POST https://{shop}/admin/oauth/access_token with form fields client_id, client_secret, code, expiring='1' (new public apps must use expiring offline access tokens). Store access_token, scope, expires_in (example: 3600s), refresh_token, refresh_token_expires_in (90 days). Send X-Shopify-Access-Token on Admin API calls. Refresh via POST .../admin/oauth/access_token with grant_type=refresh_token.
*[~30-60 minutes, agent-automatable; evidence: verified_from_docs]*
> expiring=1 belongs in the token exchange request body only - the authorization URL takes client_id, scope, redirect_uri, state (plus optional grant_options[]). Merchants can modify requested scopes during authorization, so verify granted scopes before storing. Refresh rotates: each grant returns a NEW refresh token - store both and refresh from the new pair so Shopify retires the old one; a 401 means the pair is terminal (clear it and re-authorize), while ambiguous failures (timeout/5xx/429) should be retried with the token you still hold (it stays usable until you use the replacement; don't rely on a fixed retry-window duration). Use @shopify/shopify-api (Node) or shopify-api-ruby to handle HMAC/state automatically. CLI-built apps use managed installation instead of this flow. PKCE support unverified.

### 7. Test on development store (Development store admin → Apps → Install your app)
Install the app on a development store to verify OAuth flow, token exchange, and API calls work end-to-end.
*[~10 minutes, human step; evidence: verified_from_docs]*
> Dev stores are free testing environments you own and control, but organizations are limited to 250 dev stores. They can't process real transactions, can't be converted to production stores, and can't be transferred to clients (use client transfer stores for hand-offs).

### 8. Request protected customer data access (if needed) (Partner Dashboard → API access requests → Protected customer data access)
Select your distribution method first, then request access before App Store submission: select Protected customer data, provide reasons for each field you need (name, address, phone, email), and save. Level 1 (customer data excluding name/address/phone/email) and Level 2 (including those fields) require review for public apps; both levels are always available to custom-distribution apps.
*[~Varies, human step; evidence: verified_from_docs]*
> Apps installed only on development stores are exempt - no request needed for testing. Admin-created custom apps vary by plan for Level 2. Without approval the API does not return 403: GraphQL requests return HTTP 200 with errors for unapproved objects, and unapproved fields are redacted/null - your app must handle that.

### 9. Submit for App Store review (public distribution only) (Dashboard → App → App Store submission)
Before submitting: subscribe to the mandatory compliance webhooks (customers/data_request, customers/redact, shop/redact) in shopify.app.toml and verify the endpoints respond 200 (401 on invalid HMAC). Complete the listing (description, screenshots, screencast, pricing, privacy policy, test credentials), register for the Shopify App Store (one-time fee), and ensure OAuth uses expiring offline tokens. Review moves the app through Draft → Submitted → Reviewed → Published (Paused if core requirements block review).
*[~Preparation: 1-2 hours; Review wait: no official SLA - community-reported 5-10 …, human step; evidence: verified_from_docs]*
> Public apps must authenticate with OAuth immediately on install, must use expiring offline access tokens (non-expiring tokens aren't permitted), and new public apps must be built exclusively with the GraphQL Admin API (since April 1, 2025). Revenue share: exemption on the first $1M USD of lifetime revenue and 15% on amounts above that (the annual reset was sunset in 2025). Built for Shopify is the badge for apps clearing the highest quality bars.

## Gotchas

- **HMAC validation must use constant-time comparison** — Prevents timing attacks that could leak the client secret. Shopify includes hmac parameter on every callback.
  - Handle: Use crypto.timingSafeEqual (Node) or hmac.compare_digest (Python). Remove the hmac parameter, sort the remaining parameters alphabetically, and compute HMAC-SHA256 of the message using the client secret as key.
- **State parameter required for CSRF protection** — Without state validation, attackers can hijack OAuth flows. Shopify echoes the state value back on callback.
  - Handle: Generate cryptographically random nonce per auth request, store server-side, validate on callback with constant-time comparison; reject mismatches with 403.
- **expiring=1 goes in the token exchange, not the authorization URL** — New public apps must use expiring offline access tokens; non-expiring tokens aren't permitted for public apps. But the authorization URL only accepts client_id, scope, redirect_uri, state (plus grant_options[]=per-user for online tokens) - putting expiring=1 there does nothing.
  - Handle: Include expiring:'1' as a form field in the POST to /admin/oauth/access_token. Store the refresh token (90-day lifetime) and refresh before expiry; each refresh returns a NEW refresh token, so persist the new pair.
- **Mandatory compliance webhooks for App Store apps** — Any app distributed through the Shopify App Store must respond to data subject requests regardless of whether it collects personal data. Missing or broken compliance webhooks cause rejection before publishing.
  - Handle: Subscribe to customers/data_request, customers/redact, and shop/redact via [[webhooks.subscriptions]] with compliance_topics in shopify.app.toml (they cannot be created via the webhook API). Endpoints must accept POST with JSON bodies, respond with a 200-series status, return 401 Unauthorized on invalid HMAC, and complete the action within 30 days.
- **Protected customer data needs separate approval - errors are redacted fields, not 403** — Merchant consent alone is insufficient for customer PII on public apps. Level 1/Level 2 access is reviewed via Partner Dashboard → API access requests before submission; approval is minimum-necessary.
  - Handle: Request access before App Store submission with per-field justification. Without approval, requests return HTTP 200 with unapproved fields redacted/null and GraphQL errors for unapproved objects - handle those paths in code. Custom-distribution apps get Level 1 and 2 automatically; admin-created custom apps vary by plan for Level 2.
- **Redirect URIs must be fully-qualified HTTPS and match exactly** — The redirect_uri must exactly match a redirect URI configured in the Dev Dashboard or the app's config TOML; any mismatch fails authorization. Only fully-qualified https URLs are supported.
  - Handle: Register all callback URLs (in the version release for console apps, or [auth] in shopify.app.toml for CLI apps) before authorizing. For local development use shopify app dev: Cloudflare Quick Tunnel by default, ngrok via --tunnel-url, or --use-localhost (self-signed HTTPS cert via mkcert; localhost mode can't receive webhooks or app proxies).
- **Shop domain validation regex must be anchored** — Prevents open redirect and spoofing attacks. Shopify sends shop parameter on callback.
  - Handle: Validate against ^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$ (anchored at both ends). Without the trailing $, a value such as exampleshop.myshopify.com.attacker.example passes the check.

## Common blockers

- **Public App Store review queue** — Fix all issues flagged on the review page before submitting: OAuth immediately on install, expiring offline tokens, GraphQL Admin API only (new public apps), mandatory compliance webhooks responding correctly, complete listing with screencast and test credentials, valid TLS certificate, privacy policy. Submissions move Draft → Submitted → Reviewed → Published, with Paused used when core requirements block review; there is no officially documented review SLA.
  - Escalation: Contact Shopify Partner Support via the dashboard if review stalls; withdraw and resubmit fixes from the status banner.
- **Protected customer data approval denied** — Approval is minimum-necessary: reduce requested fields (Level 1 vs Level 2), provide clear privacy handling documentation, and resubmit. Until approved, handle redacted fields and GraphQL errors in the app.
  - Escalation: Reply to the reviewer via the dashboard review flow.
- **Client secret compromised** — Immediately rotate the secret in Dev Dashboard Settings, update all server-side configurations, and audit access logs for unauthorized API calls.
  - Escalation: Report to Shopify Partner Support if misuse is detected.

## What the agent can do vs. you

**An agent can:** Research scopes and OAuth parameters from official docs; Scaffold, configure, and run the app locally with Shopify CLI (shopify app init / shopify app dev / shopify app deploy); Draft shopify.app.toml with [access_scopes], [auth] redirect URLs, and compliance webhook subscriptions; Generate authorization URL construction code; Implement HMAC/state/shop-domain validation logic using library helpers; Prepare App Store listing content drafts.
**You must:** Create and log into Shopify Partner account; Click through the Dev Dashboard to create the app, release versions, and retrieve Client ID/Secret; Accept Partner Program Agreement and App Store terms; complete App Store registration (one-time fee); Provide legal/business info and listing content for the App Store; Approve installation on the development store; Communicate with the Shopify review team.

## Connect it via Composio

Register this redirect URI in the provider console: `https://backend.composio.dev/api/v3/toolkits/auth/callback`
Then create the auth config with: client_id, client_secret, auth_url, token_url, scopes, redirect_uri.

```python
from composio import Composio

composio = Composio()
auth_config = composio.auth_configs.create(
    name="shopify-oauth",
    options={
        "type": "use_custom_auth",
        "auth_scheme": "OAUTH2",
        "credentials": {
            "client_id": "{{CLIENT_ID}}",
            "client_secret": "{{CLIENT_SECRET}}",
            "auth_url": "https://{shop}.myshopify.com/admin/oauth/authorize",
            "token_url": "https://{shop}.myshopify.com/admin/oauth/access_token",
            "scopes": ["read_products", "write_orders"],
            "redirect_uri": "https://backend.composio.dev/api/v3/toolkits/auth/callback"
        }
    }
)
```

MCP server would need dynamic shop domain substitution in auth_url/token_url. Composio custom auth config can template {shop} at runtime if supported.

## Evidence

- [Shopify Authentication and Authorization Overview](https://shopify.dev/docs/apps/build/authentication-authorization) — Grant types (authorization code, token exchange, client credentials), online vs offline token lifetimes, X-Shopify-Access-Token header, custom apps automatic protected-data access with plan variance for admin-created apps, client assertion for public-distribution client credentials
- [Authorization Code Grant](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/authorization-code-grant) — Exact authorization URL parameters (no expiring param), grant_options[]=per-user, HMAC/state/shop-domain validation with regex, token exchange with expiring='1', response fields (expires_in 3600, refresh_token_expires_in 90 days), refresh-token rotation and 401 terminal semantics, write-scope-includes-read
- [Authenticate a standalone or API-only app](https://shopify.dev/docs/apps/build/authentication-authorization/authenticate-standalone-apps) — redirect_uri must exactly match a URI configured in the Dev Dashboard or shopify.app.toml [auth] section
- [About app distribution](https://shopify.dev/docs/apps/launch/distribution) — Public vs custom distribution (custom is current, not legacy), no review for custom, custom can't use Shopify billing, distribution can't be changed after selection, App Store registration one-time fee, in-admin custom apps deprecated
- [App Store requirements](https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements) — OAuth immediately on install, TLS certificate requirement, expiring offline tokens mandatory for public apps (3.1.2), Billing API required only for apps with charges, new public apps GraphQL-only since April 1 2025, listing/testing requirements
- [About the app review process](https://shopify.dev/docs/apps/launch/app-store-review/review-process) — Review statuses Draft/Submitted/Reviewed/Published (plus Paused), no stated review duration or SLA, resubmission flow
- [Privacy law compliance (mandatory compliance webhooks)](https://shopify.dev/docs/apps/build/compliance/privacy-law-compliance) — Mandatory customers/data_request, customers/redact, shop/redact webhooks for App Store apps, TOML registration, 200-series response, 401 on invalid HMAC, 30-day action window, rejection for missing webhooks
- [Access scopes](https://shopify.dev/docs/api/usage/access-scopes) — Scope names (read_products, write_orders, read_customers), write scope grants matching read scope, scopes declared in [access_scopes], some scopes need Shopify approval before declaring, protected customer data review is separate from scope approval
- [Protected customer data access](https://shopify.dev/docs/apps/launch/protected-customer-data) — Request via Partner Dashboard → API access requests before submission, Level 1/Level 2 tiers, custom apps always available / admin-created varies by plan, dev stores exempt, unapproved responses are 200 with redacted fields and GraphQL errors (not 403)
- [Development stores](https://shopify.dev/docs/apps/build/stores/development-stores) — Dev stores are free testing environments, 250-per-organization cap, no production conversion, no client transfer, test transactions only
- [Shopify CLI for apps](https://shopify.dev/docs/apps/build/cli-for-apps) — shopify app init scaffolding, CLI 3.59+ bundles @shopify/app, deploy command, dev store preview
- [Select a networking option for local development](https://shopify.dev/docs/apps/build/cli-for-apps/networking-options) — Cloudflare Quick Tunnels by default, ngrok via --tunnel-url, --use-localhost with self-signed HTTPS (mkcert), localhost mode limits (no webhooks/app proxy/Flow)
- [Getting started with Shopify apps](https://shopify.dev/docs/apps/getting-started) — Dev Dashboard manages credentials/scopes/dev stores/logs; Shopify CLI and Dev Dashboard work against the same app record; distribution determines who can install (public needs review, custom needs none)
- [Creating a client (Shop app / Dev Dashboard)](https://shopify.dev/docs/api/shop/guides/creating-a-client) — Partner account requirement, Dev Dashboard create app (name/description), Versions → Release with scopes and redirect URLs, fully-qualified https-only redirect URLs, Client ID/Secret on Settings page, shop_app:oauth must not be sent in the scope parameter (invalid_scope)
- [Update to Shopify's app developer revenue share (changelog, Apr 2025)](https://shopify.dev/changelog/posts/update-to-shopifys-app-developer-revenue-share) — Revenue exemption on first $1M USD of LIFETIME revenue with 15% share above that; annual reset sunset (corrects the draft's 20%/15% after $1M-per-year claim)
- [Longer App Store review times - what you need to know (Shopify community)](https://community.shopify.dev/t/longer-app-store-review-times-what-you-need-to-know/31728) — Community-reported evidence that App Store review times vary and can run long; basis for the 'reported' (not verified) review-wait estimate

**Could not verify:**
- PKCE support for the authorization code grant - not documented in official OAuth pages (community threads mention it; no official statement found)
- App Store review timeline - no SLA in official docs (review-process page states no duration); the 5-10 business days figure is community-reported and variable
- REST Admin API rate limit numbers - not checked in this pass; only GraphQL cost-based limits previously confirmed
- Python library name - only Node.js (@shopify/shopify-api) and Ruby (shopify-api-ruby) libraries confirmed in docs
- Whether Partner account signup is free - requirement of a Partner account is verified, but signup pricing was not on fetched pages

*Last checked: 2026-11-04 · Status: `stable` · Generated by agent:crewai+nim:nvidia/nemotron-3-ultra-550b-a55b · Verified by human:verification-pass*