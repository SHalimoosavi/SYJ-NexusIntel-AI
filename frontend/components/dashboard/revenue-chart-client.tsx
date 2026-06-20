"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

type Props = {
  pipelineValue: number;
  forecastRevenue: number;
  wonRevenue: number;
};

export default function RevenueChartClient({
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
        rounded-3xl
        border
        border-white/10
        bg-slate-900/60
        backdrop-blur-xl
        p-6
      "
    >
      <h2 className="text-xl font-black mb-6">
        Revenue Analytics
      </h2>

      <div className="h-[300px]">

        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="metric" />
            <YAxis />
            <Tooltip />

            <Bar
              dataKey="value"
              fill="#10b981"
            />
          </BarChart>
        </ResponsiveContainer>

      </div>
    </div>
  );
}
