# Plan — spec 004, delivery E5: session renewal without third-party cookies

**Spec**: [spec.md](spec.md) § Deliveries, E5 (US9; FR-080 … FR-085) · **Branch**:
`004-identity-e5` · **Date**: 2026-10-14 · **Order**: after E2's revocation (its part 1)

E5 stays `in progress`: the expiry of an account (FR-084, US9-AS4) arrives with E3, and Safari on
real devices (US9-AS5) is the owner's check after the switch. Nothing here changes production by
itself: the owner switches it on (`docs/transfer.md` § 3.3). Block 8 forbids a deployment from
this work.

## Design

- **Same-origin proxy, prepared** (FR-080). `frontend/vercel.json` forwards `/api/*` to the API
  before the single-page fallback. The HTTP client already uses the page's origin when
  `VITE_API_URL` is empty (V2-R10); WebSockets get their own base, `VITE_WS_URL`, because the
  proxy carries HTTP only (decision N6, applied as recommended).
- **Cookie** (FR-081). Always `HttpOnly`, `Secure`, `Path=/api/auth`; `SameSite` from
  `AUTH_COOKIE_SAMESITE` — `none` by default (today's cross-origin flow), `lax` after the switch;
  an unknown value stops the start. Logout deletes it with the same attributes (today it omits
  `Secure`/`SameSite`, and a browser can keep a cross-site cookie).
- **Unauthorised requests and caching** (FR-082). A state-changing `/api/auth/*` request whose
  `Origin` is not in `CORS_ORIGINS` is refused with 403 before anything runs; requests without
  `Origin` (not a browser) pass. Every `/api/auth/*` response carries `Cache-Control: no-store`.
  Both are safe in today's flow: the frontend's origin is in `CORS_ORIGINS` already.
- **Revocation** (FR-084, part). Renewal checks the security version (E2) and the account's state.
- **WebSockets** (FR-085). First-message authentication with the security version (E2); a browser
  socket from an origin outside `CORS_ORIGINS` is refused at the handshake (N6).
- **Access token** (FR-083, as is). 15 minutes.

## Switch (owner, documented)

Vercel: `VITE_API_URL` empty, `VITE_WS_URL` = the API's `wss://` origin; then Render:
`AUTH_COOKIE_SAMESITE=lax`. Undo in the reverse order. Everyone signs in once more after the switch.
Checks on Safari (iPhone, iPad, desktop) and Chrome, each labelled real device or automated.

## Not in E5 yet

FR-084 and US9-AS4 for expired accounts (E3); US9-AS5 on real Safari devices (owner).

## Automated check on Safari's engine (2026-10-20)

`frontend/playwright.session.config.ts` runs US9-AS1 … AS4 (`frontend/e2e-session/`) against the
real API on SQLite, with the page and the API on one HTTPS origin and `AUTH_COOKIE_SAMESITE=lax`,
as after the switch, in WebKit as Safari desktop, iPhone and iPad, and in Chromium (CI job
"Sesión en Safari (WebKit)"). Its results are labelled *automated*. They do not close US9-AS5:
WebKit on Linux does not apply Safari's tracking prevention, which is what E5 addresses, so the
check on a real device (the owner's, or a remote real-device service) stays the reference.
