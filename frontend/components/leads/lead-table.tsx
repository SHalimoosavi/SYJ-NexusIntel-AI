import { Lead } from "@/types/lead";

type Props = {
  leads: Lead[];
};

export default function LeadTable({
  leads,
}: Props) {

  return (
    <div className="glass rounded-3xl p-6 overflow-auto">

      <h2 className="text-2xl font-bold mb-6">
        Leads
      </h2>

      <table className="w-full">

        <thead>

          <tr className="text-left border-b border-white/10">

            <th className="p-3">
              Business
            </th>

            <th className="p-3">
              Category
            </th>

            <th className="p-3">
              City
            </th>

            <th className="p-3">
              Contact
            </th>

          </tr>

        </thead>

        <tbody>

          {leads.map((lead) => (

            <tr
              key={lead.id}
              className="border-b border-white/5"
            >

              <td className="p-3">
                {lead.business_name}
              </td>

              <td className="p-3">
                {lead.category}
              </td>

              <td className="p-3">
                {lead.city}
              </td>

              <td className="p-3">
                {lead.contact_person}
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}
