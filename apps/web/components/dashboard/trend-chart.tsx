"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { TrendPoint } from "@single-riders/shared-types";

export function TrendChart({ points }: { points: TrendPoint[] }) {
  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Weekly Trend Summary</CardTitle>
          <CardDescription>Comment volume against human review pressure over the last two weeks.</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="h-[340px]">
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
            <XAxis dataKey="bucket" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} />
            <Tooltip />
            <Area type="monotone" dataKey="comments" stroke="#2c5545" fill="url(#commentsFill)" strokeWidth={3} />
            <Area type="monotone" dataKey="review_queue" stroke="#cf5f4f" fill="url(#reviewFill)" strokeWidth={3} />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
