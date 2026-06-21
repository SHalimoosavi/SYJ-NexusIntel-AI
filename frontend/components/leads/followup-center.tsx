type Lead = {
  id: number;
  business_name: string;
  estimated_value?: number;
  probability?: number;
  next_followup?: string | null;
  priority?: string;
};

type Props = {
  leads: Lead[];
  forecastRevenue: number;
  salesVelocity: number;
};

export default function FollowupCenter({
  leads,
  forecastRevenue,
  salesVelocity,
}: Props) {
  const today = new Date();

  const overdueLeads = leads.filter((lead) => {
    if (!lead.next_followup) return false;

    return (
      new Date(lead.next_followup) <
      today
    );
  });

  const highValueLeads =
    leads.filter(
      (lead) =>
        (lead.estimated_value || 0) >=
        100000
    );

  return (
    <div className="glass rounded-3xl p-6 mb-8">
      <h2 className="text-3xl font-black mb-6">
        Follow-Up Intelligence
      </h2>

      <div className="grid md:grid-cols-4 gap-4 mb-8">
        <div className="rounded-2xl bg-red-500/20 p-4">
          <p className="text-sm text-slate-300">
            Overdue Follow-Ups
          </p>

          <h3 className="text-4xl font-black">
            {overdueLeads.length}
          </h3>
        </div>

        <div className="rounded-2xl bg-yellow-500/20 p-4">
          <p className="text-sm text-slate-300">
            High Value Leads
          </p>

          <h3 className="text-4xl font-black">
            {highValueLeads.length}
          </h3>
        </div>

        <div className="rounded-2xl bg-emerald-500/20 p-4">
          <p className="text-sm text-slate-300">
            Forecast Revenue
          </p>

          <h3 className="text-2xl font-black">
            ₹{forecastRevenue.toLocaleString()}
          </h3>
        </div>

        <div className="rounded-2xl bg-cyan-500/20 p-4">
          <p className="text-sm text-slate-300">
            Sales Velocity
          </p>

          <h3 className="text-2xl font-black">
            ₹{salesVelocity.toLocaleString()}
          </h3>
        </div>
      </div>

      <div className="rounded-2xl bg-black/20 p-5">
        <h3 className="font-bold mb-4">
          AI Recommendations
        </h3>

        <ul className="space-y-2 text-slate-300">
          <li>
            • Prioritize HOT leads above ₹100,000.
          </li>

          <li>
            • Contact overdue leads immediately.
          </li>

          <li>
            • Move WARM leads into Proposal stage.
          </li>

          <li>
            • Focus on high probability opportunities.
          </li>
        </ul>
      </div>
    </div>
  );
}
