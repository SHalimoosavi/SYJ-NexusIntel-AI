import CreateLeadForm from "@/components/leads/create-lead-form";
import LeadTable from "@/components/leads/lead-table";
import CRMKPICards from "@/components/leads/crm-kpi-cards";
import CRMPipelineBoard from "@/components/leads/crm-pipeline-board";
import CRMExecutiveSummary from "@/components/leads/crm-executive-summary";
import FollowupCenter from "@/components/leads/followup-center";

import {
  getLeads,
  getCRMRevenue,
} from "@/lib/api";

export default async function LeadsPage() {
  const leads = await getLeads();

  const revenue =
    await getCRMRevenue();

  const hotLeads = leads.filter(
    (l: any) =>
      l.priority === "HOT"
  ).length;

  const warmLeads = leads.filter(
    (l: any) =>
      l.priority === "WARM"
  ).length;

  const coldLeads = leads.filter(
    (l: any) =>
      l.priority === "COLD"
  ).length;

  const avgLeadScore =
    leads.length > 0
      ? Math.round(
          leads.reduce(
            (
              sum: number,
              lead: any
            ) =>
              sum +
              (lead.lead_score || 0),
            0
          ) / leads.length
        )
      : 0;

  const forecastRevenue =
    revenue.forecast_revenue;

  const pipelineHealth =
    Math.min(
      100,
      Math.round(
        avgLeadScore * 0.7 +
          warmLeads * 2
      )
    );

  return (
    <main className="gradient-bg min-h-screen p-8">
      <h1 className="text-4xl font-bold mb-8">
        Sales CRM
      </h1>

      <CRMExecutiveSummary
        totalLeads={leads.length}
        hotLeads={hotLeads}
        pipelineValue={
          revenue.pipeline_value
        }
        forecastRevenue={
          forecastRevenue
        }
        avgLeadScore={
          avgLeadScore
        }
        pipelineHealth={
          pipelineHealth
        }
      />

      <CRMKPICards
        totalLeads={leads.length}
        hotLeads={hotLeads}
        warmLeads={warmLeads}
        coldLeads={coldLeads}
        pipelineValue={
          revenue.pipeline_value
        }
        forecastRevenue={
          revenue.forecast_revenue
        }
        averageDealSize={
          revenue.average_deal_size
        }
        salesVelocity={
          revenue.sales_velocity
        }
      />

      <FollowupCenter
        leads={leads}
        forecastRevenue={
          revenue.forecast_revenue
        }
        salesVelocity={
          revenue.sales_velocity
        }
      />

      <CreateLeadForm />

      <CRMPipelineBoard
        leads={leads}
      />

      <LeadTable
        leads={leads}
      />

      <div className="grid md:grid-cols-2 gap-6 mt-8">
        <div className="glass rounded-3xl p-6">
          <h2 className="text-2xl font-black mb-4">
            Quarterly Projection
          </h2>

          <p className="text-5xl font-black text-cyan-400">
            ₹
            {revenue.quarterly_projection.toLocaleString()}
          </p>
        </div>

        <div className="glass rounded-3xl p-6">
          <h2 className="text-2xl font-black mb-4">
            Annual Projection
          </h2>

          <p className="text-5xl font-black text-emerald-400">
            ₹
            {revenue.annual_projection.toLocaleString()}
          </p>
        </div>
      </div>
    </main>
  );
}
