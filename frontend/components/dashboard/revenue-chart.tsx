"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  Tooltip,
} from "recharts";

type Props = {
  pipelineValue: number;
  forecastRevenue: number;
  wonRevenue: number;
};

export default function RevenueChart({
  pipelineValue,
  forecastRevenue,
  wonRevenue,
}: Props) {
  const data = [
    {
      metric: "Pipeline",
      value: pipelineValue,
    },
    {
      metric: "Forecast",
      value: forecastRevenue,
    },
    {
      metric: "Won",
      value: wonRevenue,
    },
  ];

  return (
    <div
      className="
        glass
        rounded-3xl
        p-6
        h-[350px]
      "
    >
      <h2 className="text-xl font-bold mb-6">
        Revenue Analytics
      </h2>

      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <BarChart data={data}>
          <XAxis dataKey="metric" />

          <Tooltip />

          <Bar
            dataKey="value"
            fill="#10b981"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
