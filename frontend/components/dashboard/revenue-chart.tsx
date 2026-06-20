"use client";

import dynamic from "next/dynamic";

const RevenueChartClient =
  dynamic(
    () => import("./revenue-chart-client"),
    {
      ssr: false,
    }
  );

type Props = {
  pipelineValue: number;
  forecastRevenue: number;
  wonRevenue: number;
};

export default function RevenueChart(
  props: Props
) {
  return (
    <RevenueChartClient
      {...props}
    />
  );
}
