const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

export function getToken() {
  if (typeof document === "undefined") {
    return null;
  }

  const match = document.cookie.match(
    /(^| )token=([^;]+)/
  );

  return match
    ? match[2]
    : null;
}

export function authHeaders() {
  const token = getToken();

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

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

  if (!response.ok) {
    throw new Error(
      "Invalid credentials"
    );
  }

  return response.json();
}

export async function register(
  full_name: string,
  email: string,
  password: string
) {
  const response = await fetch(
    `${API_BASE}/auth/register`,
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
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      "Registration failed"
    );
  }

  return response.json();
}
