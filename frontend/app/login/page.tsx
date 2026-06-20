"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(
    e: React.FormEvent
  ) {
    e.preventDefault();

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
            email,
            password,
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
        throw new Error(
          "Login failed"
        );
      }

      localStorage.setItem(
        "token",
        data.access_token
      );

      router.push(
        "/dashboard"
      );
    } catch (error: any) {
      alert(
        "ERROR:\n\n" +
          error?.message
      );

      console.error(error);
    }

    setLoading(false);
  }

  return (
    <main className="min-h-screen gradient-bg flex items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="glass p-8 rounded-3xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-6">
          Login
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full p-3 rounded-xl bg-black/20 mb-6"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <button
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
