# Notion OAuth Guide — Human Verification Report

- Draft verified: `knowledge/guides/drafts/notion/v1.md`
- Corrections written: `corrections/notion.json`
- Date: 2026-11-03
- Method: every substantive claim checked against official Notion documentation only (developers.notion.com guides/reference, app.notion.com Developer portal, notion.com Help Center). WebSearch used only to locate official pages.

## Confirmed

These draft claims match official Notion documentation exactly:

1. **No review required to start OAuth.** "You can start authorization as soon as you configure the integration's client credentials and redirect URI; Marketplace submission or review is not required." (Authorization guide)
2. **Installation scope is immutable.** "Either **Any workspace** or **Selected workspaces only**. This can't be changed after creation." The draft's core gotcha is correct (wording updated from "Select 1 or more workspaces" to "Selected workspaces only"). (Public connections guide)
3. **Token endpoint and HTTP Basic Auth.** `POST https://api.notion.com/v1/oauth/token`, "authorized using HTTP Basic Authentication" with colon-delimited `CLIENT_ID:CLIENT_SECRET`; the OpenAPI spec defines `basicAuth`. (Authorization guide; Create a token reference)
4. **Token response fields.** `access_token`, `refresh_token`, `bot_id`, `workspace_id`, `owner`, `workspace_icon`, `workspace_name`, `duplicated_template_id` — the draft's instruction to store all fields is correct and `refresh_token` IS in the response. (Authorization guide; Create a token OpenAPI)
5. **Refresh rotates both tokens.** "Refreshing an access token will generate a new access token and a new refresh token." (Authorization guide; Refresh a token reference)
6. **Capabilities replace runtime scopes.** The authorize URL parameters are only `client_id`, `redirect_uri`, `response_type=code`, `owner=user`, `state` — there is no scope parameter; capabilities are configured in the portal and "users will need to re-authenticate with a connection if the capabilities are changed." (Authorization guide; Connection capabilities reference)
7. **User consent via "Allow access" + page picker per authorization.** "If the user clicks `Allow access`, they are then redirected to the `redirect_uri` with a temporary authorization `code`." Each user must authorize individually. (Authorization guide; Public connections guide)
8. **Template URL feature.** "Notion URL for optional template" input; user may duplicate the template instead of picking pages; `duplicated_template_id` returned in the token response. (Authorization guide)
9. **Redirect URIs: multiple allowed.** Registered under "OAuth Domain & URIs"; when more than one is registered (or redirect_uri was in the Authorization URL), `redirect_uri` becomes required in the token exchange; otherwise it is not allowed. (Create a token reference)
10. **Secrets storage guidance.** Secrets in the Configuration tab "should be protected and should never be included in source code or version control." (Authorization guide; Secure API tokens guide)
11. **Notion-Version header** required on API requests (latest version 2026-03-11). (Create a token reference)
12. **`state` parameter** optional, usable for CSRF prevention and state restoration. (Authorization guide)

## Corrected

1. **Developer console URL (most important).** Draft pointed to `https://developers.notion.com` — that is the documentation site. The official console is the Developer portal at **`https://app.notion.com/developers/connections`**; `https://www.notion.so/my-integrations` 307-redirects there (verified). Corrected in `guide.developer_console`, prerequisites, steps 1/2, and agent_vs_human.
2. **Marketplace review timeline is now published.** Draft said "no published SLA". The official "List on the Marketplace" FAQ states: "expect to hear back from our team within **5-10 business days** via email." Corrected `guide.time` and difficulty verdict. Review applies only to the optional Marketplace listing, not to starting OAuth.
3. **Client Secret "shown only once" is not supported by the docs.** The docs say to "access the connection's secrets in the **Configuration** tab" after creation — i.e., the secret is retrievable, not one-time-displayed. Draft step 7, secret gotcha, and the "secret lost → regenerate" blocker were rewritten; regeneration of the OAuth client secret is not documented (moved to unverified).
4. **Rate limits changed and were misstated.** Draft/source said "3 req/s per integration per workspace". Current official limits: **180 requests per 60-second window (avg 3/s)** on all plans except Business/Enterprise at **600/60s (avg 10/s)**; the budget can be spent "at any pace within the window"; a separate per-workspace limit is shared across all connections; querying a data source has a separate ~3 req/s per connection limit. Also, rate limit headers ARE now documented (`Retry-After`, `additional_data.retry_after`, `rate_limit_reason`) — removed from unverified.
5. **No "delete content" capability exists.** Draft's Composio snippet listed `delete_content` as a scope. Official capability list: read/update/insert content, read/insert comments, agent capabilities, and user info levels (none / without email / with email). Snippet scopes corrected to `read_content, update_content, insert_content, read_comments, insert_comments, read_user_information`; gotcha and mcp_note updated.
6. **Creation flow UI updated.** Draft: 'Click "New integration" and select "OAuth integration"'. Current docs: Developer portal → **Build → Public connections → "Create new connection"**; the form asks for connection name + development workspace, redirect URI(s), installation scope, and capabilities. "OAuth integrations and public integrations use the same OAuth authorization flow"; internal connections use a static token with no OAuth.
7. **Workspace owner requirement.** Draft prerequisite said "Personal account or workspace admin access". Official: "You are required to be a **workspace owner** to create a connection." (Authorization guide; Help Center: "Only Workspace owners will be able to access the Connections tab and create integrations.")
8. **Creation-form fields.** Draft step 3 listed name + logo + description. Official creation form documents name + development workspace, optional logo (Help Center), and capabilities; descriptions/categories/images are Marketplace **Listings** details managed separately, not creation fields.
9. **Template URL location.** It is configured **after creation** in the Configuration tab → Basic information ("Notion URL for optional template"), not in the creation form as the draft's step 6 implied.
10. **Redirect URI HTTPS/localhost claim downgraded.** "HTTPS required for production; http://localhost:* allowed for development" is NOT stated anywhere in Notion's official docs (the docs only link to generic OAuth guidance). Kept as practical guidance but flagged unverified in prerequisites, step 5 nuances, and the unverified list; exact-match/trailing-slash claims likewise not documented by Notion.
11. **Draft's "Sending client_id/client_secret in body fails"** was an inference; docs state the request "is authorized using HTTP Basic Authentication" (Basic is the documented method). Reworded to the documented requirement.
12. **agent_vs_human updated**: removed "Copy Client Secret (shown once)" and "Accept Notion API Terms of Service and Developer Policy" (terms acceptance not documented in the flow I verified) in favor of the verified portal steps; added Marketplace review timeline note; PKCE mention qualified (see below).
13. **Unverified list refreshed.** Removed: Marketplace review timeline (now documented, 5-10 business days) and rate limit headers format (now documented). Added: HTTPS/localhost redirect URI rules, exact-match semantics, client-secret regeneration, terms-acceptance step. PKCE entry corrected — Notion documents PKCE only for MCP clients; no `code_challenge` parameter exists in the REST OAuth authorize reference.

## Could not verify

Not stated anywhere in official Notion documentation (kept in the `unverified` list of corrections/notion.json):

1. Exact access token TTL — the token response includes `refresh_token` but no expiry fields.
2. Exact refresh token TTL.
3. HTTPS/localhost requirements for redirect URIs (standard OAuth guidance only).
4. Exact-match semantics for redirect URIs (trailing slash, query params, case).
5. Whether the OAuth client secret can be regenerated after creation (retrievable from the Configuration tab; no documented regeneration flow).
6. PKCE support for the REST API OAuth flow (documented only for Notion MCP clients).
7. Maximum number of redirect URIs per connection.
8. Detailed Marketplace rejection criteria (official FAQ gives general categories only: brand/trademark, quality, baseline criteria).
9. Integration ownership transfer process.
10. Whether accepting the Notion API Terms of Service / Developer Policy is a required portal step.
11. Composio-specific claims (`composio_next.managed`, catalog presence) — out of scope: verification restricted to official Notion sources; left unchanged except the Notion-side scope/capability fixes.
