"use client";

import { motion } from "framer-motion";

type Props = {
  briefing: {
    pipeline_value: number;
    forecast_revenue: number;
    annual_projection: number;
    executive_summary: string;
    risk_summary: string;
    recommendation: string;
  };
};

export default function ExecutiveBriefing({
  briefing,
}: Props) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        glass-premium
        rounded-3xl
        p-8
      "
    >
      <div className="flex items-center justify-between">

        <div>
          <p className="text-emerald-400 text-sm">
            EXECUTIVE AI
          </p>

          <h2
            className="
              text-3xl
              font-black
              mt-2
            "
          >
            Intelligence Briefing
          </h2>
        </div>

        <div
          className="
            h-4
            w-4
            rounded-full
            bg-emerald-500
            animate-pulse
          "
        />

      </div>

      <div
        className="
          grid
          gap-4
          md:grid-cols-3
          mt-8
        "
      >

        <div>
          <p className="text-slate-400">
            Pipeline
          </p>

          <h3 className="text-3xl font-bold">
            ${briefing.pipeline_value}
          </h3>
        </div>

        <div>
          <p className="text-slate-400">
            Forecast
          </p>

          <h3 className="text-3xl font-bold">
            ${briefing.forecast_revenue}
          </h3>
        </div>

        <div>
          <p className="text-slate-400">
            Annual Projection
          </p>

          <h3 className="text-3xl font-bold">
            ${briefing.annual_projection}
          </h3>
        </div>

      </div>

      <div className="mt-8 space-y-6">

        <div>
          <p className="text-emerald-400 text-sm">
            Executive Summary
          </p>

          <p className="text-slate-300 mt-2">
            {briefing.executive_summary}
          </p>
        </div>

        <div>
          <p className="text-red-400 text-sm">
            Risk Analysis
          </p>

          <p className="text-slate-300 mt-2">
            {briefing.risk_summary}
          </p>
        </div>

        <div>
          <p className="text-cyan-400 text-sm">
            Recommendation
          </p>

          <p className="text-slate-300 mt-2">
            {briefing.recommendation}
          </p>
        </div>

      </div>
    </motion.div>
  );
}
