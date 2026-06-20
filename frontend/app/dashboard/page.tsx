import ExecutiveDashboard from "@/components/dashboard/executive-dashboard";

import {
  getCRMStats,
  getCRMRevenue,
  getCRMPipeline,
} from "@/lib/api";

export default async function DashboardPage() {

  const stats =
    await getCRMStats();

  const revenue =
    await getCRMRevenue();

  const pipeline =
    await getCRMPipeline();

  return (
    <main
      className="
        min-h-screen
        gradient-bg
        p-8
      "
    >
      <div className="mb-10">

        <h1
          className="
            text-5xl
            font-black
            mb-3
          "
        >
          Executive Dashboard
        </h1>

        <p className="text-slate-400">
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
      />

    </main>
  );
}
