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
  pipeline: {
    new: number;
    contacted: number;
    meeting: number;
    proposal: number;
    won: number;
    lost: number;
  };
};

export default function PipelineChartClient({
  pipeline,
}: Props) {

  const data = [
    {
      stage: "NEW",
      count: pipeline.new,
    },
    {
      stage: "CONTACT",
      count: pipeline.contacted,
    },
    {
      stage: "MEETING",
      count: pipeline.meeting,
    },
    {
      stage: "PROPOSAL",
      count: pipeline.proposal,
    },
    {
      stage: "WON",
      count: pipeline.won,
    },
    {
      stage: "LOST",
      count: pipeline.lost,
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
        CRM Pipeline
      </h2>

      <div className="h-[300px]">

        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="stage" />
            <YAxis />
            <Tooltip />

            <Bar
              dataKey="count"
              fill="#10b981"
            />
          </BarChart>
        </ResponsiveContainer>

      </div>
    </div>
  );
}
