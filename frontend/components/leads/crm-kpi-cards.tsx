type Props = {
  totalLeads: number;
  hotLeads: number;
  warmLeads: number;
  coldLeads: number;
  pipelineValue: number;
};

export default function CRMKPICards({
  totalLeads,
  hotLeads,
  warmLeads,
  coldLeads,
  pipelineValue,
}: Props) {
  const cards = [
    {
      title: "Total Leads",
      value: totalLeads,
    },
    {
      title: "Hot Leads",
      value: hotLeads,
    },
    {
      title: "Warm Leads",
      value: warmLeads,
    },
    {
      title: "Cold Leads",
      value: coldLeads,
    },
    {
      title: "Pipeline Value",
      value: `₹${pipelineValue.toLocaleString()}`,
    },
  ];

  return (
    <div className="grid md:grid-cols-5 gap-4 mb-8">
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
