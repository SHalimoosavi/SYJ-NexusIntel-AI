import CommandLayout from "@/components/layout/command-layout";

import ExecutiveBriefing from "@/components/dashboard/executive-briefing";
import OpportunityMatrix from "@/components/dashboard/opportunity-matrix";
import MemoryTimeline from "@/components/dashboard/memory-timeline";
import AgentFeed from "@/components/dashboard/agent-feed";
import RevenueChart from "@/components/dashboard/revenue-chart";

import {
  getExecutiveBriefing,
  getExecutiveOpportunities,
  getMemoryHistory,
  getCRMRevenue,
} from "@/lib/api";

export default async function InvestorDemoPage() {

  const briefing =
    await getExecutiveBriefing();

  const opportunities =
    await getExecutiveOpportunities();

  const memories =
    await getMemoryHistory(
      "google.com"
    );

  const revenue =
    await getCRMRevenue();

  return (
    <CommandLayout>

      <div
        className="
          mb-10
          text-center
        "
      >

        <p
          className="
            text-emerald-400
            tracking-[0.3em]
            text-sm
            uppercase
          "
        >
          Investor Demo Mode
        </p>

        <h1
          className="
            text-6xl
            font-black
            mt-4
          "
        >
          SYJ NexusIntel AI
        </h1>

        <p
          className="
            text-slate-400
            mt-4
            max-w-3xl
            mx-auto
          "
        >
          Autonomous Multi-Agent Business
          Intelligence Platform combining
          Opportunity Discovery,
          Revenue Forecasting,
          Executive Intelligence,
          CRM Analytics and
          AI Decision Support.
        </p>

      </div>

      <div className="space-y-8">

        <ExecutiveBriefing
          briefing={briefing}
        />

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

          <AgentFeed />

        </div>

        <div
          className="
            grid
            gap-6
            xl:grid-cols-2
          "
        >

          <OpportunityMatrix
            opportunities={
              opportunities
            }
          />

          <MemoryTimeline
            memories={memories}
          />

        </div>

        <div
          className="
            glass-premium
            rounded-3xl
            p-8
          "
        >

          <h2
            className="
              text-3xl
              font-black
              mb-6
            "
          >
            Growth Projection
          </h2>

          <div
            className="
              grid
              gap-6
              md:grid-cols-3
            "
          >

            <div>
              <p className="text-slate-400">
                Pipeline Value
              </p>

              <h3
                className="
                  text-4xl
                  font-bold
                  text-emerald-400
                "
              >
                $
                {briefing.pipeline_value}
              </h3>
            </div>

            <div>
              <p className="text-slate-400">
                Forecast Revenue
              </p>

              <h3
                className="
                  text-4xl
                  font-bold
                  text-cyan-400
                "
              >
                $
                {briefing.forecast_revenue}
              </h3>
            </div>

            <div>
              <p className="text-slate-400">
                Annual Projection
              </p>

              <h3
                className="
                  text-4xl
                  font-bold
                  text-yellow-400
                "
              >
                $
                {briefing.annual_projection}
              </h3>
            </div>

          </div>

        </div>

      </div>

    </CommandLayout>
  );
}
