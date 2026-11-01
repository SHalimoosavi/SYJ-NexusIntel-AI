"use client";

import { useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://syj-nexusintel-ai-production.up.railway.app";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
        cache: "no-store",
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success) {
        setError(typeof data.detail === "string" ? data.detail : "Unable to sign in. Check your credentials.");
        return;
      }
      window.location.assign("/dashboard");
    } catch {
      setError("Unable to connect to the authentication service.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen gradient-bg flex items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="glass p-8 rounded-3xl w-full max-w-md"
      >
        <h1 className="text-4xl font-bold mb-6">Login</h1>
        {error && (
          <p role="alert" className="mb-4 rounded-xl bg-red-500/20 p-3">
            {error}
          </p>
        )}
        <input
          type="email"
          autoComplete="username"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
        />
        <input
          type="password"
          autoComplete="current-password"
          required
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 rounded-xl bg-black/20 mb-6"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-500 text-black py-3 rounded-xl font-bold"
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </main>
  );
}
