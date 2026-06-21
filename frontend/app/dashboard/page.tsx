"use client";

import { useEffect, useState } from "react";

import CommandLayout from "@/components/layout/command-layout";
import ExecutiveDashboard from "@/components/dashboard/executive-dashboard";

import {
getCRMStats,
getCRMRevenue,
getCRMPipeline,
getExecutiveBriefing,
getMemoryHistory,
getExecutiveOpportunities,
getExecutiveRisks,
getIntelligenceReport,
} from "@/lib/api";

export default function DashboardPage() {
const [data, setData] = useState<any>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

useEffect(() => {
async function loadDashboard() {
try {
const [
stats,
revenue,
pipeline,
briefing,
memories,
opportunities,
risks,
intelligenceReport,
] = await Promise.all([
getCRMStats(),
getCRMRevenue(),
getCRMPipeline(),
getExecutiveBriefing(),
getMemoryHistory("google.com"),
getExecutiveOpportunities(),
getExecutiveRisks(),
getIntelligenceReport(),
]);

    setData({
      stats,
      revenue,
      pipeline,
      briefing,
      memories,
      opportunities,
      risks,
      intelligenceReport,
    });
  } catch (err: any) {
    console.error(err);
    setError(
      err?.message ||
      "Failed to load dashboard"
    );
  } finally {
    setLoading(false);
  }
}

loadDashboard();

}, []);

if (loading) {
return (
<CommandLayout>
<div className="p-8">
Loading Dashboard...
</div>
</CommandLayout>
);
}

if (error) {
return (
<CommandLayout>
<div className="p-8 text-red-500">
{error}
</div>
</CommandLayout>
);
}

return (
<CommandLayout>
<div className="mb-8">
<h1
className="
text-5xl
font-black
tracking-tight
"
>
Executive Dashboard
</h1>

    <p
      className="
        text-slate-400
        mt-2
      "
    >
      Revenue Intelligence,
      CRM Analytics,
      Opportunity Tracking
      and Forecasting.
    </p>
  </div>

  <ExecutiveDashboard
    stats={data.stats}
    revenue={data.revenue}
    pipeline={data.pipeline}
    briefing={data.briefing}
    memories={data.memories}
    opportunities={data.opportunities}
    intelligenceReport={data.intelligenceReport}
    risks={data.risks}
  />
</CommandLayout>

);
}
