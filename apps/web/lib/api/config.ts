const LOCAL_API_FALLBACK = "http://localhost:8000";

export function getServerApiBaseUrl() {
  return process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? LOCAL_API_FALLBACK;
}

export function getInternalApiToken() {
  return process.env.INTERNAL_API_TOKEN ?? "";
}

export function getBrowserApiPrefix() {
  return "/api/proxy";
}
