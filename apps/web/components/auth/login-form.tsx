"use client";

import { useMemo, useState, useTransition } from "react";
import type { Route } from "next";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [accessCode, setAccessCode] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const nextPath = useMemo(() => searchParams.get("next") || "/dashboard", [searchParams]);

  return (
    <Card className="mx-auto max-w-xl border-white/70 bg-white/80 shadow-panel backdrop-blur">
      <CardHeader>
        <div>
          <CardTitle>Internal Login</CardTitle>
          <CardDescription>
            Hosted access is restricted to the allowlisted Single Riders team. Use your approved email and the shared internal access code.
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            setMessage(null);

            startTransition(async () => {
              const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, accessCode }),
              });

              const payload = (await response.json().catch(() => ({}))) as { detail?: string };
              if (!response.ok) {
                setMessage(payload.detail ?? "Login failed.");
                return;
              }

              const destination = (nextPath.startsWith("/") ? nextPath : "/dashboard") as Route;
              router.replace(destination);
              router.refresh();
            });
          }}
        >
          <div className="space-y-2">
            <label className="text-sm font-medium text-ink" htmlFor="email">
              Email
            </label>
            <Input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@company.com" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-ink" htmlFor="access-code">
              Shared Access Code
            </label>
            <Input
              id="access-code"
              type="password"
              value={accessCode}
              onChange={(event) => setAccessCode(event.target.value)}
              placeholder="Internal team code"
            />
          </div>
          <div className="rounded-2xl bg-paper px-4 py-3 text-sm text-slate">
            Adam, Joe, Kiele, and Jason should each use their own allowlisted email address. The app only admits emails present in the deployment allowlist.
          </div>
          <Button type="submit" disabled={isPending}>
            {isPending ? "Signing in..." : "Sign In"}
          </Button>
          {message ? <p className="text-sm text-rose-700">{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
