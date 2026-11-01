"use client";

import type { Lead } from "@/types/lead";
import { deleteLead as deleteLeadRequest } from "@/lib/api";

type Props = {
  leads: Lead[];
};

export default function LeadTable({
  leads,
}: Props) {
  async function deleteLead(
    id: number
  ) {
    const confirmed =
      window.confirm(
        "Delete this lead?"
      );

    if (!confirmed) {
      return;
    }

    try {
      await deleteLeadRequest(id);

      window.location.reload();
    } catch (error) {
      console.error(error);

      alert(
        "Failed to delete lead"
      );
    }
  }

  function priorityBadge(
    priority?: string
  ) {
    if (priority === "HOT") {
      return (
        <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-400 text-xs font-bold">
          HOT
        </span>
      );
    }

    if (priority === "WARM") {
      return (
        <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-bold">
          WARM
        </span>
      );
    }

    return (
      <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 text-xs font-bold">
        COLD
      </span>
    );
  }

  return (
    <div className="glass rounded-3xl p-6 overflow-auto">
      <h2 className="text-2xl font-bold mb-6">
        Professional CRM
      </h2>

      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10 text-left">
            <th className="p-3">
              Business
            </th>

            <th className="p-3">
              Lead Score
            </th>

            <th className="p-3">
              Priority
            </th>

            <th className="p-3">
              Pipeline
            </th>

            <th className="p-3">
              Probability
            </th>

            <th className="p-3">
              Value
            </th>

            <th className="p-3">
              Forecast
            </th>

            <th className="p-3">
              Actions
            </th>
          </tr>
        </thead>

        <tbody>
          {leads.map((lead) => {
            const forecast =
              Math.round(
                ((lead
                  .estimated_value ||
                  0) *
                  (lead
                    .probability ||
                    0)) /
                  100
              );

            return (
              <tr
                key={lead.id}
                className="border-b border-white/5"
              >
                <td className="p-3">
                  <div>
                    <div className="font-semibold">
                      {
                        lead.business_name
                      }
                    </div>

                    <div className="text-xs text-slate-400">
                      {lead.city}
                    </div>
                  </div>
                </td>

                <td className="p-3">
                  {lead.lead_score ||
                    0}
                  /100
                </td>

                <td className="p-3">
                  {priorityBadge(
                    lead.priority
                  )}
                </td>

                <td className="p-3">
                  {
                    lead.pipeline_stage
                  }
                </td>

                <td className="p-3">
                  {
                    lead.probability
                  }
                  %
                </td>

                <td className="p-3">
                  ₹
                  {(
                    lead.estimated_value ||
                    0
                  ).toLocaleString()}
                </td>

                <td className="p-3 text-emerald-400 font-semibold">
                  ₹
                  {forecast.toLocaleString()}
                </td>

                <td className="p-3">
                  <button
                    onClick={() =>
                      deleteLead(
                        lead.id
                      )
                    }
                    className="px-3 py-1 rounded-lg bg-red-500 text-white"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
