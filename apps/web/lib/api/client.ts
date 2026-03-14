import { getBrowserApiPrefix, getInternalApiToken, getServerApiBaseUrl } from "@/lib/api/config";

const API_TIMEOUT_MS = 8000;

const fallbackApiBaseUrl = typeof window === "undefined" ? getServerApiBaseUrl() : getBrowserApiPrefix();

function buildUrl(path: string) {
  return `${fallbackApiBaseUrl}${path}`;
}

function buildHeaders(initHeaders?: HeadersInit) {
  const headers = new Headers(initHeaders);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (typeof window === "undefined") {
    const internalApiToken = getInternalApiToken();
    if (internalApiToken) {
      headers.set("x-internal-api-token", internalApiToken);
    }
  }
  return headers;
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(buildUrl(path), {
      cache: "no-store",
      ...init,
      signal: controller.signal,
      headers: buildHeaders(init?.headers),
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`API request timed out for ${path}. Make sure the backend is running on ${fallbackApiBaseUrl}.`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw new Error(`API request failed for ${path}: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS * 2);

  let response: Response;
  try {
    response = await fetch(buildUrl(path), {
      method: "POST",
      body: formData,
      signal: controller.signal,
      headers: typeof window === "undefined" && getInternalApiToken() ? { "x-internal-api-token": getInternalApiToken() } : undefined,
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`Upload timed out for ${path}. Make sure the backend is running on ${fallbackApiBaseUrl}.`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw new Error(`Upload failed for ${path}: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function buildQuery(params: Record<string, string | number | boolean | undefined | null>) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    query.set(key, String(value));
  });

  const serialized = query.toString();
  return serialized ? `?${serialized}` : "";
}
