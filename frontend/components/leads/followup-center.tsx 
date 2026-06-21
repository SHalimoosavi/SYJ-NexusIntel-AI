import { Lead } from "@/types/lead";
import LeadHealthBadge from "./lead-health-badge";

type Props = {
  leads: Lead[];
};

export default function FollowupCenter({
  leads,
}: Props) {
  const followups = leads.filter(
    (lead) =>
      lead.pipeline_stage === "CONTACTED" ||
      lead.pipeline_stage === "MEETING" ||
      lead.next_followup
  );

  return (
    <div className="glass rounded-3xl p-6 mb-8">
      <h2 className="text-2xl font-bold mb-4">
        Follow-Up Center
      </h2>

      <div className="space-y-3">
        {followups.map((lead) => (
          <div
            key={lead.id}
            className="flex flex-col md:flex-row md:items-center md:justify-between rounded-xl bg-black/20 p-4"
          >
            <div>
              <p className="font-bold">
                {lead.business_name}
              </p>

              <p className="text-sm text-slate-400">
                {lead.contact_person}
              </p>
            </div>

            <div className="flex gap-3 mt-3 md:mt-0">
              <LeadHealthBadge
                score={lead.lead_score || 0}
              />

              <span className="px-2 py-1 rounded-lg bg-slate-800 text-sm">
                {lead.priority}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
