# Shopify OAuth Guide — Human Verification Report

Draft verified: `D:\Product_ops\knowledge\guides\drafts\shopify\v1.md`
Corrections applied: `D:\Product_ops\corrections\shopify.json`
Verification date: 2026-11-04 · Sources: official shopify.dev pages (plus one Shopify community thread, tagged `reported`)

## Confirmed

Claims from the draft that check out against official documentation:

- **HMAC callback validation** — remove `hmac`, sort remaining params, HMAC-SHA256 with the client secret, constant-time comparison (`crypto.timingSafeEqual` / `hmac.compare_digest`). [Authorization Code Grant]
- **State nonce requirement** — random nonce, stored server-side, compared on callback; CSRF protection; reject mismatches with 403. [Authorization Code Grant]
- **Shop domain regex** — `^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$`, anchored both ends; the docs use the same `attacker.example` bypass example for a missing `$`. [Authorization Code Grant]
- **Token exchange endpoint and body** — `POST https://{shop}/admin/oauth/access_token` with `client_id`, `client_secret`, `code`, `expiring='1'`; response carries `access_token`, `scope`, `expires_in` (example 3600s), `refresh_token`, `refresh_token_expires_in` (90 days). "New public apps must use expiring offline access tokens." [Authorization Code Grant; App Store requirements §3.1.2]
- **Refresh via `grant_type=refresh_token`** at the same access_token endpoint. [Authorization Code Grant]
- **Scopes** — `read_products` / `write_orders` are real Admin API scopes; "any scope that writes a resource also grants read access" (draft's "write scopes implicitly include read" is correct); scopes verified in the token response because merchants can modify requested scopes. [Access scopes; Authorization Code Grant]
- **Partner account required for the Dev Dashboard**; app name + description at creation; versions configure scopes and redirect URLs; credentials (Client ID/Secret) on the app Settings page after a release. [Creating a client]
- **Custom apps install without App Store review**; public distribution requires Shopify review. [About app distribution]
- **HTTPS redirect URIs, fully-qualified only**; tunneling for local dev exists (draft's core claim). [Creating a client; Networking options]
- **Protected customer data needs separate Shopify approval beyond merchant consent for public apps.** [Protected customer data; Auth overview]
- **Billing API is NOT an auth/setup requirement** — it is required only "if your app has any charges." The draft correctly does not imply otherwise. [App Store requirements §1.2]
- **App Store registration is required for public distribution** and review covers listing + app quality. [About app distribution; App Store requirements]
- **X-Shopify-Access-Token header** for Admin API calls; client credentials grant exists (client secret for own-org stores, client assertion for public-distribution apps) — this resolves a draft "unverified" item. [Auth overview]

## Corrected

1. **`expiring=1` was placed in the wrong request (step 6 / gotcha).** The draft put `&expiring=1` in the *authorization URL*. Per the Authorization Code Grant doc, the authorization URL takes only `client_id`, `scope`, `redirect_uri`, `state` (plus `grant_options[]=per-user` for online tokens); `expiring='1'` is a form field of the *token exchange* POST only. **Most important correction.**
2. **Mandatory compliance webhooks were missing entirely (new gotcha; step 9; blocker 1).** Any App Store app must subscribe to `customers/data_request`, `customers/redact`, `shop/redact` via `[[webhooks.subscriptions]]` compliance_topics in `shopify.app.toml` before publishing (not creatable via the webhook API); endpoints respond 200-series, return 401 on invalid HMAC, complete actions within 30 days; missing/broken webhooks cause rejection. [Privacy law compliance]
3. **"Custom (legacy, no longer creatable)" is wrong (step 2).** Custom distribution is a current, documented path (single store / Plus org / dev stores, no review, but can't charge via Shopify billing). What's retired is *in-admin* custom apps with pre-generated tokens. Also added: distribution can't be changed after selection. [About app distribution]
4. **"Unlimited free development stores" is wrong (prerequisite, step 7).** Dev stores are free testing environments but organizations are limited to 250; they can't be converted to production or transferred to clients (client transfer stores exist for that). [Development stores]
5. **Revenue share figures outdated (step 9 nuance).** Draft said "20% (15% after first $1M/year)". April 2025 changelog: exemption on the first $1M USD of *lifetime* revenue and 15% on amounts above that; annual reset sunset. [Changelog]
6. **Protected customer data details (step 8, gotcha).** Request is made in Partner Dashboard → API access requests *before* submission (Level 1 vs Level 2 tiers). Without approval the API does **not** return 403 — responses are HTTP 200 with unapproved fields redacted/null and GraphQL errors for unapproved objects. Custom-distribution apps get Level 1+2 automatically; only admin-created custom apps "vary by plan" (now verified, removing a draft unverified item); dev stores are exempt. [Protected customer data]
7. **Missing CLI flow (new step 3; agent_vs_human).** Added the documented Shopify CLI path (`shopify app init` / `shopify app dev` / `shopify app deploy`; `npm init @shopify/app @latest` also official) with its key consequence: CLI apps use *managed installation* by default and don't hand-roll the authorization code grant. Also covers default Cloudflare tunnel, ngrok `--tunnel-url`, and `--use-localhost` (self-signed HTTPS via mkcert) — refining the draft's "no localhost HTTP unless tunneled via ngrok". [CLI for apps; Networking options; Getting started]
8. **`shop_app:oauth` scope example misleading (step 4).** It is a Shop-app channel scope; sending it in the authorization request's `scope` parameter fails with `invalid_scope`. [Creating a client]
9. **Redirect URI matching (gotcha, prerequisite).** `redirect_uri` must *exactly match* a URI configured in the Dev Dashboard or `shopify.app.toml` `[auth]` (the draft only said "register all callback URLs"; exact-match is the operative rule — modern docs configure exact URIs, not domain wildcards). [Authenticate standalone apps]
10. **Refresh-token rotation nuance added (step 6).** Each refresh returns a NEW refresh token — store the new pair; 401 = terminal (clear and re-authorize); ambiguous failures retry with the held token (usable until the replacement is used; no fixed retry window). [Authorization Code Grant]
11. **Review process precision (step 9, blocker 1, time).** Official docs state no review SLA (statuses Draft → Submitted → Reviewed → Published, plus Paused). Kept "5-10 business days" explicitly tagged community-`reported` with source; added that new public apps must be GraphQL Admin API-only (April 1, 2025) and OAuth must occur immediately on install. [Review process; App Store requirements]
12. **Prerequisite wording tightened**: dropped unverified "free registration" phrasing (Partner account requirement itself is verified); expanded the HTTPS/redirect prerequisite with exact-match + tunnel details.

## Could not verify

- **PKCE support for the authorization code grant** — not documented in official OAuth pages; only community mentions. Kept in `unverified`.
- **App Store review timeline (5-10 business days)** — official docs state no duration; figure kept but tagged `reported` with the Shopify community thread as source.
- **REST Admin API rate limit numbers** — not checked in this pass (not load-bearing for OAuth setup).
- **Python library name** — only Node.js (`@shopify/shopify-api`) and Ruby (`shopify-api-ruby`) confirmed in docs.
- **Whether Partner signup is free** — the Partner account *requirement* is verified; signup pricing was not on fetched pages (dropped from prerequisite wording).
- **Composio catalog claims** (`managed: false`, catalog presence) — out of scope for Shopify docs verification; left unchanged.

**Source coverage:** 16 sources in `shopify.json` (15 official shopify.dev pages + 1 tagged Shopify community thread; 4 draft source URLs were kept where still accurate — note two of them, `getting-started` and `creating-a-client`, no longer support everything the draft attributed to them, so attribution was re-pointed; the draft's cited URL `.../launch/app-protected-redirect` and `/docs/apps/build/oauth` and `/docs/apps/build/cli` now return 404 and were replaced with their live equivalents).
