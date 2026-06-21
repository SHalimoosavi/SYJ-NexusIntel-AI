import CreateLeadForm from "@/components/leads/create-lead-form";
import LeadTable from "@/components/leads/lead-table";
import CRMKPICards from "@/components/leads/crm-kpi-cards";
import CRMPipelineBoard from "@/components/leads/crm-pipeline-board";
import CRMExecutiveSummary from "@/components/leads/crm-executive-summary";

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
    leads.reduce(
      (
        sum: number,
        lead: any
      ) =>
        sum +
        Math.round(
          (
            (lead.estimated_value || 0) *
            (lead.probability || 0)
          ) / 100
        ),
      0
    );

  const pipelineHealth =
    Math.min(
      100,
      Math.round(
        avgLeadScore * 0.7 +
        warmLeads * 2
      )
    );

  const salesVelocity =
    Math.round(
      forecastRevenue /
      Math.max(
        leads.length,
        1
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
          forecastRevenue
        }
        salesVelocity={
          salesVelocity
        }
      />

      <CreateLeadForm />

      <CRMPipelineBoard
        leads={leads}
      />

      <LeadTable
        leads={leads}
      />
    </main>
  );
}
