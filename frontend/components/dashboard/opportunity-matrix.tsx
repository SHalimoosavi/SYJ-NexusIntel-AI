"use client";

type Opportunity = {
  id: number;
  business_name: string;
  estimated_value: number;
  pipeline_stage: string;
};

type Props = {
  opportunities: Opportunity[];
};

export default function OpportunityMatrix({
  opportunities,
}: Props) {

  const totalValue =
    opportunities.reduce(
      (sum, item) =>
        sum + item.estimated_value,
      0
    );

  return (
    <div
      className="
        glass-premium
        rounded-3xl
        p-6
      "
    >
      <div className="flex justify-between items-center mb-6">

        <div>

          <h2 className="text-2xl font-black">
            Opportunity Center
          </h2>

          <p className="text-slate-400">
            Revenue Opportunities
          </p>

        </div>

        <div>

          <p className="text-xs text-slate-400">
            Pipeline Value
          </p>

          <h3
            className="
              text-xl
              font-bold
              text-emerald-400
            "
          >
            ${totalValue}
          </h3>

        </div>

      </div>

      <div className="space-y-3">

        {opportunities.map((item) => (

          <div
            key={item.id}
            className="
              rounded-2xl
              border
              border-white/5
              p-4
              bg-black/20
            "
          >
            <div className="flex justify-between">

              <div>

                <h3 className="font-bold">
                  {item.business_name}
                </h3>

                <p className="text-sm text-slate-400">
                  {item.pipeline_stage}
                </p>

              </div>

              <div className="text-right">

                <p className="text-xs text-slate-500">
                  Opportunity Value
                </p>

                <p
                  className="
                    font-bold
                    text-emerald-400
                  "
                >
                  ${item.estimated_value}
                </p>

              </div>

            </div>
          </div>

        ))}

      </div>
    </div>
  );
}
