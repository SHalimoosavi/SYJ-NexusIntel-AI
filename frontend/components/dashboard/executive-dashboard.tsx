"use client";

import {
  Users,
  Briefcase,
  DollarSign,
  Trophy,
} from "lucide-react";

import KPICard from "./kpi-card";
import RevenueChart from "./revenue-chart";
import PipelineChart from "./pipeline-chart";

type Props = {
  stats: {
    total_leads: number;
  };

  revenue: {
    pipeline_value: number;
    forecast_revenue: number;
    won_revenue: number;
  };

  pipeline: {
    new: number;
    contacted: number;
    meeting: number;
    proposal: number;
    won: number;
    lost: number;
  };
};

export default function ExecutiveDashboard({
  stats,
  revenue,
  pipeline,
}: Props) {
  return (
    <div className="space-y-8">

      <div
        className="
          grid
          gap-6
          md:grid-cols-2
          xl:grid-cols-4
        "
      >
        <KPICard
          title="Total Leads"
          value={stats.total_leads}
          subtitle="CRM Records"
          icon={Users}
        />

        <KPICard
          title="Pipeline Value"
          value={`$${revenue.pipeline_value}`}
          subtitle="Open Opportunities"
          icon={Briefcase}
        />

        <KPICard
          title="Forecast Revenue"
          value={`$${revenue.forecast_revenue}`}
          subtitle="Expected Revenue"
          icon={DollarSign}
        />

        <KPICard
          title="Won Revenue"
          value={`$${revenue.won_revenue}`}
          subtitle="Closed Revenue"
          icon={Trophy}
        />
      </div>

      <div
        className="
          grid
          gap-6
          lg:grid-cols-2
        "
      >
        <RevenueChart
          pipelineValue={
            revenue.pipeline_value
          }
          forecastRevenue={
            revenue.forecast_revenue
          }
          wonRevenue={
            revenue.won_revenue
          }
        />

        <PipelineChart
          pipeline={pipeline}
        />
      </div>

    </div>
  );
}
