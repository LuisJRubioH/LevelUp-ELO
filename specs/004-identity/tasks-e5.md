# Tasks — spec 004, delivery E5

**Plan**: [plan-e5.md](plan-e5.md). FR-080 … FR-082 and FR-085 are `[CHANGE]` (their tests fail on
the base branch); FR-083 is `[AS-IS]`. Written with the code; done unless marked open.

- [x] T001 API: cookie scope and SameSite setting, deletion with the same attributes, no-store,
  foreign `Origin` refused, foreign WebSocket refused, 15-minute token, revoked or inactive renewal
  refused, proxy rule before the SPA fallback — `tests/api/test_spec004_e5_session.py`
- [x] T002 Screens: renewal by itself through the same origin, reload, logout, refused renewal —
  `frontend/e2e/spec004-session.spec.ts`
- [x] T003 `AUTH_COOKIE_SAMESITE`; cookie helpers; origin dependency on the auth router; no-store
  middleware (`api/config.py`, `api/routers/auth.py`, `api/main.py`)
- [x] T004 WebSocket origin check (`api/websocket/connections.py`, `notifications.py`, `pvp.py`)
- [x] T005 `frontend/vercel.json` proxy; `frontend/src/api/wsBase.ts` and both socket hooks
- [x] T006 `docs/transfer.md` § 3 and § 3.3, `.env.example`
- [ ] T007 FR-084 / US9-AS4 for expired accounts — with E3
- [ ] T008 US9-AS5 — Safari on iPhone, iPad and desktop after the owner's switch
