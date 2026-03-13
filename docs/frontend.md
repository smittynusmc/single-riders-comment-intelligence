# Frontend

## Goal

The web app is an internal admin dashboard for exploring comments, reviewing AI output, and exporting strong signals into backlog systems.

## Page map

### `/dashboard`

- total comments
- comments this week
- needs review count
- total signals
- trend chart
- top repeated requests
- safety snapshot

### `/imports`

- drag-and-drop JSON-first upload form
- CSV fallback upload support
- file preview with detected format and shape
- sample fields, missing fields, and parse warnings
- import history table with source format and run status

### `/comments`

- keyword, video, category, MVP area, sentiment, and review filters
- TanStack table of raw and normalized records
- detail drawer for individual comment inspection

### `/classifications`

- AI output review table
- approve action
- override modal
- false-positive action

### `/signals`

- signal cards with grouped evidence
- priority, evidence count, sample comments
- reviewed and archive actions
- GitHub and Trello export placeholders

### `/review`

- filtered human review queue based on `needs_human_review=true`

## Shared contracts

`packages/shared-types` mirrors the backend response shapes the dashboard depends on. That keeps client wrappers and page components aligned without scattering ad hoc interfaces across the UI.

## UI direction

The dashboard uses a warm internal-tool visual system rather than a generic neutral admin template:

- `Space Grotesk` for display typography
- `IBM Plex Sans` for dense operational content
- sand, ink, spruce, coral, and gold color tokens
- cards and soft gradients instead of flat default panes

## Future additions

- auth and team roles
- saved filters and views
- signal merge workflow
- docs export action in the UI
- richer charts and weekly digest pages
