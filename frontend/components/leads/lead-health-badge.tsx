type Props = {
  score: number;
};

export default function LeadHealthBadge({
  score,
}: Props) {
  let label = "Weak";
  let color = "bg-red-500";

  if (score >= 90) {
    label = "Excellent";
    color = "bg-green-500";
  } else if (score >= 70) {
    label = "Good";
    color = "bg-cyan-500";
  } else if (score >= 50) {
    label = "Average";
    color = "bg-yellow-500";
  }

  return (
    <span
      className={`px-2 py-1 rounded-lg text-xs text-white ${color}`}
    >
      {label} ({score})
    </span>
  );
}
