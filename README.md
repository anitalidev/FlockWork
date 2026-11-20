# Flockwork

A warm, student-centered community platform built for HackCamp 2026. Flockwork helps students find study partners and friends, exchange skills, and discover project collaborators.

> Flockwork is an independent student project and is not affiliated with the University of British Columbia.

## Current scope

Flockwork is a full-stack app: a React/TypeScript frontend hosted on DeepSpace and a FastAPI backend.

- **Sign-in:** Auth0 passwordless email login (`/auth`). The backend verifies each token's signature, issuer and audience, and only accepts verified UBC email addresses.
- **Buddies and SkillShare:** swipe decks ranked by compatibility, with mutual-like matching.
- **Projects:** create, browse and delete listings (only the owner can delete), plus teammate discovery by skill.
- **Messaging:** private conversations between matched students.
- **Campus activity heatmap:** opt-in location sharing, aggregated into broad areas so no one's exact location is shown. A shared location expires after 3 minutes (`PRESENCE_TTL_SECONDS`).

The previews and artwork on the public landing page are illustrative, not live student data.

## Deployment

| Part | Host | Check |
|---|---|---|
| Frontend | DeepSpace, `https://flockwork.app.space` | Page loads and `/api/client-config` returns JSON |
| Backend | Railway (Vultr guide in `deploy/vultr/`) | `/` returns `{"status":"ok"}`, `/health/db` returns `{"database":"ok"}` |
| Auth | Auth0 | Login on the live site reaches the dashboard |

### Backend (Railway)

Set the service's root directory to `backend`. `backend/Procfile` starts the API with:

```sh
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Required variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Persistent PostgreSQL URL. If unset, the API falls back to a local SQLite file that is wiped on every redeploy (a warning is logged). |
| `AUTH0_DOMAIN` | Auth0 hostname, without `https://` |
| `AUTH0_AUDIENCE` | The Auth0 API identifier (same value as the frontend) |
| `CORS_ORIGINS` | Frontend origins, comma-separated, e.g. `https://flockwork.app.space` |
| `GEMINI_API_KEY` | Optional, for AI listing tools |

If the database is unreachable at startup, the API still starts: `/` answers, `/health/db` returns 503, and the real error is in the logs.

### Frontend (DeepSpace)

The deployed worker needs `VITE_API_URL` (the backend URL), `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID` and `VITE_AUTH0_AUDIENCE` at runtime, not only in a local `.env`. Never put a client secret there.

### Auth0

- Allowed callback URL: `https://flockwork.app.space/auth`
- Allowed logout URL: `https://flockwork.app.space`
- Passwordless connection: `email`; scopes `openid profile email`
- Frontend and backend must use the same tenant and API audience.

### Definition of working

1. Backend `/` and `/health/db` both succeed.
2. The frontend and `/api/client-config` load.
3. Signed out, `/me` returns 401.
4. A verified test user can create and read their profile.
5. Two test accounts can match, and one cannot delete the other's project.
6. A shared location shows on the heatmap, can be removed, and expires.
7. Data survives a backend redeploy.

## Frontend-only local preview

Requires Node 22.15+ (22.x, 24.x, or 26.x) and npm 11.6+. Install with `npm ci`.

```sh
npm --prefix frontend run preview:local -- --host 127.0.0.1 --port 5174 --strictPort
```

Open http://localhost:5174/. This uses `vite.preview.config.ts` and does **not** register an app, authenticate users, access a database, deploy, or spend DeepSpace credits. Its inert placeholder is never a valid DeepSpace app ID and the preview configuration is not for deployment or shared production data.

## DeepSpace

- SDK: `deepspace@0.43.0` (pinned)
- Documentation: https://docs.deep.space — append `.md` to a documentation URL for Markdown.
- Production build: `npx deepspace build`, or `npx deepspace deploy` when deliberate registration/deployment has been approved.
- App registration: `npx deepspace auth whoami`, then `npx deepspace app init`. Confirm the intended owner first.
- Full-stack local development: `npx deepspace dev start`, after checking the intended account and port.

The scaffold intentionally leaves `DEEPSPACE_APP_ID = "__APP_ID__"` until registration. Do not substitute a hand-written ID to make the production build or SDK test configuration pass. The frontend-only preview/test configs are isolated from this safeguard.

**Source control is GitHub:** `goople-tech/skillshare`. Before a first deployment, read https://docs.deep.space/guides/source-control.md. A first deployment can permanently attach the app's source provider; never run `deepspace push` as a shortcut.

## Checks

```sh
npm --prefix frontend run lint           # full-project ESLint
npm --prefix frontend run test:frontend  # pure frontend validation tests; no app ID needed
cd frontend && npm run type-check        # after app registration (SDK app ID required)
cd frontend && npm run build             # production build; registered app ID required
```

## Team workflow

- Keep `main` stable. Work on small feature branches such as `feat/buddies-discovery`.
- Rebase or merge the current default branch before opening a focused PR; do not rewrite teammates' branches.
- Keep unrelated refactors and generated artifacts out of PRs. `node_modules`, `dist`, `.dev.vars`, and local credentials are ignored.
- Include a short summary, UI screenshots for visual changes, commands tested, and any unfinished integration work.
- Preserve distinctions between illustrative previews and live user data. Student status must be verified server-side before granting student-only privileges.
- Follow the relevant `AGENTS.md` before editing. Frontend guidance is in `frontend/src/components/landing/AGENTS.md`. Backend-local boundaries are in `backend/AGENTS.md`.

## Teammate backend starter

`backend/` provides FastAPI, SQLite/Postgres, and Gemini-powered listing tools. The original `frontend/src/App.jsx` and `api.js` are preserved as integration references for that workflow; they are not connected to the new landing page yet. Latest main includes Auth0 passwordless code and bearer/JWKS verification for protected routes. Review its verified-email and token-validation behavior for actual identity handling; the landing demo domain check is only a presentation prototype. Keep any new integration explicit about its security boundary, coordinate API changes with backend contributors, and never expose `GEMINI_API_KEY` to the browser.

## Dependency security

DeepSpace remains `0.43.0`; its transitive `better-auth` dependency is pinned/overridden to `1.7.18` with the matching adapter family to address advisory-affected earlier 1.6 releases. This is a compatibility-only security fix until the Auth0 owner replaces the scaffold authentication; it is not a competing authentication implementation. No change to the landing page's explicit prototype signup flow is implied. Updating that override requires a matching compatibility review and an `npm ci`, not only a shallow `npm ls` against the previously installed directory.
