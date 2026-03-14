# Single Riders Comment Intelligence

Single Riders Comment Intelligence is a production-minded internal product tool for turning social comments into grouped MVP signals. It is built as a monorepo with a FastAPI API and worker pipeline, a Next.js admin dashboard, and export placeholders for backlog handoff.

## Why this shape

- TikTok JSON export import is the primary ingestion path for phase 1.
- CSV remains supported as a convenience path for cleaned manual datasets and third-party exports.
- The ingestion layer is adapter-based so the core pipeline never depends on TikTok-specific retrieval logic.
- TikTok OAuth is intentionally not part of ingestion design because TikTok public developer APIs do not expose organic comment retrieval.
- Raw comments, normalized comments, classifications, and grouped signals are stored separately so the system stays auditable and replayable.

## Monorepo structure

```text
apps/
  api/        FastAPI service, worker pipeline, Alembic, backend tests
  web/        Next.js internal admin dashboard
packages/
  shared-types/  Shared TypeScript API shapes for the web app
docs/
  architecture.md
  frontend.md
  handoff.md
  ingestion.md
  mvp-audience-insights.md
  native-handoff.md
infra/
  docker/
  docker-compose.yml
  windows/
sample_data/
  tiktok_comments_sample.json
  tiktok_comments_sample.csv
```

## Backend highlights

- FastAPI + SQLAlchemy + Pydantic
- PostgreSQL-ready persistence model with Alembic migration scaffold
- Redis/RQ worker orchestration with explicit inline fallback for local development
- `TikTokJsonImportAdapter` for TikTok-style export and portability JSON files
- `CsvImportAdapter` for secondary CSV convenience imports
- `TikTokResearchAdapter` parser for approved research response JSON supplied manually
- Placeholder adapters for manual paste, third-party exports, and future approved TikTok connectors
- Rules pre-pass for: `beta`, `safety`, `fake`, `bot`, `meetup`, `same day`, `passholder`
- Structured classification contract with configurable provider mode (`stub` or `openai_compatible`)
- Signal aggregation service that groups repeated requests into ranked MVP signals

## Frontend highlights

- Next.js App Router with TypeScript
- Tailwind and shadcn-style primitives
- TanStack Table for explorer and review tables
- Recharts trend chart on the dashboard
- Audience insights ranking tied to MVP themes and user-story alignment
- Imports page with drag-and-drop upload, format preview, sections detected, ignored sections, sample fields, missing fields, and parse warnings
- In-app guide page with workflow help, glossary, and data-scope rules
- Pages for dashboard, audience insights, imports, comments, classifications, signals, guide, and review queue

## Hosted deployment

Hosted deployment is now the primary internal path.

- Frontend: Vercel
- Backend: Railway
- Database: shared hosted PostgreSQL
- Access: allowlisted internal users only

Use [hosted-deployment.md](/c:/single-riders-comment-intelligence/docs/hosted-deployment.md) for the full setup guide, including Vercel setup, Railway setup, environment variables, first admin setup, allowlist setup, and shared upload storage behavior.

## Fallback handoff

The native and Docker handoff flows remain available as fallback options when hosted deployment is not the right fit.

This repo now supports two teammate-friendly handoff paths:

- native Windows packaging for teammates who should not install Python, Node, PostgreSQL, or Redis
- Docker handoff as the fallback path when you want the whole stack containerized

### Native Windows handoff

1. Build the native package with `.\scripts\build-native-installer.bat`.
2. Share the installer or the portable zip from `dist\native`.
3. On the teammate machine, install or unzip the package.
4. Double-click `scripts\start-native.bat`.
5. Double-click `scripts\stop-native.bat` when you are done.

The native bundle includes the API executable, the standalone web server, a bundled Node runtime, and SQLite storage. See [native-handoff.md](/c:/single-riders-comment-intelligence/docs/native-handoff.md).

### Docker handoff

1. Install Docker Desktop and open it once.
2. Unzip the shared handoff bundle.
3. Double-click `scripts\start-handoff.bat`.
4. Wait for the browser to open `http://localhost:3000/guide`.
5. Double-click `scripts\stop-handoff.bat` when you are done.

This creates a teammate-friendly environment with Docker services and automatic database migrations. See [handoff.md](/c:/single-riders-comment-intelligence/docs/handoff.md) for the full Docker-based flow.

## Get your TikTok JSON export

Use TikTok's official export flow:

1. Open TikTok and go to `Profile`.
2. Open `Menu` > `Settings and privacy` > `Account` > `Download your data`.
3. Choose `JSON` as the file format for this app.
4. Submit the request and download the file when TikTok makes it available.

TikTok's official support page is here:

- https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/how-to-download-your-data

## Local development

### Prerequisites

- Python 3.11+
- Node 20+
- PostgreSQL 16+
- Redis 7+

### Backend

1. Copy `apps/api/.env.example` to `apps/api/.env` and adjust values.
2. Create a virtual environment and install dependencies:
   - `cd apps/api`
   - `pip install -e .[dev]`
3. Run migrations:
   - `alembic upgrade head`
4. Start the API:
   - `uvicorn app.main:app --reload`
5. Start the worker in another terminal:
   - Windows local shortcut: set `SCI_WORKER_MODE=inline`
   - Redis worker path: `rq worker comment-intelligence --url %SCI_REDIS_URL%`
6. Seed from the sample TikTok JSON export if desired:
   - `python -m app.scripts.seed`

Windows shortcut:

- `.\scripts\dev-api.ps1`

### Frontend

1. Copy `apps/web/.env.example` to `apps/web/.env.local`.
2. Install workspace dependencies from the repo root:
   - `npm install`
3. Start the dashboard:
   - `npm run dev:web`

Windows shortcut for NVM-managed Node 20+:

- `.\scripts\dev-web.ps1`

### Docker compose

- `docker compose -f infra/docker-compose.yml up --build`

## Sample data

Use [tiktok_comments_sample.json](/c:/single-riders-comment-intelligence/sample_data/tiktok_comments_sample.json) to exercise the primary TikTok JSON import flow, or [tiktok_comments_sample.csv](/c:/single-riders-comment-intelligence/sample_data/tiktok_comments_sample.csv) for CSV fallback testing.

## Key API routes

- `POST /imports/preview`
- `POST /imports/json`
- `POST /imports/csv`
- `GET /imports`
- `GET /imports/{id}`
- `GET /comments`
- `GET /comments/{id}`
- `GET /classifications`
- `PATCH /classifications/{id}`
- `GET /signals`
- `GET /signals/{id}`
- `POST /signals/rebuild`
- `PATCH /signals/{id}`
- `POST /signals/{id}/export/github`
- `POST /signals/{id}/export/trello`
- `GET /dashboard/summary`
- `GET /dashboard/trends`
- `GET /dashboard/top-signals`
- `GET /dashboard/audience-insights`

## Tests

### Backend

- `cd apps/api`
- `pytest`

### Frontend

- `cd apps/web`
- `npm run test`

## Commit message ideas

- `feat(api): add json-first comment ingestion pipeline`
- `feat(web): add import preview workflow to the admin dashboard`
- `feat(worker): add rules, classification, and signal orchestration`
- `docs(architecture): document adapter-first json ingestion design`
