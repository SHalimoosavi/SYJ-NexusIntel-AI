type Props = {
  totalLeads: number;
  healthyRelationships: number;
  overdueFollowups: number;
  engagementScore: number;
  recommendations: string[];
};

export default function RelationshipIntelligence({
  totalLeads,
  healthyRelationships,
  overdueFollowups,
  engagementScore,
  recommendations,
}: Props) {
  return (
    <div className="glass rounded-3xl p-6 mb-8">
      <h2 className="text-3xl font-black mb-6">
        Relationship Intelligence
      </h2>

      <div className="grid md:grid-cols-4 gap-4 mb-6">
        <div className="rounded-2xl bg-cyan-500/20 p-4">
          <p>Total Leads</p>
          <h3 className="text-4xl font-black">
            {totalLeads}
          </h3>
        </div>

        <div className="rounded-2xl bg-emerald-500/20 p-4">
          <p>Healthy</p>
          <h3 className="text-4xl font-black">
            {healthyRelationships}
          </h3>
        </div>

        <div className="rounded-2xl bg-red-500/20 p-4">
          <p>Overdue</p>
          <h3 className="text-4xl font-black">
            {overdueFollowups}
          </h3>
        </div>

        <div className="rounded-2xl bg-yellow-500/20 p-4">
          <p>Engagement</p>
          <h3 className="text-4xl font-black">
            {engagementScore}%
          </h3>
        </div>
      </div>

      <div className="rounded-2xl bg-black/20 p-4">
        <h3 className="font-bold mb-3">
          AI Recommendations
        </h3>

        <ul className="space-y-2">
          {recommendations.map(
            (item, index) => (
              <li key={index}>
                • {item}
              </li>
            )
          )}
        </ul>
      </div>
    </div>
  );
}
