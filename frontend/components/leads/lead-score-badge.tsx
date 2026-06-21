type Props = {
  leadScore?: number;
  priority?: string;
  probability?: number;
};

export default function LeadScoreBadge({
  leadScore = 0,
  priority = "COLD",
  probability = 0,
}: Props) {
  const priorityColor =
    priority === "HOT"
      ? "bg-red-500"
      : priority === "WARM"
      ? "bg-yellow-500"
      : "bg-slate-500";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span
          className={`px-2 py-1 rounded-lg text-xs font-bold text-black ${priorityColor}`}
        >
          {priority}
        </span>

        <span className="text-xs text-slate-400">
          {probability}% Win Rate
        </span>
      </div>

      <div>
        <div className="flex justify-between text-xs mb-1">
          <span>Lead Score</span>
          <span>{leadScore}/100</span>
        </div>

        <div className="w-full bg-slate-800 rounded-full h-2">
          <div
            className="bg-emerald-500 h-2 rounded-full"
            style={{
              width: `${leadScore}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}
