const configuredApiBase = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!configuredApiBase) {
  throw new Error("NEXT_PUBLIC_API_BASE_URL must be configured at build time");
}

export const API_BASE = configuredApiBase.replace(/\/+$/, "");
