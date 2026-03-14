# MVP Audience Insights

## Purpose

This module turns TikTok feedback into internal product guidance for the Single Riders MVP. It extends the existing imports, comments, classifications, review, and signals workflow with a more opinionated question:

What do users care about most before launch?

## Source Product Documents

The audience insight themes in the app were aligned to these local product docs:

- `MVP.docx`
- `Single Rider User Story & App Plan.docx`
- `Single_Riders_Beta_Onboarding_Plan.docx`
- `User Stories-Single Riders.docx`

Those docs were distilled into a practical theme set for the admin dashboard rather than copied verbatim into the product.

## MVP Themes Used In The App

The current audience-insights layer tracks feedback against these story-driven themes:

- Dating mode demand
- Friendship mode demand
- Park-day coordination
- Matching and filters
- Profiles and self-expression
- Messaging and chat
- Safety and moderation
- Beta access and onboarding
- Account trust and lifecycle
- Positive validation

These themes are intentionally broader than one comment or one signal so they can help with roadmap decisions, not just content review.

## Product Story Alignment

The current UI and ranking logic are designed to reflect recurring MVP stories from the product docs:

- Users want a clear split between dating intent and friendship intent
- Users want stronger matching quality and filters
- Users want richer profiles that feel expressive and trustworthy
- Users expect messaging after a mutual match
- Users care deeply about safety, reporting, moderation, and fake-profile prevention
- Users want confidence around login persistence, account deletion, and protection of their information
- Beta onboarding needs to be understandable before launch

## Audience Ranking Logic

The "What users care about most" section uses a weighted score based on:

- evidence count
- model relevance score
- urgency score
- confidence score
- recent momentum
- extra boosts for safety and confusion themes

This is not a replacement for product judgment. It is a prioritization aid.

## How To Use The Module

1. Upload a TikTok export on the Imports page.
2. Confirm the preview only includes approved sections.
3. Let the processing pipeline normalize, classify, and group comments.
4. Open Dashboard or Audience Insights to see ranked MVP themes.
5. Use Comments Explorer to inspect evidence and raw payloads.
6. Use Review Queue and Classifications to correct weak AI calls.
7. Use Signals to review grouped requests and export the strongest ones to backlog tooling.

## Data Scope And Privacy

Phase 1 keeps the data scope intentionally narrow.

Approved input:

- comment exports
- portability comment wrappers
- optional post metadata for context

Ignored by default:

- direct messages
- login history
- device and IP history
- other sensitive account-level metadata

This keeps the tool focused on product feedback rather than surveillance-style account data.

Do not use login history, device or IP history, or private DM history in dashboard counts, date-range calculations, or product insight summaries.

## Date Range Audit And Root Cause

The uploaded TikTok portability export used for the March-range audit was not March-only. It contained 84 comments spanning July 8, 2025 through March 7, 2026 across 9 distinct months.

The audit verified the same date span across the core processing layers:

- JSON parsing: 84 comments, July 2025 to March 2026, 9 months
- raw comments persisted: 84 comments, same span
- normalized comments: 84 comments, same span
- classified comments: 84 comments, same span

The root cause was not the parser, import service, normalization, or classification pipeline.

The actual narrowing happened in the dashboard read layer:

- the trend query was previously hard-scoped to the last 14 days
- the UI did not show the imported date span clearly
- the comments explorer had a row limit but no clear active-range/filter banner

The fix now does four things:

- trends use the full imported span, switching to monthly buckets for longer ranges
- import preview shows total comments, earliest date, latest date, and months represented
- dashboard and comments pages show visible date coverage and active filter range
- comments explorer shows active filter pills and an empty state that explains when filters may be hiding older data

## UX Guidance

This is an internal decision tool for founders, product, marketing, and UX.

The interface should optimize for:

- clarity
- speed
- evidence visibility
- insight discovery
- safe human override

It should not behave like a public social dashboard or a vanity analytics tool.
