"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "@/lib/auth";

export default function RegisterPage() {

  const router =
    useRouter();

  const [fullName,setFullName] =
    useState("");

  const [email,setEmail] =
    useState("");

  const [password,setPassword] =
    useState("");

  async function submit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    await register(
      fullName,
      email,
      password
    );

    router.push(
      "/login"
    );
  }

  return (
    <main className="min-h-screen gradient-bg flex items-center justify-center">
      <form
        onSubmit={submit}
        className="glass p-8 rounded-3xl w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-6">
          Register
        </h1>

        <input
          placeholder="Full Name"
          className="w-full p-3 rounded-xl bg-black/20 mb-4"
          value={fullName}
          onChange={(e)=>
            setFullName(
              e.target.value
            )
          }
        />

        <input
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
          placeholder="Password"
          type="password"
          className="w-full p-3 rounded-xl bg-black/20 mb-6"
          value={password}
          onChange={(e)=>
            setPassword(
              e.target.value
            )
          }
        />

        <button
          className="w-full bg-emerald-500 text-black py-3 rounded-xl font-bold"
        >
          Register
        </button>
      </form>
    </main>
  );
}
