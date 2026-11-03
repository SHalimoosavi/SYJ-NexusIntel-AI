"use client";

import { useEffect, useState } from "react";
import { getLeadActivities, type Activity } from "@/lib/api";

type Props = {
  leadId: number;
};

export default function ActivityTimeline({ leadId }: Props) {
  const [activities, setActivities] = useState<Activity[]>([]);

  useEffect(() => {
    let active = true;

    getLeadActivities(leadId)
      .then((data) => {
        if (active) setActivities(data);
      })
      .catch((error: unknown) => {
        if (active) console.error(error);
      });

    return () => {
      active = false;
    };
  }, [leadId]);

  return (
    <div className="glass rounded-3xl p-6">
      <h2 className="text-2xl font-black mb-4">Activity Timeline</h2>
      <div className="space-y-4">
        {activities.map((activity) => (
          <div
            key={activity.id}
            className="rounded-xl bg-black/20 p-4"
          >
            <p className="font-bold">{activity.activity_type}</p>
            <p className="text-sm text-slate-300">
              {activity.description}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              {new Date(activity.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
