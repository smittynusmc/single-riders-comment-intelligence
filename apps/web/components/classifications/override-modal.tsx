"use client";

import { useState, useTransition } from "react";
import type { MvpArea, PrimaryCategory } from "@single-riders/shared-types";

import { updateClassification } from "@/lib/api/classifications";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

const categories: PrimaryCategory[] = [
  "feature_request",
  "bug_or_quality",
  "safety_or_trust",
  "moderation_or_bot",
  "social_coordination",
  "confusion_or_onboarding",
  "praise_or_delight",
  "pricing_or_value",
  "other",
];

const mvpAreas: MvpArea[] = [
  "matching",
  "meetups",
  "safety",
  "onboarding",
  "profiles",
  "moderation",
  "messaging",
  "monetization",
  "passholders",
  "community",
  "operations",
  "other",
];

export function OverrideModal({ classificationId }: { classificationId: string }) {
  const [note, setNote] = useState("");
  const [category, setCategory] = useState<PrimaryCategory | "">("");
  const [mvpArea, setMvpArea] = useState<MvpArea | "">("");
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="secondary">Override</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Override Classification</DialogTitle>
        <DialogDescription>Correct category, MVP area, or leave a reviewer note for downstream signal quality.</DialogDescription>
        <div className="mt-6 space-y-4">
          <select className="h-11 w-full rounded-2xl border border-ink/10 px-4 text-sm" value={category} onChange={(event) => setCategory(event.target.value as PrimaryCategory | "")}>
            <option value="">Keep AI category</option>
            {categories.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <select className="h-11 w-full rounded-2xl border border-ink/10 px-4 text-sm" value={mvpArea} onChange={(event) => setMvpArea(event.target.value as MvpArea | "")}>
            <option value="">Keep AI MVP area</option>
            {mvpAreas.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <Input placeholder="Reviewer note" value={note} onChange={(event) => setNote(event.target.value)} />
          <div className="flex items-center gap-3">
            <Button
              disabled={isPending}
              onClick={() => {
                startTransition(async () => {
                  try {
                    await updateClassification(classificationId, {
                      review_status: "approved",
                      reviewer_note: note || undefined,
                      override_primary_category: category || undefined,
                      override_mvp_area: mvpArea || undefined,
                    });
                    setMessage("Classification updated.");
                    window.location.reload();
                  } catch (error) {
                    setMessage(error instanceof Error ? error.message : "Update failed.");
                  }
                });
              }}
            >
              {isPending ? "Saving..." : "Save Override"}
            </Button>
            {message ? <span className="text-sm text-slate">{message}</span> : null}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
