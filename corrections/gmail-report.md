# Gmail OAuth Guide — Verification Report (agent-verified, human-supervised)

Draft reviewed: `knowledge/guides/drafts/gmail/v1.md` (2026-11-03)
Method: every substantive claim checked against official Google pages only (developers.google.com / support.google.com). JSON corrections in `corrections/gmail.json`.

## Confirmed

- **7-day refresh token expiry in Testing** — an external user type project with publishing status "Testing" is issued refresh tokens expiring in 7 days, unless the only scopes requested are userinfo.email / userinfo.profile / openid. (developers.google.com/identity/protocols/oauth2)
- **100 test users in Testing status** — "Projects configured with a publishing status of Testing are limited to up to 100 test users listed in the OAuth consent screen"; test-user authorizations expire 7 days after consent. (support.google.com/cloud/answer/15549945)
- **Unverified-app warning screen and 100 new-user cap** — apps requesting sensitive or restricted scopes without verification show the unverified app screen and are limited to 100 new users; the cap applies over the entire lifetime of the project and cannot be reset, even in production; exhaustion disables Google sign-in. (support.google.com/cloud/answer/7454865, /13463817, /15549945)
- **Restricted Gmail scopes** — gmail.readonly, gmail.compose, gmail.modify, gmail.metadata, gmail.insert, gmail.settings.basic, gmail.settings.sharing and https://mail.google.com/ are RESTRICTED. (developers.google.com/gmail/api/auth/scopes)
- **Verification + demo video + per-scope justification required** for sensitive/restricted scopes; exemptions exist for certain scenarios. (support.google.com/cloud/answer/13464321, /13464323)
- **Redirect URI rules** — HTTPS required (localhost exempt), no raw IP hosts (localhost exempt), no wildcards, no fragment, exact match else redirect_uri_mismatch. (developers.google.com/identity/protocols/oauth2/web-server)
- **access_type=offline / prompt=consent semantics** — refresh token issued on first exchange; prompt=consent needed to re-issue. Same page.
- **Access-token ~1h lifetime, invalid_grant handling, incremental authorization best practice** — consistent with web-server page and oauth2 overview.
- **Brand verification** — a lighter-weight "brand-verification" process is needed to display app name/logo on the consent screen. (support.google.com/cloud/answer/9110914)
- **Refresh-token limit** — "limit of 100 refresh tokens per Google account per OAuth 2.0 client ID" is stated on the oauth2 overview page; moved out of the unverified list.

## Corrected

1. **Most important: "all Gmail scopes are restricted" is wrong.** gmail.send is SENSITIVE (verification only); gmail.readonly and most other Gmail data scopes are RESTRICTED; gmail.labels and add-on action scopes are non-sensitive. Fixed in step 3, step 10, difficulty verdict, and summary.
2. **Missing CASA security assessment.** Restricted scopes require, beyond verification, a security assessment by a CASA-authorized independent assessor, repeated annually; Google charges no fee but the developer pays the authorized assessor (or uses Tier 1 self-scan where eligible). Added to step 10 and a new gotcha. (support.google.com/cloud/answer/13463817)
3. **100-user cap nuance.** The 100 cap for unverified apps is 100 NEW users for the project's entire lifetime (cannot be reset), distinct from the 100-test-user limit in Testing. Gotcha rewritten accordingly. (13463817, 15549945)
4. **Quota numbers outdated.** Draft said 1 billion units/day per project and 250 units/sec per user. Official quota page (updated May 1, 2026): new projects get 1,200,000 units/min/project, 6,000 units/min/user, 80,000,000 units/day billing threshold; per-method costs 1–100+ units; projects created before May 1, 2026 keep prior quotas. Fixed step 7 and quota gotcha. (developers.google.com/workspace/gmail/api/reference/quota)
5. **Step 10 retitled and rewritten** to include the security assessment and the correct sensitive/restricted framing.
6. **Unverified list trimmed** — removed the refresh-token 100/account/client limit (now verified) and the per-method quota costs item (now verified).

## Could not verify

- Exact verification review timeline in business days (no official figure found on fetched pages).
- Exact OAuth token endpoint rate limits (~100 req/100s/user is community-reported only).
- Maximum redirect URIs per client (50 suspected; not stated on fetched official pages).
- Enterprise/Workspace Marketplace listing fees.
- Service account / domain-wide delegation specifics for Gmail.
- Full re-verification trigger list beyond new scopes/branding changes.
- Whether authorized-domain verification currently runs via Search Console (help center now points to "Google Auth Platform"; exact flow not confirmed) — draft step 2 nuance retained but flagged.
