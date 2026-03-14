import { render, screen } from "@testing-library/react";

import GuidePage from "@/app/guide/page";

describe("GuidePage", () => {
  it("renders the workflow and glossary content", async () => {
    render(await GuidePage());

    expect(screen.getByText("How To Use The App")).toBeInTheDocument();
    expect(screen.getByText("Step-By-Step Workflow")).toBeInTheDocument();
    expect(screen.getByText("Handoff Quick Start")).toBeInTheDocument();
    expect(screen.getByText("Get Your TikTok JSON")).toBeInTheDocument();
    expect(screen.getByText(/Preferred path: use the native Windows package/i)).toBeInTheDocument();
    expect(screen.getByText("Glossary")).toBeInTheDocument();
    expect(screen.getByText("Data Scope Rules")).toBeInTheDocument();
  });
});
