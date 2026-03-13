# Single Riders Comment Intelligence

Single Riders Comment Intelligence is a production-minded internal product tool for turning social comments into grouped MVP signals. It is built as a monorepo with a FastAPI API and worker pipeline, a Next.js admin dashboard, and export placeholders for backlog handoff.

## Why this shape

- CSV import is the MVP ingestion path.
- The ingestion layer is adapter-based so the core pipeline does not depend on TikTok-specific retrieval logic.
- TikTok OAuth is intentionally not part of ingestion design because public TikTok developer APIs do not expose organic comment retrieval.
- Raw comments, normalized comments, classifications, and aggregated signals are stored separately so the pipeline stays auditable and replayable.

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
  ingestion.md
infra/
  docker/
  docker-compose.yml
sample_data/
  tiktok_comments_sample.csv
```

## Backend highlights

- FastAPI + SQLAlchemy + Pydantic
- PostgreSQL persistence model with Alembic migration scaffold
- Redis/RQ worker orchestration with explicit inline fallback for local development
- CSV adapter implemented first
- Placeholder adapters included for manual paste, third-party exports, and future approved TikTok connectors
- Rules pre-pass for: `beta`, `safety`, `fake`, `bot`, `meetup`, `same day`, `passholder`
- Structured classification contract with configurable provider mode (`stub` or `openai_compatible`)
- Signal aggregation service that groups repeated requests into ranked MVP signals

## Frontend highlights

- Next.js App Router with TypeScript
- Tailwind and shadcn-style primitives
- TanStack Table for explorer/review tables
- Recharts trend chart on the dashboard
- Pages for dashboard, imports, comments, classifications, signals, and review queue

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
   - `rq worker comment-intelligence --url %SCI_REDIS_URL%`
6. Seed from sample CSV if desired:
   - `python -m app.scripts.seed`

### Frontend

1. Copy `apps/web/.env.example` to `apps/web/.env.local`.
2. Install workspace dependencies from the repo root:
   - `npm install`
3. Start the dashboard:
   - `npm run dev:web`

### Docker compose

- `docker compose -f infra/docker-compose.yml up --build`

## Sample CSV

Use [sample_data/tiktok_comments_sample.csv](/c:/single-riders-comment-intelligence/sample_data/tiktok_comments_sample.csv) to exercise the full import and signal pipeline without any live TikTok access.

## Key API routes

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

## Tests

### Backend

- `cd apps/api`
- `pytest`

### Frontend

- `cd apps/web`
- `npm run test`

## Commit message ideas

- `feat(api): add csv-first comment ingestion pipeline`
- `feat(web): build internal signal review dashboard`
- `feat(worker): add rules and classification orchestration`
- `docs(architecture): document adapter-first ingestion design`
