"use client";

import { useEffect, useState } from "react";

const API_BASE =
  "https://syj-nexusintel-ai-production.up.railway.app";

type Activity = {
  id: number;
  lead_id: number;
  activity_type: string;
  description: string | null;
  created_at: string;
};

type Props = {
  leadId: number;
};

export default function ActivityTimeline({
  leadId,
}: Props) {
  const [activities, setActivities] =
    useState<Activity[]>([]);

  async function loadActivities() {
    try {
      const response =
        await fetch(
          `${API_BASE}/activities/${leadId}`
        );

      const data =
        await response.json();

      setActivities(data);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    loadActivities();
  }, [leadId]);

  return (
    <div className="glass rounded-3xl p-6">
      <h2 className="text-2xl font-black mb-4">
        Activity Timeline
      </h2>

      <div className="space-y-4">
        {activities.map(
          (activity) => (
            <div
              key={activity.id}
              className="rounded-xl bg-black/20 p-4"
            >
              <p className="font-bold">
                {
                  activity.activity_type
                }
              </p>

              <p className="text-sm text-slate-300">
                {
                  activity.description
                }
              </p>

              <p className="text-xs text-slate-500 mt-2">
                {new Date(
                  activity.created_at
                ).toLocaleString()}
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
