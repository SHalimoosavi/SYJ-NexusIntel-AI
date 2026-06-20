"use client";

import { useState } from "react";
import { authHeaders } from "@/lib/auth";

const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

export default function CreateLeadForm() {
  const [loading, setLoading] =
    useState(false);

  const [form, setForm] = useState({
    business_name: "",
    contact_person: "",
    email: "",
    phone: "",
    website: "",
    city: "",
    category: "",
    source: "Manual",
    notes: "",
  });

  async function submitLead(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/leads/`,
        {
          method: "POST",
          headers: authHeaders(),
          body: JSON.stringify(form),
        }
      );

      if (!response.ok) {
        const error =
          await response.text();

        alert(error);

        setLoading(false);

        return;
      }

      alert(
        "Lead created successfully"
      );

      window.location.reload();
    } catch (error) {
      console.error(error);

      alert(
        "Failed to create lead"
      );
    }

    setLoading(false);
  }

  return (
    <form
      onSubmit={submitLead}
      className="
        glass
        rounded-3xl
        p-6
        mb-8
      "
    >
      <h2 className="text-xl font-bold mb-6">
        Create Lead
      </h2>

      <div className="grid md:grid-cols-2 gap-4">
        <input
          placeholder="Business Name"
          className="p-3 rounded-xl bg-black/20"
          value={form.business_name}
          onChange={(e) =>
            setForm({
              ...form,
              business_name:
                e.target.value,
            })
          }
        />

        <input
          placeholder="Contact Person"
          className="p-3 rounded-xl bg-black/20"
          value={form.contact_person}
          onChange={(e) =>
            setForm({
              ...form,
              contact_person:
                e.target.value,
            })
          }
        />

        <input
          placeholder="Email"
          className="p-3 rounded-xl bg-black/20"
          value={form.email}
          onChange={(e) =>
            setForm({
              ...form,
              email:
                e.target.value,
            })
          }
        />

        <input
          placeholder="Phone"
          className="p-3 rounded-xl bg-black/20"
          value={form.phone}
          onChange={(e) =>
            setForm({
              ...form,
              phone:
                e.target.value,
            })
          }
        />

        <input
          placeholder="Website"
          className="p-3 rounded-xl bg-black/20"
          value={form.website}
          onChange={(e) =>
            setForm({
              ...form,
              website:
                e.target.value,
            })
          }
        />

        <input
          placeholder="City"
          className="p-3 rounded-xl bg-black/20"
          value={form.city}
          onChange={(e) =>
            setForm({
              ...form,
              city:
                e.target.value,
            })
          }
        />

        <input
          placeholder="Category"
          className="p-3 rounded-xl bg-black/20"
          value={form.category}
          onChange={(e) =>
            setForm({
              ...form,
              category:
                e.target.value,
            })
          }
        />
      </div>

      <button
        disabled={loading}
        className="
          mt-6
          px-6
          py-3
          rounded-xl
          bg-emerald-500
          text-black
          font-bold
        "
      >
        {loading
          ? "Creating..."
          : "Create Lead"}
      </button>
    </form>
  );
}
