"use client";

import { useState, useTransition } from "react";
import type { Signal } from "@single-riders/shared-types";

import { exportSignal, updateSignal } from "@/lib/api/signals";
import { Button } from "@/components/ui/button";

export function SignalExportActions({ signal }: { signal: Signal }) {
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button
        variant="secondary"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            const response = await updateSignal(signal.id, { status: "reviewed", reviewed_by: "internal_user" });
            setMessage(`Signal marked ${response.status}.`);
            window.location.reload();
          });
        }}
      >
        Mark Reviewed
      </Button>
      <Button
        variant="secondary"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            const response = await exportSignal(signal.id, "github");
            setMessage(response.reference ?? "GitHub export placeholder created.");
          });
        }}
      >
        Export GitHub
      </Button>
      <Button
        variant="secondary"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            const response = await exportSignal(signal.id, "trello");
            setMessage(response.reference ?? "Trello export placeholder created.");
          });
        }}
      >
        Export Trello
      </Button>
      <Button
        variant="ghost"
        disabled={isPending}
        onClick={() => {
          startTransition(async () => {
            const response = await updateSignal(signal.id, { status: "archived" });
            setMessage(`Signal marked ${response.status}.`);
            window.location.reload();
          });
        }}
      >
        Archive
      </Button>
      <Button variant="ghost" disabled>
        Merge Placeholder
      </Button>
      {message ? <span className="text-sm text-slate">{message}</span> : null}
    </div>
  );
}
