import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";

const workflowSteps = [
  "Upload a TikTok export on Imports and confirm the preview only includes approved sections such as comments and optional post metadata.",
  "Wait for processing so raw comments are normalized, classified, and grouped into signals.",
  "Open Dashboard to see what users care about most, which themes are rising, and whether confusion or safety concerns need attention.",
  "Open Audience Insights when you want a deeper read on MVP priorities, user-story alignment, and top videos driving useful feedback.",
  "Use Comments Explorer to inspect evidence behind any theme, filter by category or MVP area, and open the raw payload when context matters.",
  "Use Review Queue and Classifications to correct weak AI calls before they distort signal grouping or backlog decisions.",
  "Use Signals to review grouped requests, mark them reviewed, and export the strongest evidence to roadmap tooling.",
];

const glossary = [
  {
    term: "Primary Category",
    definition: "The main interpretation of a comment, such as feature request, safety concern, confusion, or praise.",
  },
  {
    term: "MVP Area",
    definition: "The product area most affected by the comment, such as matching, onboarding, messaging, moderation, or profiles.",
  },
  {
    term: "Signal",
    definition: "A grouped product insight created from multiple comments that point to the same repeated theme.",
  },
  {
    term: "Priority Score",
    definition: "A weighted score based on relevance, urgency, confidence, and evidence volume to help rank what deserves attention first.",
  },
  {
    term: "Momentum",
    definition: "The share of evidence that is recent, which helps identify whether a theme is rising right now or mostly historical.",
  },
  {
    term: "Needs Review",
    definition: "A flag showing the AI was not confident enough to let the comment flow through without a human decision.",
  },
];

const mvpThemes = [
  "Dating mode and friendship mode are both core launch stories, so audience feedback should be read through both lenses.",
  "Matching quality and filters matter because users want to find people with similar interests, age range, location, and park preferences.",
  "Profiles matter because the docs emphasize bios, photos, favorites, and self-expression as trust and matching inputs.",
  "Messaging matters because mutual matches are only useful if people can actually talk, unmatch, and manage conversations.",
  "Safety, reporting, moderation, and bot detection are high-priority launch requirements in both the user stories and beta plan.",
  "Account lifecycle matters because the docs call out login persistence, account deletion, and protection of user information.",
  "Beta onboarding matters because the beta plan specifically calls out explicit dating/friendship onboarding before launch.",
];

const scopeRules = [
  "Phase 1 uses comment feedback as the main source of insight.",
  "Optional post metadata can be used as supporting context for grouping comments by source video or post.",
  "Private DMs are ignored by default.",
  "Login history, device/IP history, and other sensitive account sections are out of scope for this workflow.",
  "If an export is missing video ids, the app still imports comments and labels that context clearly in the UI.",
];

const handoffSteps = [
  "Preferred path: use the native Windows package and double-click scripts/start-native.bat on the new computer.",
  "The native package bundles the API, web runtime, Node, and SQLite so the reviewer does not need Python, Node, Postgres, or Redis installed.",
  "Docker remains the fallback path if you prefer containers. In that case, install Docker Desktop and use scripts/start-handoff.bat instead.",
  "Wait for the browser to open the Guide page at localhost:3000 or 127.0.0.1:3000.",
  "Use the matching stop script when you are finished: stop-native for the native package or stop-handoff for Docker.",
];

const tiktokExportSteps = [
  "In TikTok, open Profile, then Menu, then Settings and privacy.",
  "Open Account and choose Download your data.",
  "When TikTok asks for file format, choose JSON so it matches this app's import flow.",
  "Submit the request and wait for TikTok to prepare the export.",
  "Download the file once TikTok marks it ready and upload it on the Imports page here.",
];

export default function GuidePage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="How To Use The App"
        description="A step-by-step guide for importing TikTok feedback, validating classifications, and turning audience comments into roadmap-ready MVP decisions."
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr,1fr]">
        <Card className="bg-gradient-to-br from-white via-white to-sand/55">
          <CardHeader>
            <div>
              <CardTitle>Step-By-Step Workflow</CardTitle>
              <CardDescription>The shortest path from a raw export file to a product decision the team can trust.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4">
              {workflowSteps.map((step, index) => (
                <li key={step} className="rounded-[1.75rem] bg-paper px-4 py-4 text-sm leading-6 text-ink">
                  <span className="mr-3 inline-flex h-8 w-8 items-center justify-center rounded-full bg-ink font-medium text-white">
                    {index + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Data Scope Rules</CardTitle>
              <CardDescription>What this tool uses from TikTok exports and what it intentionally ignores.</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {scopeRules.map((rule) => (
              <div key={rule} className="rounded-3xl bg-paper px-4 py-4 text-sm leading-6 text-ink">
                {rule}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Handoff Quick Start</CardTitle>
              <CardDescription>The fastest way to run the app on a new Windows computer without installing Python, Node, Postgres, or Redis.</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {handoffSteps.map((step) => (
              <div key={step} className="rounded-3xl bg-paper px-4 py-4 text-sm leading-6 text-ink">
                {step}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Get Your TikTok JSON</CardTitle>
              <CardDescription>Use TikTok&apos;s account data export, then upload the JSON file on the Imports page.</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {tiktokExportSteps.map((step) => (
              <div key={step} className="rounded-3xl bg-paper px-4 py-4 text-sm leading-6 text-ink">
                {step}
              </div>
            ))}
            <a
              href="https://support.tiktok.com/en/account-and-privacy/personalized-ads-and-data/how-to-download-your-data"
              target="_blank"
              rel="noreferrer"
              className="inline-flex text-sm font-medium text-spruce underline underline-offset-4"
            >
              Official TikTok help page
            </a>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Glossary</CardTitle>
              <CardDescription>Quick definitions for the terms you will see across the dashboard, explorer, and review screens.</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {glossary.map((item) => (
              <div key={item.term} className="rounded-3xl border border-ink/10 bg-white px-4 py-4">
                <p className="font-medium text-ink">{item.term}</p>
                <p className="mt-2 text-sm leading-6 text-slate">{item.definition}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>MVP Themes From The Product Docs</CardTitle>
              <CardDescription>These are the major themes extracted from the MVP, user-story, and beta onboarding documents.</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {mvpThemes.map((theme) => (
              <div key={theme} className="rounded-3xl bg-paper px-4 py-4 text-sm leading-6 text-ink">
                {theme}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
