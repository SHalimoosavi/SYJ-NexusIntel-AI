const API_BASE =
  "http://127.0.0.1:8001";

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

export async function getLeads() {
  const response =
    await fetch(
      `${API_BASE}/leads/`,
      {
        cache: "no-store",
      }
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch leads"
    );
  }

  return response.json();
}

export async function getCRMStats(): Promise<CRMStats> {
  const response =
    await fetch(
      `${API_BASE}/crm/stats`,
      {
        cache: "no-store",
      }
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch CRM stats"
    );
  }

  return response.json();
}

export async function getCRMRevenue(): Promise<CRMRevenue> {
  const response =
    await fetch(
      `${API_BASE}/crm/revenue`,
      {
        cache: "no-store",
      }
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch revenue data"
    );
  }

  return response.json();
}

export async function getCRMPipeline(): Promise<CRMPipeline> {
  const response =
    await fetch(
      `${API_BASE}/crm/pipeline`,
      {
        cache: "no-store",
      }
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch pipeline data"
    );
  }

  return response.json();
}

export { API_BASE };
