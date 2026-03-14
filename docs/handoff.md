# Docker Handoff Guide

Docker handoff is the fallback path now that hosted deployment is the primary internal setup.

This guide covers the Docker-based handoff path. For the native Windows installer and portable bundle, use [native-handoff.md](/c:/single-riders-comment-intelligence/docs/native-handoff.md).

## What teammates need

- Windows with Docker Desktop installed
- The zipped handoff bundle created from `scripts\package-handoff.bat`

They do not need Python, Node, PostgreSQL, or Redis installed locally.

## Run the app on a clean computer

1. Install Docker Desktop and open it once so the Docker engine is running.
2. Unzip the handoff bundle.
3. Double-click `scripts\start-handoff.bat`.
4. Wait for the launcher to:
   - start PostgreSQL, Redis, API, worker, and web containers
   - run database migrations automatically
   - open the in-app guide at `http://localhost:3000/guide`
5. Use the app at `http://localhost:3000`.
6. Double-click `scripts\stop-handoff.bat` when you are done.

If you need a clean reset later, run:

- `powershell -ExecutionPolicy Bypass -File .\scripts\stop-handoff.ps1 -ResetData`

## Create the handoff zip

From the repo root, run:

- `.\scripts\package-handoff.bat`

The script creates a timestamped zip in `dist\`. It excludes `.git`, virtual environments, caches, compiled output, and local databases.

## Get the TikTok JSON export

Use TikTok's official account data export flow:

1. Open TikTok.
2. Go to `Profile`.
3. Open `Menu`.
4. Open `Settings and privacy`.
5. Open `Account`.
6. Open `Download your data`.
7. When TikTok asks for file format, choose `JSON` because this app imports the JSON export directly.
8. Submit the request and wait for TikTok to prepare the file.
9. Download the export when TikTok marks it ready.

TikTok says the export can take a few days to prepare and is available to download for a limited time after it is ready. Official help page:

- https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/how-to-download-your-data

## What the app imports from TikTok

Phase 1 is intentionally narrow:

- approved: `Comment -> Comments -> CommentsList`
- optional supporting context: `Post -> Posts -> VideoList`
- ignored by default: direct messages, login history, device/IP history, and other sensitive account metadata

## Recommended handoff note

When you share the bundle, tell teammates:

- install Docker Desktop first
- run `scripts\start-handoff.bat`
- upload the TikTok JSON export on the `Imports` page
- open `Guide` in the sidebar if they need step-by-step help
