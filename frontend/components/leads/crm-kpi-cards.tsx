type Props = {
  totalLeads: number;
  hotLeads: number;
  warmLeads: number;
  coldLeads: number;

  pipelineValue: number;

  forecastRevenue: number;

  averageDealSize: number;

  salesVelocity: number;
};

export default function CRMKPICards({
  totalLeads,
  hotLeads,
  warmLeads,
  coldLeads,
  pipelineValue,
  forecastRevenue,
  averageDealSize,
  salesVelocity,
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
      title: "WARM Leads",
      value: warmLeads,
    },
    {
      title: "COLD Leads",
      value: coldLeads,
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
      title: "Average Deal",
      value: `₹${averageDealSize.toLocaleString()}`,
    },
    {
      title: "Sales Velocity",
      value: `₹${Math.round(
        salesVelocity
      ).toLocaleString()}`,
    },
  ];

  return (
    <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
      {cards.map((card) => (
        <div
          key={card.title}
          className="glass rounded-3xl p-6"
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
  );
}
