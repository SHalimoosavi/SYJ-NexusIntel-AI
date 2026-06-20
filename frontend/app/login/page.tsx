"use client";

import { useState } from "react";

const API_BASE =
"https://syj-nexusintel-ai-production.up.railway.app";

export default function LoginPage() {
const [email, setEmail] =
useState("");

const [password, setPassword] =
useState("");

const [loading, setLoading] =
useState(false);

async function handleLogin(
e: React.FormEvent
) {
e.preventDefault();

alert(
  `EMAIL=[${email}]

PASSWORD=[${password}]`
);

setLoading(true);

try {
  const response = await fetch(
    `${API_BASE}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        email: email.trim(),
        password:
          password.trim(),
      }),
    }
  );

  const data =
    await response.json();

  alert(
    JSON.stringify(
      data,
      null,
      2
    )
  );

  if (
    !response.ok ||
    !data.access_token
  ) {
    setLoading(false);
    return;
  }

  localStorage.setItem(
    "token",
    data.access_token
  );

  alert(
    "TOKEN SAVED - REDIRECTING"
  );

  window.location.href =
    "/dashboard";
} catch (error) {
  console.error(error);

  alert(
    "FETCH FAILED"
  );
}

setLoading(false);

}

return (
<main className="min-h-screen gradient-bg flex items-center justify-center">
<form
onSubmit={handleLogin}
className="glass p-8 rounded-3xl w-full max-w-md"
>
<h1 className="text-4xl font-bold mb-6">
Login
</h1>

    <input
      type="email"
      placeholder="Email"
      value={email}
      onChange={(e) =>
        setEmail(
          e.target.value
        )
      }
      className="w-full p-3 rounded-xl bg-black/20 mb-4"
    />

    <input
      type="password"
      placeholder="Password"
      value={password}
      onChange={(e) =>
        setPassword(
          e.target.value
        )
      }
      className="w-full p-3 rounded-xl bg-black/20 mb-6"
    />

    <button
      type="submit"
      disabled={loading}
      className="w-full bg-emerald-500 text-black py-3 rounded-xl font-bold"
    >
      {loading
        ? "Logging in..."
        : "Login"}
    </button>
  </form>
</main>

);
}
