import LeadTable from "@/components/leads/lead-table";

import CreateLeadForm from "@/components/leads/create-lead-form";

import { getLeads } from "@/lib/api";

export default async function LeadsPage() {

  const leads =
    await getLeads();

  return (
    <main className="gradient-bg min-h-screen p-8">

      <h1 className="text-4xl font-bold mb-8">
        Lead Center
      </h1>

      <CreateLeadForm />

      <LeadTable
        leads={leads}
      />

    </main>
  );
}
