const API_TIMEOUT_MS = 8000;

const fallbackApiBaseUrl =
  typeof window === "undefined"
    ? process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
    : process.env.NEXT_PUBLIC_API_BASE_URL ?? process.env.API_BASE_URL ?? "http://localhost:8000";

function buildUrl(path: string) {
  return `${fallbackApiBaseUrl}${path}`;
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
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
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
