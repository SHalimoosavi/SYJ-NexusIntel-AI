const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

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
