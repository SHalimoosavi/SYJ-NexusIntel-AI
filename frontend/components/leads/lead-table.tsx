"use client";

import { Lead } from "@/types/lead";
import { authHeaders } from "@/lib/auth";

const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

type Props = {
  leads: Lead[];
};

export default function LeadTable({
  leads,
}: Props) {
  async function deleteLead(
    id: number
  ) {
    const confirmed = window.confirm(
      "Delete this lead?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE}/leads/${id}`,
        {
          method: "DELETE",
          headers: authHeaders(),
        }
      );

      if (!response.ok) {
        alert(
          "Failed to delete lead"
        );
        return;
      }

      window.location.reload();
    } catch (error) {
      console.error(error);

      alert(
        "Failed to delete lead"
      );
    }
  }

  return (
    <div className="glass rounded-3xl p-6 overflow-auto">
      <h2 className="text-2xl font-bold mb-6">
        Leads
      </h2>

      <table className="w-full">
        <thead>
          <tr className="text-left border-b border-white/10">
            <th className="p-3">
              Business
            </th>

            <th className="p-3">
              Category
            </th>

            <th className="p-3">
              City
            </th>

            <th className="p-3">
              Contact
            </th>

            <th className="p-3">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => (
            <tr
              key={lead.id}
              className="border-b border-white/5"
            >
              <td className="p-3">
                {lead.business_name}
              </td>

              <td className="p-3">
                {lead.category}
              </td>

              <td className="p-3">
                {lead.city}
              </td>

              <td className="p-3">
                {lead.contact_person}
              </td>

              <td className="p-3">
                <button
                  onClick={() =>
                    deleteLead(
                      lead.id
                    )
                  }
                  className="
                    px-3
                    py-1
                    rounded-lg
                    bg-red-500
                    text-white
                  "
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
