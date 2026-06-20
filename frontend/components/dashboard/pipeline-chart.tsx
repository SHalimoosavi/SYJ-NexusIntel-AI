"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
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

export default function PipelineChart({
  pipeline,
}: Props) {
  const data = [
    {
      stage: "NEW",
      count: pipeline.new,
    },
    {
      stage: "CONTACTED",
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
        glass
        rounded-3xl
        p-6
        h-[350px]
      "
    >
      <h2 className="text-xl font-bold mb-6">
        CRM Pipeline
      </h2>

      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <BarChart data={data}>
          <XAxis dataKey="stage" />

          <Tooltip />

          <Bar
            dataKey="count"
            fill="#10b981"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
