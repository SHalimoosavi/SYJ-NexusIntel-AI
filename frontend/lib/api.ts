import { authHeaders } from "./auth";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
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

export interface RelationshipIntelligence {
  total_leads: number;
  healthy_relationships: number;
  overdue_followups: number;
  engagement_score: number;
  recommendations: string[];
}

export interface Activity {
  id: number;
  lead_id: number;
  activity_type: string;
  description: string | null;
  created_at: string;
}

export interface CRMStats {
  total_leads: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  average_lead_score: number;
  won_deals: number;
  lost_deals: number;
  close_rate: number;
}

export interface CRMRevenue {
  pipeline_value: number;
  forecast_revenue: number;
  won_revenue: number;

  win_rate: number;
  average_deal_size: number;
  sales_velocity: number;

  quarterly_projection: number;
  annual_projection: number;
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
      credentials: "include",
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch leads");
  }

  return response.json();
}

export async function getRelationshipIntelligence(): Promise<RelationshipIntelligence> {
  const response = await fetch(
    `${API_BASE}/relationship-intelligence`,
    {
      headers: authHeaders(),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch relationship intelligence"
    );
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
      headers: authHeaders(),
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
      headers: authHeaders(),
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
      headers: authHeaders(),
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
      headers: authHeaders(),
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
      headers: authHeaders(),
      cache: "no-store",
    }
  );

  return response.json();
}

export async function getExecutiveRisks() {
  const response = await fetch(
    `${API_BASE}/executive-intelligence/risks`,
    {
      headers: authHeaders(),
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
      headers: authHeaders(),
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
      headers: authHeaders(),
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
      headers: authHeaders(),
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

export async function getLeadActivities(
  leadId: number
): Promise<Activity[]> {
  const response = await fetch(
    `${API_BASE}/activities/${leadId}`,
    {
      headers: authHeaders(),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch activities"
    );
  }

  return response.json();
}
