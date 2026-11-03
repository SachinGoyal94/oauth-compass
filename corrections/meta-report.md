# Meta (Facebook) OAuth Guide — Verification Report (agent-verified, human-supervised)

Draft: `knowledge/guides/drafts/meta-for-developers/v1.md`
Corrections: `corrections/meta.json`
Verified against official Meta documentation only (developers.facebook.com), 2026-11-03.

## Confirmed

- App creation flow at developers.facebook.com/apps/creation/: app name + contact email, use-case selection, business portfolio step ("Create an App" doc).
- public_profile is auto-added as a required, non-removable permission by relevant use cases ("Create an App" doc).
- Valid OAuth Redirect URIs configured in App Dashboard under Facebook Login > Settings; the redirect_uri must be identical at the Login Dialog step and the server-side token-exchange step; state is listed among required parameters of the manual flow (manual-flow doc).
- Token exchange endpoint `https://graph.facebook.com/{v}/oauth/access_token` must be called server-to-server (app secret involved).
- In Development mode, only people with a role on the app can use it; Live mode is required before role-less users can request App Review-approved permissions (App Mode/Release doc).
- Standard Access vs Advanced Access: all Business/Consumer/Gaming apps are automatically approved for Standard Access (role-holders only); Advanced Access is approved per-permission via App Review and requires Business Verification (Access Levels doc).
- Business Verification: apps requesting Advanced Access must be connected to a business that completed verification; done via App Dashboard Settings > Basic > Verification; exemptions when only role-holders use the app (Business Verification doc).
- App Review submission requires: 1024x1024 app icon, public Privacy Policy URL, high-res (1080+) screen recordings per permission, valid reviewer/test credentials, at least one successful API call per permission within 30 days of submitting; inaccessible app = whole submission rejected; stay in Development mode during review (App Review Submission Guide).
- Data deletion: a Data Deletion Request URL callback (HTTPS) or data deletion instructions URL is required; privacy policy must explain deletion requests (Data Deletion Callback doc).
- Long-lived user access tokens generally last about 60 days; short-lived ~1-2 hours; Meta warns lifetimes may change without warning (Access Tokens doc).

## Corrected

1. **"User access tokens expire after 60 days and cannot be refreshed" → wrong.** Long-lived tokens are refreshable: mobile SDK tokens auto-refresh once per day when the user is active (90-day window); an expired token cannot be exchanged, but active users' tokens renew. Draft's step 10 and token gotcha rewritten. (Most important correction.)
2. **Graph API version v19.0 in the Composio snippet → v26.0** (version shown in current official manual-flow docs); note added that versions rotate.
3. **"Business apps have modes and a Development/Live toggle" → Business apps have no app modes** and rely exclusively on access levels; step 8 and the Development-mode gotcha now scope the toggle to Consumer/Gaming apps.
4. **Terms of Service URL marked "Required" → not required** by the official App Review submission guide; it is now optional/non-blocking, replaced by the genuinely required app icon (1024x1024) prerequisite.
5. **Missing prerequisite added: data deletion callback URL or instructions URL** (mandatory, HTTPS, confirmation_code + url JSON response; non-compliance can disable the app).
6. **"Business Verification needed for WhatsApp/Instagram/Marketing APIs" → generalized:** Business Verification is required for any Advanced Access permission (since Feb 1, 2023), not just those APIs; the process runs from App Dashboard Settings > Basic > Verification (not "Business Manager → Security Center" as the draft claimed).
7. **Step 2 "choose an app type (Consumer or Business)" → the modern flow is use-case based**; use cases cannot be removed after creation, and required permissions cannot be removed.
8. **"public_profile is added automatically" → refined with Standard/Advanced Access detail:** automatic Advanced Access for email + public_profile applies to new Consumer apps only, is Standard by default, and requires the app to be Live first.
9. **App Review gotcha rewritten:** screen recordings (1080p+, per permission, reviewers ignore audio), missing recordings = permission not approved; screencast/test-user detail upgraded from "reported" to verified_from_docs.
10. **Redirect URI gotcha upgraded to verified_from_docs** with state parameter and desktop webview fixed redirect (`https://www.facebook.com/connect/login_success.html`) added; HTTPS-only-for-redirect-URIs kept as unverified (docs only confirm HTTPS for JS SDK auth actions).
11. **Sources replaced:** 12 official Meta pages (max respected); the non-Meta Nango source removed from evidence; every corrected fact carries `verified_from_docs` + source_url; genuinely unknown items (review timeline, app-token permanence, HTTPS rule, Composio catalog) stay `reported`/`unknown` and are listed under `unverified`.
12. **Steps trimmed 10 → 9** (draft's redundant "Add Website platform" step removed as not required by official docs; all other steps 5–12 range respected, same schema/tone).

## Could not verify

- App Review timeline ("a few days to several weeks") — official docs state no duration; kept as community-reported.
- Meta Developer registration step-by-step details — not documented on fetched pages.
- HTTPS-only rule for all Valid OAuth Redirect URIs — not explicitly stated in the manual-flow doc.
- Whether general app access tokens never expire — docs only say Marketing API Standard-access and System User tokens do not expire by time.
- Composio managed auth config availability — catalog not found; custom auth kept.
- Meta API rate limits/caps — not checked.
- Exact current Graph API version — v26.0 at fetch time; versions rotate quarterly.
