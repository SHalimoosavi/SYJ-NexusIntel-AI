import { Lead } from "@/types/lead";
import LeadScoreBadge from "@/components/leads/lead-score-badge";

type Props = {
  leads: Lead[];
};

const stages = [
  "NEW",
  "CONTACTED",
  "MEETING",
  "PROPOSAL",
  "NEGOTIATION",
  "WON",
];

export default function CRMPipelineBoard({
  leads,
}: Props) {
  return (
    <div className="grid xl:grid-cols-6 gap-4 mb-8">
      {stages.map((stage) => {
        const stageLeads = leads.filter(
          (lead) =>
            lead.pipeline_stage === stage
        );

        return (
          <div
            key={stage}
            className="glass rounded-3xl p-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-black">
                {stage}
              </h3>

              <span className="text-xs text-slate-400">
                {stageLeads.length}
              </span>
            </div>

            <div className="space-y-4">
              {stageLeads.map((lead) => (
                <div
                  key={lead.id}
                  className="bg-black/20 rounded-2xl p-4 border border-white/5"
                >
                  <h4 className="font-bold">
                    {lead.business_name}
                  </h4>

                  <p className="text-xs text-slate-400 mt-1">
                    {lead.industry || "Unknown Industry"}
                  </p>

                  <p className="text-xs text-slate-500">
                    {lead.company_size || "Unknown Size"}
                  </p>

                  <div className="mt-3">
                    <LeadScoreBadge
                      leadScore={lead.lead_score}
                      priority={lead.priority}
                      probability={lead.probability}
                    />
                  </div>

                  <div className="mt-4 space-y-1">
                    <p className="text-xs text-slate-400">
                      Pipeline Value
                    </p>

                    <p className="font-bold text-emerald-400">
                      ₹
                      {(
                        lead.estimated_value || 0
                      ).toLocaleString()}
                    </p>
                  </div>

                  <div className="mt-3">
                    <p className="text-xs text-slate-400">
                      Forecast Revenue
                    </p>

                    <p className="font-bold text-cyan-400">
                      ₹
                      {Math.round(
                        ((lead.estimated_value ||
                          0) *
                          (lead.probability ||
                            0)) /
                          100
                      ).toLocaleString()}
                    </p>
                  </div>

                  {lead.next_followup && (
                    <div className="mt-3">
                      <p className="text-xs text-slate-400">
                        Next Follow-up
                      </p>

                      <p className="text-xs">
                        {lead.next_followup}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
