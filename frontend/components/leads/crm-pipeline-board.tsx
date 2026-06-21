import { Lead } from "@/types/lead";

type Props = {
  leads: Lead[];
};

const stages = [
  "NEW",
  "CONTACTED",
  "MEETING",
  "PROPOSAL",
  "WON",
];

export default function CRMPipelineBoard({
  leads,
}: Props) {
  return (
    <div className="grid md:grid-cols-5 gap-4 mb-8">
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
            <h3 className="font-bold mb-4">
              {stage}
            </h3>

            <div className="space-y-3">
              {stageLeads.map((lead) => (
                <div
                  key={lead.id}
                  className="rounded-xl bg-black/20 p-3"
                >
                  <p className="font-semibold">
                    {lead.business_name}
                  </p>

                  <p className="text-xs text-slate-400">
                    ₹{lead.estimated_value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
