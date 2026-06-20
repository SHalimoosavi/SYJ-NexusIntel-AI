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
import ExecutiveBriefing from "./executive-briefing";
import AgentFeed from "./agent-feed";
import MemoryTimeline from "./memory-timeline";
import OpportunityMatrix from "./opportunity-matrix";
import IntelligencePanel from "./intelligence-panel";

import Reveal from "@/components/motion/reveal";

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

briefing: {
pipeline_value: number;
forecast_revenue: number;
annual_projection: number;
executive_summary: string;
risk_summary: string;
recommendation: string;
};

memories: {
id: number;
overall_score: number;
priority: string;
created_at: string;
}[];

opportunities: {
id: number;
business_name: string;
estimated_value: number;
pipeline_stage: string;
}[];

intelligenceReport: {
overall_score: number;
security_score: number;
seo_score: number;
trust_score: number;
recommendations: string[];
};

risks: {
risk_count: number;
risks: string[];
};
};

export default function ExecutiveDashboard({
stats,
revenue,
pipeline,
briefing,
memories,
opportunities,
intelligenceReport,
risks,
}: Props) {
return (
<div className="space-y-6">

  <Reveal delay={0.30}>
    <ExecutiveBriefing
      briefing={briefing}
    />
  </Reveal>

  <Reveal delay={0.45}>
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
  </Reveal>

  <Reveal delay={0.60}>
    <div
      className="
        grid
        gap-6
        xl:grid-cols-2
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
  </Reveal>

  <Reveal delay={0.75}>
    <div
      className="
        grid
        gap-6
        xl:grid-cols-2
      "
    >
      <AgentFeed />

      <MemoryTimeline
        memories={memories}
      />
    </div>
  </Reveal>

  <Reveal delay={1.00}>
    <div
      className="
        grid
        gap-6
        xl:grid-cols-2
      "
    >
      <OpportunityMatrix
        opportunities={opportunities}
      />

      <IntelligencePanel
        report={
          intelligenceReport
        }
        risks={risks}
      />
    </div>
  </Reveal>

</div>

);
}
