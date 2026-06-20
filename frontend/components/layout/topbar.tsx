"use client";

import { motion } from "framer-motion";

export default function Topbar() {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: -30,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.5,
        delay: 0.15,
      }}
      className="
        rounded-3xl
        border
        border-white/10
        bg-white/[0.03]
        backdrop-blur-2xl
        p-5
        flex
        justify-between
        items-center
      "
    >
      <div>
        <h2
          className="
            text-2xl
            font-black
          "
        >
          AI Command Center
        </h2>

        <p className="text-slate-400">
          Autonomous Business Intelligence
        </p>
      </div>

      <div
        className="
          flex
          items-center
          gap-2
        "
      >
        <div
          className="
            h-3
            w-3
            rounded-full
            bg-emerald-500
            animate-pulse
          "
        />

        <span
          className="
            text-emerald-400
          "
        >
          Online
        </span>

      </div>
    </motion.div>
  );
}
