"use client";

type Memory = {
  id: number;
  overall_score: number;
  priority: string;
  created_at: string;
};

type Props = {
  memories: Memory[];
};

export default function MemoryTimeline({
  memories,
}: Props) {
  return (
    <div
      className="
        glass-premium
        rounded-3xl
        p-6
      "
    >
      <h2
        className="
          text-2xl
          font-black
          mb-6
        "
      >
        Memory Timeline
      </h2>

      <div className="space-y-4">

        {memories.map((memory) => (

          <div
            key={memory.id}
            className="
              border-l-2
              border-emerald-500
              pl-4
            "
          >
            <p className="font-bold">
              Score {memory.overall_score}
            </p>

            <p
              className="
                text-sm
                text-slate-400
              "
            >
              {memory.priority}
            </p>

            <p
              className="
                text-xs
                text-slate-500
              "
            >
              {memory.created_at}
            </p>

          </div>

        ))}

      </div>
    </div>
  );
}
