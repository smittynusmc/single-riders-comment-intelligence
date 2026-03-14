const SESSION_COOKIE_NAME = "sci_session";
const SESSION_DURATION_SECONDS = 60 * 60 * 12;
const encoder = new TextEncoder();
const decoder = new TextDecoder();

export interface AuthSession {
  email: string;
  display_name: string;
  expires_at: string;
}

interface SessionPayload extends AuthSession {
  exp: number;
}

function getSessionSecret() {
  const secret = process.env.AUTH_SESSION_SECRET;
  if (!secret) {
    throw new Error("AUTH_SESSION_SECRET is required for hosted sessions.");
  }
  return secret;
}

function getCryptoApi() {
  const cryptoApi = globalThis.crypto;
  if (!cryptoApi?.subtle) {
    throw new Error("Web Crypto is required for hosted sessions.");
  }
  return cryptoApi;
}

function toBase64(value: Uint8Array) {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(value).toString("base64");
  }

  let binary = "";
  value.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function fromBase64(value: string) {
  if (typeof Buffer !== "undefined") {
    return new Uint8Array(Buffer.from(value, "base64"));
  }

  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function toBase64Url(value: Uint8Array) {
  return toBase64(value).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/u, "");
}

function fromBase64Url(value: string) {
  const normalized = value.replaceAll("-", "+").replaceAll("_", "/");
  const paddingLength = (4 - (normalized.length % 4 || 4)) % 4;
  return fromBase64(`${normalized}${"=".repeat(paddingLength)}`);
}

async function importSigningKey() {
  return getCryptoApi().subtle.importKey(
    "raw",
    encoder.encode(getSessionSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

async function signPayloadSegment(payloadSegment: string) {
  const key = await importSigningKey();
  const signature = await getCryptoApi().subtle.sign("HMAC", key, encoder.encode(payloadSegment));
  return toBase64Url(new Uint8Array(signature));
}

async function verifyPayloadSignature(payloadSegment: string, signatureSegment: string) {
  const key = await importSigningKey();
  return getCryptoApi().subtle.verify(
    "HMAC",
    key,
    fromBase64Url(signatureSegment),
    encoder.encode(payloadSegment),
  );
}

function decodePayload(payloadSegment: string): SessionPayload | null {
  try {
    const payload = JSON.parse(decoder.decode(fromBase64Url(payloadSegment))) as Partial<SessionPayload>;
    if (
      typeof payload.email !== "string" ||
      typeof payload.display_name !== "string" ||
      typeof payload.expires_at !== "string" ||
      typeof payload.exp !== "number"
    ) {
      return null;
    }
    return payload as SessionPayload;
  } catch {
    return null;
  }
}

export function normalizeEmail(email: string) {
  return email.trim().toLowerCase();
}

export function parseAllowedUserEmails(rawValue = process.env.AUTH_ALLOWED_USER_EMAILS ?? "") {
  return rawValue
    .split(",")
    .map((item) => normalizeEmail(item))
    .filter(Boolean);
}

export function isAllowedUserEmail(email: string) {
  return parseAllowedUserEmails().includes(normalizeEmail(email));
}

export function getSharedAccessCode() {
  const code = process.env.AUTH_SHARED_ACCESS_CODE;
  if (!code) {
    throw new Error("AUTH_SHARED_ACCESS_CODE is required for hosted login.");
  }
  return code;
}

export function getSessionCookieName() {
  return SESSION_COOKIE_NAME;
}

export function inferDisplayName(email: string) {
  const localPart = normalizeEmail(email).split("@")[0] ?? email;
  return localPart
    .split(/[._-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export async function createSessionToken(email: string) {
  const normalizedEmail = normalizeEmail(email);
  const displayName = inferDisplayName(normalizedEmail);
  const exp = Math.floor(Date.now() / 1000) + SESSION_DURATION_SECONDS;
  const expiresAt = new Date(exp * 1000).toISOString();
  const payloadSegment = toBase64Url(
    encoder.encode(
      JSON.stringify({
        email: normalizedEmail,
        display_name: displayName,
        expires_at: expiresAt,
        exp,
      } satisfies SessionPayload),
    ),
  );
  const signatureSegment = await signPayloadSegment(payloadSegment);

  return {
    token: `${payloadSegment}.${signatureSegment}`,
    session: {
      email: normalizedEmail,
      display_name: displayName,
      expires_at: expiresAt,
    } satisfies AuthSession,
  };
}

export async function verifySessionToken(token: string): Promise<AuthSession | null> {
  const [payloadSegment, signatureSegment] = token.split(".");
  if (!payloadSegment || !signatureSegment) {
    return null;
  }

  const isValid = await verifyPayloadSignature(payloadSegment, signatureSegment);
  if (!isValid) {
    return null;
  }

  const payload = decodePayload(payloadSegment);
  if (!payload || payload.exp <= Math.floor(Date.now() / 1000)) {
    return null;
  }

  return {
    email: normalizeEmail(payload.email),
    display_name: payload.display_name,
    expires_at: payload.expires_at,
  };
}
