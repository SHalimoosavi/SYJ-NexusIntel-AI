type Props = {
  totalLeads: number;
  hotLeads: number;
  pipelineValue: number;
  forecastRevenue: number;
  avgLeadScore: number;
  pipelineHealth: number;
};

export default function CRMExecutiveSummary({
  totalLeads,
  hotLeads,
  pipelineValue,
  forecastRevenue,
  avgLeadScore,
  pipelineHealth,
}: Props) {
  const cards = [
    {
      title: "Total Leads",
      value: totalLeads,
    },
    {
      title: "HOT Leads",
      value: hotLeads,
    },
    {
      title: "Pipeline Value",
      value: `₹${pipelineValue.toLocaleString()}`,
    },
    {
      title: "Forecast Revenue",
      value: `₹${forecastRevenue.toLocaleString()}`,
    },
    {
      title: "Avg Lead Score",
      value: `${avgLeadScore}%`,
    },
    {
      title: "Pipeline Health",
      value: `${pipelineHealth}%`,
    },
  ];

  return (
    <div className="grid md:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
      {cards.map((card) => (
        <div
          key={card.title}
          className="glass rounded-3xl p-5"
        >
          <p className="text-slate-400 text-sm">
            {card.title}
          </p>

          <h3 className="text-2xl font-black mt-2">
            {card.value}
          </h3>
        </div>
      ))}
    </div>
  );
}
