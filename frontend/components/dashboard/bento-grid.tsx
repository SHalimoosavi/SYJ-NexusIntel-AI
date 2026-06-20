"use client";

import { motion } from "framer-motion";

import StatsCard from "./stats-card";

export default function BentoGrid() {
  return (
    <div className="grid gap-6 lg:grid-cols-4">

      <StatsCard
        title="Total Leads"
        value="1,284"
      />

      <StatsCard
        title="Hot Leads"
        value="326"
      />

      <StatsCard
        title="Reports"
        value="84"
      />

      <StatsCard
        title="Scans"
        value="512"
      />

      <motion.div
        whileHover={{
          scale: 1.02,
        }}
        className="
          glass
          rounded-3xl
          p-6
          lg:col-span-2
          min-h-[240px]
        "
      >
        <h2 className="text-xl font-bold">
          Intelligence Engine
        </h2>

        <p className="mt-3 text-slate-400">
          Website Intelligence,
          OSINT Analysis,
          Lead Qualification
          and Security Scoring.
        </p>
      </motion.div>

      <motion.div
        whileHover={{
          scale: 1.02,
        }}
        className="
          glass
          rounded-3xl
          p-6
          min-h-[240px]
        "
      >
        <h2 className="text-xl font-bold">
          Technology Detection
        </h2>

        <p className="mt-3 text-slate-400">
          Framework and stack
          discovery engine.
        </p>
      </motion.div>

      <motion.div
        whileHover={{
          scale: 1.02,
        }}
        className="
          glass
          rounded-3xl
          p-6
          min-h-[240px]
        "
      >
        <h2 className="text-xl font-bold">
          Reports
        </h2>

        <p className="mt-3 text-slate-400">
          Generate PDF reports
          for clients instantly.
        </p>
      </motion.div>
    </div>
  );
}
