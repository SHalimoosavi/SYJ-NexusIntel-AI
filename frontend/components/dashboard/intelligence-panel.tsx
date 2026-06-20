"use client";

type Props = {
  report: {
    overall_score: number;
    security_score: number;
    seo_score: number;
    trust_score: number;
    recommendations: string[];
  };

  risks: {
    risk_count: number;
    risks: string[];
  };
};

export default function IntelligencePanel({
  report,
  risks,
}: Props) {
  return (
    <div
      className="
        glass-premium
        rounded-3xl
        p-6
      "
    >
      <h2 className="text-2xl font-black mb-6">
        Intelligence Center
      </h2>

      <div className="grid grid-cols-2 gap-4 mb-6">

        <div>
          <p className="text-slate-400">
            Overall Score
          </p>

          <h3 className="text-3xl font-bold">
            {report.overall_score}
          </h3>
        </div>

        <div>
          <p className="text-slate-400">
            Trust Score
          </p>

          <h3 className="text-3xl font-bold">
            {report.trust_score}
          </h3>
        </div>

        <div>
          <p className="text-slate-400">
            Security
          </p>

          <h3 className="text-2xl font-bold">
            {report.security_score}
          </h3>
        </div>

        <div>
          <p className="text-slate-400">
            SEO
          </p>

          <h3 className="text-2xl font-bold">
            {report.seo_score}
          </h3>
        </div>

      </div>

      <div className="mb-6">

        <h3 className="font-bold mb-3">
          Recommendations
        </h3>

        <ul className="space-y-2">

          {report.recommendations.map(
            (item) => (
              <li
                key={item}
                className="
                  text-sm
                  text-slate-300
                "
              >
                • {item}
              </li>
            )
          )}

        </ul>

      </div>

      <div>

        <h3
          className="
            font-bold
            mb-3
            text-red-400
          "
        >
          Risk Center
        </h3>

        <ul className="space-y-2">

          {risks.risks.map(
            (risk) => (
              <li
                key={risk}
                className="
                  text-sm
                  text-slate-300
                "
              >
                • {risk}
              </li>
            )
          )}

        </ul>

      </div>
    </div>
  );
}
