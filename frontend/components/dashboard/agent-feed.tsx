"use client";

import { motion } from "framer-motion";

const agents = [
  {
    name: "Research Agent",
    status: "ANALYZING",
  },
  {
    name: "Opportunity Agent",
    status: "SCORING",
  },
  {
    name: "Sales Agent",
    status: "FOLLOWING UP",
  },
  {
    name: "Executive Agent",
    status: "FORECASTING",
  },
];

export default function AgentFeed() {
  return (
    <div
      className="
        rounded-3xl
        border
        border-white/10
        bg-white/[0.03]
        backdrop-blur-2xl
        p-6
        shadow-[0_0_40px_rgba(16,185,129,0.08)]
      "
    >
      <h2
        className="
          text-xl
          font-bold
          mb-6
        "
      >
        Agent Activity Center
      </h2>

      <div className="space-y-4">

        {agents.map(
          (agent) => (
            <motion.div
              key={agent.name}
              whileHover={{
                scale: 1.02,
              }}
              className="
                flex
                items-center
                justify-between
                rounded-2xl
                border
                border-white/10
                bg-black/20
                p-4
              "
            >
              <div>

                <p className="font-medium">
                  {agent.name}
                </p>

                <p
                  className="
                    text-sm
                    text-slate-400
                  "
                >
                  Active
                </p>

              </div>

              <div
                className="
                  flex
                  items-center
                  gap-3
                "
              >

                <motion.div
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [0.4, 1, 0.4],
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 2,
                  }}
                  className="
                    h-3
                    w-3
                    rounded-full
                    bg-emerald-500
                  "
                />

                <span
                  className="
                    text-emerald-400
                    text-sm
                    font-semibold
                  "
                >
                  {agent.status}
                </span>

              </div>

            </motion.div>
          )
        )}

      </div>
    </div>
  );
}
