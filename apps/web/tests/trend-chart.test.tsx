import { render, screen } from "@testing-library/react";

import { TrendChart } from "@/components/dashboard/trend-chart";

describe("TrendChart", () => {
  it("renders an empty state when no trend data is available", () => {
    render(<TrendChart points={[]} />);

    expect(screen.getByText("Trend data is not available yet for this deployment. The rest of the dashboard is still using live shared data.")).toBeInTheDocument();
  });
});
