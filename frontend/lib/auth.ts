const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

/* =========================
   TOKEN HELPERS
========================= */

export function getToken(): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const match = document.cookie.match(
    /(^| )token=([^;]+)/
  );

  return match ? match[2] : null;
}

export function authHeaders() {
  const token = getToken();

  return {
    "Content-Type": "application/json",
    ...(token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {}),
  };
}

export function saveToken(
  token: string
) {
  document.cookie =
    `token=${token}; path=/; max-age=86400`;
}

export function logout() {
  document.cookie =
    "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";

  window.location.href = "/login";
}

/* =========================
   LOGIN
========================= */

export async function login(
  email: string,
  password: string
) {
  const response = await fetch(
    `${API_BASE}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Invalid credentials"
    );
  }

  return data;
}

/* =========================
   INVITATION ACCEPTANCE
========================= */

export async function acceptInvitation(
  full_name: string,
  email: string,
  password: string,
  invitation_token: string
) {
  const response = await fetch(
    `${API_BASE}/invitations/accept`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        full_name,
        email,
        password,
        invitation_token,
      }),
    }
  );

  const data =
    await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Invitation acceptance failed"
    );
  }

  return data;
}
