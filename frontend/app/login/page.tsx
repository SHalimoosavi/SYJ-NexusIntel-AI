"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();

  const [email,setEmail] =
    useState("");

  const [password,setPassword] =
    useState("");

  const [loading,setLoading] =
    useState(false);

  async function handleLogin(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setLoading(true);

    try {
      const result =
        await login(
          email,
          password
        );

      localStorage.setItem(
        "token",
        result.access_token
      );

      router.push(
        "/dashboard"
      );
    } catch {
      alert(
        "Invalid login"
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
        <h1 className="text-3xl font-bold mb-6">
          Login
        </h1>

        <input
          type="email"
          placeholder="Email"
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
          value={email}
          onChange={(e)=>
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
          onChange={(e)=>
            setPassword(
              e.target.value
            )
          }
        />

        <button
          disabled={loading}
          className="w-full bg-emerald-500 text-black py-3 rounded-xl font-bold"
        >
          {
            loading
            ? "Logging in..."
            : "Login"
          }
        </button>
      </form>
    </main>
  );
}
