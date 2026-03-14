# Hosted Deployment Guide

Hosted deployment is now the primary internal path for MVP Audience Insights.

- Frontend: Vercel
- Backend: Railway
- Database: shared hosted PostgreSQL
- Access: private internal allowlist
- Native bundle: fallback only

## Hosted architecture

The hosted setup uses Vercel as the authenticated front door and Railway as the protected API service.

- Users sign in to the Vercel app with an allowlisted email and the shared internal access code.
- The Vercel app stores a signed session cookie using `AUTH_SESSION_SECRET`.
- Browser requests go to Vercel route handlers under `/api/proxy/...`.
- The Vercel proxy forwards requests to Railway with `X-Internal-Api-Token`.
- Railway rejects non-health traffic unless the internal API token matches.
- Imported TikTok JSON files are stored centrally in the shared database with each ingestion run, so every allowlisted user sees the same imported source and resulting classifications/signals.

## Required environment variables

### Vercel frontend

Set these on the Vercel project for `apps/web`:

- `NEXT_PUBLIC_API_BASE_URL`
  - The public Railway API origin, for example `https://single-riders-api.up.railway.app`
- `API_BASE_URL`
  - Usually the same Railway API origin as `NEXT_PUBLIC_API_BASE_URL`
- `INTERNAL_API_TOKEN`
  - A long random token shared with Railway via `SCI_INTERNAL_API_TOKEN`
- `AUTH_SESSION_SECRET`
  - A long random secret used to sign the internal session cookie
- `AUTH_SHARED_ACCESS_CODE`
  - The internal shared access code your allowlisted users enter at login
- `AUTH_ALLOWED_USER_EMAILS`
  - Comma-separated allowlist of the real internal email addresses that should have access

Example:

```env
NEXT_PUBLIC_API_BASE_URL=https://single-riders-api.up.railway.app
API_BASE_URL=https://single-riders-api.up.railway.app
INTERNAL_API_TOKEN=use-a-long-random-token
AUTH_SESSION_SECRET=use-a-different-long-random-secret
AUTH_SHARED_ACCESS_CODE=SR-Internal-Launch-2026-Access
AUTH_ALLOWED_USER_EMAILS=smittynusmc@gmail.com,schnecklothkiele@gmail.com,joseph.lastoria@gmail.com,joethebeardednerd@gmail.com,adam.a.tucker@outlook.com,singleridersofficial01@gmail.com
```

### Railway backend

Set these on the Railway service for `apps/api`:

- `SCI_DATABASE_URL`
  - Shared PostgreSQL connection string
- `SCI_ALLOWED_ORIGINS`
  - Include the Vercel domain, for example `https://single-riders-insights.vercel.app`
- `SCI_INTERNAL_API_TOKEN`
  - Must match Vercel `INTERNAL_API_TOKEN`
- `SCI_WORKER_MODE`
  - Set to `inline` for the primary hosted deployment path
- `SCI_LLM_PROVIDER`
  - `stub` for demo/test behavior, or your configured provider when ready
- `SCI_LLM_MODEL`
  - Model name for the configured provider
- `SCI_LLM_BASE_URL`
  - Required when using `openai_compatible`
- `SCI_LLM_API_KEY`
  - Required when using `openai_compatible`
- `SCI_GITHUB_EXPORT_REPOSITORY`
  - Optional
- `SCI_TRELLO_BOARD_ID`
  - Optional

Example:

```env
SCI_ENVIRONMENT=production
SCI_DATABASE_URL=postgresql+psycopg://postgres:password@host:5432/comment_intelligence
SCI_ALLOWED_ORIGINS=https://single-riders-insights.vercel.app
SCI_INTERNAL_API_TOKEN=use-the-same-long-random-token-as-vercel
SCI_WORKER_MODE=inline
SCI_LLM_PROVIDER=stub
SCI_LLM_MODEL=single-riders-comment-intelligence-v1
```

## Vercel setup

1. Create a new Vercel project from this repository.
2. Set the project Root Directory to `apps/web`.
3. Leave the framework as Next.js.
4. Add the Vercel environment variables listed above.
5. Deploy.

Notes:

- [vercel.json](/c:/single-riders-comment-intelligence/apps/web/vercel.json) includes workspace-friendly install and build commands for the monorepo.
- [next.config.mjs](/c:/single-riders-comment-intelligence/apps/web/next.config.mjs) is configured for standalone output and shared package tracing.

## Railway setup

1. Create a new Railway service from this repository.
2. Set the service Root Directory to `apps/api`.
3. Attach a shared PostgreSQL database or point `SCI_DATABASE_URL` at your hosted Postgres.
4. Add the Railway environment variables listed above.
5. Deploy.

Notes:

- [Procfile](/c:/single-riders-comment-intelligence/apps/api/Procfile) runs `alembic upgrade head` before starting `uvicorn`.
- The hosted-first path uses `SCI_WORKER_MODE=inline`, so you do not need a separate worker service for the initial internal deployment.

## First admin user setup

There is no separate seeded admin table in phase 1.

- All access is controlled by `AUTH_ALLOWED_USER_EMAILS`.
- Add the real internal email addresses you want to admit to that allowlist.
- All allowlisted users currently have the same internal admin privileges.

If you want to add or remove users later, update `AUTH_ALLOWED_USER_EMAILS` and redeploy Vercel.

## Allowlist setup

Use real email addresses, not first names.

Good:

```env
AUTH_ALLOWED_USER_EMAILS=smittynusmc@gmail.com,schnecklothkiele@gmail.com,joseph.lastoria@gmail.com,joethebeardednerd@gmail.com,adam.a.tucker@outlook.com,singleridersofficial01@gmail.com
```

Avoid:

```env
AUTH_ALLOWED_USER_EMAILS=Adam,Joe,Kiele,Jason
```

## Shared upload storage

Hosted imports are centralized in the shared database.

- The original uploaded file bytes are stored with the ingestion run.
- The uploader email is recorded when the import comes through the authenticated Vercel proxy.
- Import history shows the source file and uploader.
- The normalized comments, classifications, and signals are shared across all allowlisted users.

This means Adam, Joe, Kiele, and Jason will all see the same import history and the same processed results.

## TikTok JSON download steps

Use TikTok's official export flow:

1. Open TikTok.
2. Go to `Profile`.
3. Open `Menu` > `Settings and privacy` > `Account` > `Download your data`.
4. Choose `JSON`.
5. Submit the request.
6. Download the export when TikTok makes it available.
7. Upload it in the hosted app from the `Imports` page.

Official support page:

- https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/how-to-download-your-data

## Operational notes

- Do not use login history, device/IP history, or private DM history in dashboard counts, date-range calculations, or product insight summaries.
- Railway health checks can use `/health` without the internal API token.
- Everything else is protected by `SCI_INTERNAL_API_TOKEN` when that variable is set.
- The native bundle in `dist/native` remains available as a fallback only.
