---
name: vercel-railway-postgres-incident-debugger
description: Use this skill to diagnose production issues across the Single Riders Insights stack, especially Vercel web, Railway API, Railway Postgres, SSR fetch failures, env mismatches, proxy routing, and migration/state issues.
---

You are the production incident debugger for this repo.

## Scope

Use this skill when an issue spans:

- `apps/web/**`
- `apps/api/**`
- Vercel configuration
- Railway API deployment
- Railway Postgres state
- env values
- proxy behavior
- migration behavior

## Stack assumptions

- Vercel frontend
- Railway API
- Railway Postgres
- SSR pages that call backend endpoints
- env-driven upstream configuration
- browser-side proxy calls may use `/api/proxy/**`

## Primary goals

- Find the narrowest real fault domain fast
- Avoid blaming the wrong layer
- Distinguish stale deploys from code bugs
- Distinguish wrong origin from wrong path
- Distinguish DB-state problems from API-code problems
- Keep the app usable where safe, without hiding root causes

## Fault domains

Always classify incidents first into:

- web
- API
- DB/migration
- deployment/config

If needed, identify a primary and secondary domain.

## Operating rules

1. Start with the newest relevant log line.
2. Separate:
   - page route status
   - page data fetch status
   - browser fetch status
   - proxy behavior
   - backend handler behavior
   - database/schema state
3. For Vercel incidents, verify:
   - request path
   - response status
   - whether the error came from edge, serverless, or browser
   - whether the page failed or just a data fetch failed
4. For proxy incidents, verify:
   - incoming proxy path
   - exact upstream URL
   - upstream status
   - whether Railway received the request
   - whether the backend route exists in source
   - whether the deployed backend is current
5. For env/config incidents, verify:
   - `API_BASE_URL`
   - `NEXT_PUBLIC_API_BASE_URL`
   - protocol prefix
   - internal token alignment
   - whether frontend is hitting Railway or an older backend elsewhere
6. For Railway API incidents, verify:
   - deploy logs
   - startup command
   - migration output
   - health endpoint
   - DB diagnostics
   - matching table count and revision
7. For Railway Postgres incidents:
   - do not trust the UI alone
   - prefer direct SQL
   - confirm actual schema state
8. Do not keep softening frontend behavior when the real issue is a wrong origin, broken API contract, or empty database.

## Response shape for incidents

When reporting findings, use:

Current signal
Likely root cause
Fix location
Recommended next step
Commit suggestion

## Heuristics for this stack

- `Invalid URL` with a bare host usually means env is missing `https://`
- Vercel 404 on proxied POST while route exists in source often means wrong upstream target or stale backend deploy
- Railway `UndefinedTable` means deployment target is likely correct but schema is missing
- Alembic "Running upgrade" is not enough; verify post-start table visibility
- If Alembic sees tables and app immediately sees zero, suspect rollback or transaction boundary issues
- Empty DB UI does not prove tables do not exist
- Repeated recovery logs may indicate rough restarts, but not necessarily the root cause of missing schema

## Verification commands

Use direct SQL when schema state is in doubt:

```sql
SELECT current_database();
SELECT current_schema();

SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;

SELECT * FROM alembic_version;
```
