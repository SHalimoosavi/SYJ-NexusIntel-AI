"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { acceptInvitation } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [invitationToken, setInvitationToken] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      await acceptInvitation(
        fullName,
        email,
        password,
        invitationToken
      );

      router.push("/login");
    } catch (err: any) {
      setError(
        err?.message ||
          "Invitation acceptance failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen gradient-bg flex items-center justify-center">
      <form
        onSubmit={submit}
        className="glass p-8 rounded-3xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-2">
          Join Organization
        </h1>

        <p className="mb-6 opacity-70">
          Accept your invitation to
          SYJ NexusIntel AI
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/20">
            {error}
          </div>
        )}

        <input
          placeholder="Full Name"
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
          value={fullName}
          onChange={(e) =>
            setFullName(
              e.target.value
            )
          }
        />

        <input
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
          placeholder="Password"
          type="password"
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <input
          placeholder="Invitation Token"
          className="w-full p-3 rounded-xl bg-black/20 mb-6"
          value={invitationToken}
          onChange={(e) =>
            setInvitationToken(
              e.target.value
            )
          }
        />

        <button
          disabled={loading}
          className="w-full bg-emerald-500 text-black py-3 rounded-xl font-bold"
        >
          {loading
            ? "Joining..."
            : "Accept Invitation"}
        </button>
      </form>
    </main>
  );
}
