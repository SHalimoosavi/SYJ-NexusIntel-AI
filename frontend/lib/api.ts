const API_BASE =
  "http://127.0.0.1:8000";

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
