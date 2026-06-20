import { authHeaders } from "./auth";

export const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

/* =========================
   TYPES
========================= */

export interface Lead {
  id: number;
  business_name: string;
  contact_person: string;
  email: string;
  phone: string;
  website: string;
  city: string;
  category: string;
  source: string;
  notes: string;
  created_at: string;
}

export interface CRMStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  meeting_leads: number;
  proposal_leads: number;
  won_deals: number;
  lost_deals: number;
}

export interface CRMRevenue {
  pipeline_value: number;
  won_revenue: number;
  forecast_revenue: number;
}

export interface CRMPipeline {
  new: number;
  contacted: number;
  meeting: number;
  proposal: number;
  won: number;
  lost: number;
}

export interface ExecutiveBriefing {
  pipeline_value: number;
  forecast_revenue: number;
  annual_projection: number;
  close_rate: number;
  executive_summary: string;
  risk_summary: string;
  recommendation: string;
}

export interface SalesPriority {
  id: number;
  business_name: string;
  estimated_value: number;
  pipeline_stage: string;
  score: number;
  priority: string;
  next_followup: string | null;
}

export interface AgentMemory {
  id: number;
  domain: string;
  overall_score: number;
  priority: string;
  estimated_value: string;
  created_at: string;
}

/* =========================
   LEADS (JWT PROTECTED)
========================= */

export async function getLeads() {
  const response = await fetch(
    `${API_BASE}/leads/`,
    {
      headers: authHeaders(),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch leads");
  }

  return response.json();
}

export async function createLead(
  payload: any
) {
  const response = await fetch(
    `${API_BASE}/leads/`,
    {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to create lead");
  }

  return response.json();
}

export async function updateLead(
  leadId: number,
  payload: any
) {
  const response = await fetch(
    `${API_BASE}/leads/${leadId}`,
    {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update lead");
  }

  return response.json();
}

export async function deleteLead(
  leadId: number
) {
  const response = await fetch(
    `${API_BASE}/leads/${leadId}`,
    {
      method: "DELETE",
      headers: authHeaders(),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete lead");
  }

  return response.json();
}

/* =========================
   DASHBOARD APIS
========================= */

export async function getCRMStats(): Promise<CRMStats> {
  const response = await fetch(
    `${API_BASE}/crm/stats`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch CRM stats");
  }

  return response.json();
}

export async function getCRMRevenue(): Promise<CRMRevenue> {
  const response = await fetch(
    `${API_BASE}/crm/revenue`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch revenue");
  }

  return response.json();
}

export async function getCRMPipeline(): Promise<CRMPipeline> {
  const response = await fetch(
    `${API_BASE}/crm/pipeline`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch pipeline");
  }

  return response.json();
}

export async function getExecutiveBriefing(): Promise<ExecutiveBriefing> {
  const response = await fetch(
    `${API_BASE}/executive-intelligence/briefing`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch executive briefing");
  }

  return response.json();
}

export async function getExecutiveOpportunities() {
  const response = await fetch(
    `${API_BASE}/executive-intelligence/opportunities`,
    {
      cache: "no-store",
    }
  );

  return response.json();
}

export async function getExecutiveRisks() {
  const response = await fetch(
    `${API_BASE}/executive-intelligence/risks`,
    {
      cache: "no-store",
    }
  );

  return response.json();
}

export async function getMemoryHistory(
  domain: string
): Promise<AgentMemory[]> {
  const response = await fetch(
    `${API_BASE}/agent-memory/history/${domain}`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch memory history");
  }

  return response.json();
}

export async function getSalesPriorities(): Promise<SalesPriority[]> {
  const response = await fetch(
    `${API_BASE}/sales-agent/priorities`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch priorities");
  }

  return response.json();
}

export async function getIntelligenceReport() {
  const response = await fetch(
    `${API_BASE}/intelligence/report`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        domain: "google.com",
      }),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch intelligence report"
    );
  }

  return response.json();
}
