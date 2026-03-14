"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { TrendPoint } from "@single-riders/shared-types";

function inferGranularity(points: TrendPoint[]) {
  return points.some((point) => point.bucket.length === 7) ? "month" : "day";
}

function formatBucket(bucket: string, granularity: "month" | "day") {
  if (granularity === "month") {
    const [year, month] = bucket.split("-").map(Number);
    return new Intl.DateTimeFormat("en-US", { month: "short", year: "numeric" }).format(new Date(Date.UTC(year, month - 1, 1)));
  }

  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(`${bucket}T00:00:00Z`));
}

export function TrendChart({ points }: { points: TrendPoint[] }) {
  const granularity = inferGranularity(points);

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>{granularity === "month" ? "Monthly Trend Summary" : "Daily Trend Summary"}</CardTitle>
          <CardDescription>Comment volume and review pressure across the full imported date span.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="h-[340px]">
        {points.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-[rgba(17,32,49,0.16)] bg-[rgba(255,255,255,0.66)] px-6 text-center text-sm text-[rgba(17,32,49,0.72)]">
            Trend data is not available yet for this deployment. The rest of the dashboard is still using live shared data.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={points} margin={{ left: 0, right: 0, top: 8, bottom: 0 }}>
              <defs>
                <linearGradient id="commentsFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#2c5545" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="#2c5545" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="reviewFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#cf5f4f" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#cf5f4f" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(17,32,49,0.08)" vertical={false} />
              <XAxis dataKey="bucket" tickLine={false} axisLine={false} tickFormatter={(value) => formatBucket(String(value), granularity)} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip labelFormatter={(value) => formatBucket(String(value), granularity)} />
              <Area type="monotone" dataKey="comments" stroke="#2c5545" fill="url(#commentsFill)" strokeWidth={3} />
              <Area type="monotone" dataKey="review_queue" stroke="#cf5f4f" fill="url(#reviewFill)" strokeWidth={3} />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
