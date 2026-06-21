type Props = {
  pipelineValue: number;
  forecastRevenue: number;
  annualProjection: number;
  pipelineHealth: number;
  hotLeads: number;
  overdueFollowups: number;
  engagementScore: number;
};

export default function ExecutiveCommandCenter({
  pipelineValue,
  forecastRevenue,
  annualProjection,
  pipelineHealth,
  hotLeads,
  overdueFollowups,
  engagementScore,
}: Props) {
  const cards = [
    {
      title: "Pipeline Value",
      value: `₹${pipelineValue.toLocaleString()}`,
    },
    {
      title: "Forecast Revenue",
      value: `₹${forecastRevenue.toLocaleString()}`,
    },
    {
      title: "Annual Projection",
      value: `₹${annualProjection.toLocaleString()}`,
    },
    {
      title: "Pipeline Health",
      value: `${pipelineHealth}%`,
    },
    {
      title: "HOT Leads",
      value: hotLeads,
    },
    {
      title: "Overdue Follow-Ups",
      value: overdueFollowups,
    },
    {
      title: "Engagement Score",
      value: `${engagementScore}%`,
    },
  ];

  return (
    <div className="glass rounded-3xl p-6 mb-8">
      <h2 className="text-3xl font-black mb-6">
        Executive CRM Command Center
      </h2>

      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div
            key={card.title}
            className="rounded-2xl bg-black/20 p-5"
          >
            <p className="text-slate-400 text-sm">
              {card.title}
            </p>

            <h3 className="text-3xl font-black mt-2">
              {card.value}
            </h3>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl bg-cyan-500/10 p-5">
        <h3 className="font-bold mb-3">
          AI Executive Recommendations
        </h3>

        <ul className="space-y-2 text-slate-300">
          <li>
            • Prioritize HOT leads with the highest deal values.
          </li>

          <li>
            • Follow up immediately on overdue opportunities.
          </li>

          <li>
            • Move qualified WARM leads into Proposal stage.
          </li>

          <li>
            • Focus on opportunities with the highest probability.
          </li>
        </ul>
      </div>
    </div>
  );
}
