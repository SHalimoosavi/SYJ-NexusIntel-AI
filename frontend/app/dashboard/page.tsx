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

export default async function DashboardPage() {

  const stats =
    await getCRMStats();

  const revenue =
    await getCRMRevenue();

  const pipeline =
    await getCRMPipeline();

  const briefing =
    await getExecutiveBriefing();

  const memories =
    await getMemoryHistory(
      "google.com"
    );

  const opportunities =
    await getExecutiveOpportunities();

  const risks =
    await getExecutiveRisks();

  const intelligenceReport =
    await getIntelligenceReport();

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
        stats={stats}
        revenue={revenue}
        pipeline={pipeline}
        briefing={briefing}
        memories={memories}
        opportunities={opportunities}
        intelligenceReport={intelligenceReport}
        risks={risks}
      />

    </CommandLayout>
  );
}
