const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://syj-nexusintel-ai-production.up.railway.app";

/**
 * Browser authentication is held in an HttpOnly cookie scoped to the API.
 * JavaScript must never read, persist, or attach the session JWT itself.
 */
export function authHeaders() {
  return { "Content-Type": "application/json" };
}

export async function logout() {
  try {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include",
      cache: "no-store",
    });
  } finally {
    window.location.assign("/login");
  }
}

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Invalid credentials");
  }
  return data;
}

export async function acceptInvitation(
  full_name: string,
  email: string,
  password: string,
  invitation_token: string
) {
  const response = await fetch(`${API_BASE}/invitations/accept`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      full_name,
      email,
      password,
      invitation_token,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Invitation acceptance failed");
  }
  return data;
}
