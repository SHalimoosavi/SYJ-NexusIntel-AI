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

    setLoading(true);

    const targetUrl = `${API_BASE}/auth/login`;

    alert(
      "DEBUG: About to fetch\nURL: " +
      targetUrl +
      "\nEmail: " +
      email
    );

    try {
      const response =
        await fetch(
          targetUrl,
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

      alert(
        "DEBUG: Fetch resolved\nStatus: " +
        response.status +
        "\nOK: " +
        response.ok
      );

      const data =
        await response.json();

      alert(
        "DEBUG: Response body\n" +
        JSON.stringify(data, null, 2)
      );

      if (
        !response.ok ||
        !data.access_token
      ) {
        alert(
          JSON.stringify(
            data,
            null,
            2
          )
        );

        setLoading(false);
        return;
      }

      document.cookie =
        `token=${data.access_token}; path=/; max-age=86400`;

      window.location.href =
        "/dashboard";
    } catch (error) {
      alert(
        "DEBUG: Fetch threw an error\nName: " +
        (error instanceof Error ? error.name : "unknown") +
        "\nMessage: " +
        (error instanceof Error ? error.message : String(error)) +
        "\nStack: " +
        (error instanceof Error ? error.stack : "no stack")
      );

      console.error(error);

      alert(
        "Unable to connect to API"
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
