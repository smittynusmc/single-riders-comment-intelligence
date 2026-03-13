"use client";

import { useState, useTransition } from "react";

import { apiUpload } from "@/lib/api/client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function CsvUploadForm() {
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>CSV Upload</CardTitle>
          <CardDescription>Primary MVP ingestion path. Upload TikTok comment exports or structurally compatible third-party CSV files.</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const formData = new FormData(form);
            startTransition(async () => {
              try {
                const response = await apiUpload<{ ingestion_run_id: string }>("/imports/csv", formData);
                setMessage(`Import queued for run ${response.ingestion_run_id}.`);
                window.location.reload();
              } catch (error) {
                setMessage(error instanceof Error ? error.message : "Upload failed.");
              }
            });
          }}
        >
          <div>
            <label className="mb-2 block text-sm font-medium text-ink" htmlFor="file">
              Comment CSV
            </label>
            <Input id="file" name="file" type="file" accept=".csv" required />
          </div>
          <Button type="submit" disabled={isPending}>
            {isPending ? "Uploading..." : "Upload CSV"}
          </Button>
          {message ? <p className="text-sm text-slate">{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
