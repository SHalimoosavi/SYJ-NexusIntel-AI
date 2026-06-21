type Activity = {
  id: number;
  activity_type: string;
  description: string | null;
  created_at: string;
};

type Props = {
  activities: Activity[];
};

export default function ActivityTimeline({
  activities,
}: Props) {
  return (
    <div className="glass rounded-3xl p-6">
      <h2 className="text-2xl font-black mb-6">
        Activity Timeline
      </h2>

      <div className="space-y-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="border-l-2 border-cyan-500 pl-4"
          >
            <p className="font-semibold">
              {activity.activity_type}
            </p>

            <p className="text-slate-400 text-sm">
              {activity.description}
            </p>

            <p className="text-xs text-slate-500 mt-1">
              {new Date(
                activity.created_at
              ).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
