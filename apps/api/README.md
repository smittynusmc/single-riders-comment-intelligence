# API Workspace

FastAPI service and background worker for the Single Riders comment intelligence platform.

## Hosted deployment

For the hosted internal deployment path:

- deploy this workspace to Railway with Root Directory `apps/api`
- let Railway install [requirements.txt](/c:/single-riders-comment-intelligence/apps/api/requirements.txt) or set a custom build command of `pip install -r requirements.txt`
- keep the default [Procfile](/c:/single-riders-comment-intelligence/apps/api/Procfile), which uses `python -m alembic` and `python -m uvicorn` so the `app` package stays importable in production containers
- set `SCI_DATABASE_URL` to the shared hosted database
- set `SCI_INTERNAL_API_TOKEN` to match the Vercel `INTERNAL_API_TOKEN`
- keep `SCI_WORKER_MODE=inline` for the initial hosted rollout

See [hosted-deployment.md](/c:/single-riders-comment-intelligence/docs/hosted-deployment.md).
