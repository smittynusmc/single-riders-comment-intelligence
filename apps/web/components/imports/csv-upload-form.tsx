"use client";

import { useId, useState, useTransition } from "react";

import type { ImportFormat, ImportPreview } from "@single-riders/shared-types";

import { previewImport } from "@/lib/api/imports";
import { apiUpload } from "@/lib/api/client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

function inferImportEndpoint(fileName: string, detectedFormat?: ImportFormat) {
  if (detectedFormat === "csv" || fileName.toLowerCase().endsWith(".csv")) {
    return "/imports/csv";
  }
  return "/imports/json";
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}

function PreviewList({ items }: { items: string[] }) {
  if (!items.length) {
    return <p className="text-sm text-slate">None</p>;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className="rounded-full bg-paper px-3 py-1 text-xs text-slate shadow-sm">
          {item}
        </span>
      ))}
    </div>
  );
}

export function ImportUploadForm() {
  const inputId = useId();
  const [message, setMessage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [isPreviewPending, startPreviewTransition] = useTransition();
  const [isImportPending, startImportTransition] = useTransition();

  function handleFile(file: File | null) {
    setSelectedFile(file);
    setPreview(null);
    setMessage(null);

    if (!file) {
      return;
    }

    startPreviewTransition(async () => {
      try {
        const formData = new FormData();
        formData.set("file", file);
        const result = await previewImport(formData);
        setPreview(result);
      } catch (error) {
        setPreview(null);
        setMessage(error instanceof Error ? error.message : "Could not preview the file.");
      }
    });
  }

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Export Upload</CardTitle>
          <CardDescription>
            TikTok JSON exports are the primary MVP input. CSV remains available for cleaned manual datasets.
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            if (!selectedFile) {
              setMessage("Choose a JSON or CSV export file first.");
              return;
            }

            startImportTransition(async () => {
              try {
                const formData = new FormData();
                formData.set("file", selectedFile);
                const endpoint = inferImportEndpoint(selectedFile.name, preview?.detected_format);
                const response = await apiUpload<{ ingestion_run_id: string }>(endpoint, formData);
                setMessage(`Import queued for run ${response.ingestion_run_id}.`);
                window.location.reload();
              } catch (error) {
                setMessage(error instanceof Error ? error.message : "Upload failed.");
              }
            });
          }}
        >
          <label
            htmlFor={inputId}
            className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-ink/25 bg-sand/60 px-6 py-8 text-center transition hover:border-ink/40 hover:bg-sand"
            onDragOver={(event) => {
              event.preventDefault();
            }}
            onDrop={(event) => {
              event.preventDefault();
              handleFile(event.dataTransfer.files.item(0));
            }}
          >
            <span className="text-base font-semibold text-ink">
              {selectedFile ? selectedFile.name : "Drop a TikTok JSON export or CSV here"}
            </span>
            <span className="mt-2 text-sm text-slate">
              {selectedFile ? "Preview updates automatically after selection." : "Or click to browse local files."}
            </span>
          </label>
          <Input
            id={inputId}
            name="file"
            type="file"
            accept=".json,.csv"
            className="hidden"
            onChange={(event) => handleFile(event.target.files?.item(0) ?? null)}
          />

          <div className="flex flex-wrap items-center gap-3 text-sm text-slate">
            <span className="rounded-full bg-paper px-3 py-1 shadow-sm">JSON-first</span>
            <span className="rounded-full bg-paper px-3 py-1 shadow-sm">CSV convenience</span>
            <span className="rounded-full bg-paper px-3 py-1 shadow-sm">No OAuth comment sync</span>
          </div>

          {isPreviewPending ? <p className="text-sm text-slate">Parsing file summary...</p> : null}

          {preview ? (
            <div className="space-y-4 rounded-3xl border border-paper bg-cream px-5 py-4">
              <div className="grid gap-3 md:grid-cols-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate">Detected Format</p>
                  <p className="mt-1 text-sm font-semibold text-ink">{formatLabel(preview.detected_format)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate">Detected Shape</p>
                  <p className="mt-1 text-sm font-semibold text-ink">{preview.detected_shape ?? "unknown"}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate">Parsed Comments</p>
                  <p className="mt-1 text-sm font-semibold text-ink">{preview.comment_count}</p>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.2em] text-slate">Sample Fields</p>
                <PreviewList items={preview.sample_fields} />
              </div>

              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.2em] text-slate">Missing Canonical Fields</p>
                <PreviewList items={preview.missing_fields} />
              </div>

              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.2em] text-slate">Parse Warnings</p>
                <PreviewList items={preview.parse_warnings} />
              </div>

              {preview.sample_comments.length ? (
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate">Sample Comments</p>
                  <div className="space-y-2">
                    {preview.sample_comments.map((comment) => (
                      <div key={comment.source_comment_id} className="rounded-2xl bg-paper px-4 py-3 text-sm shadow-sm">
                        <p className="font-medium text-ink">{comment.comment_text}</p>
                        <p className="mt-1 text-xs text-slate">
                          {comment.author_handle ?? "unknown author"} · {comment.source_video_id ?? "no video id"} · {comment.source_comment_id}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}

          <Button type="submit" disabled={!selectedFile || isImportPending || isPreviewPending}>
            {isImportPending ? "Uploading..." : "Import File"}
          </Button>
          {message ? <p className="text-sm text-slate">{message}</p> : null}
        </form>
      </CardContent>
    </Card>
  );
}
