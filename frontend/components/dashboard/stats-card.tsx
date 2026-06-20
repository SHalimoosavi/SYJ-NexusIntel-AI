"use client";

import { motion } from "framer-motion";

type Props = {
  title: string;
  value: string;
};

export default function StatsCard({
  title,
  value,
}: Props) {
  return (
    <motion.div
      whileHover={{
        scale: 1.03,
      }}
      className="glass neon rounded-3xl p-6"
    >
      <p className="text-slate-400 text-sm">
        {title}
      </p>

      <h3 className="text-4xl font-bold mt-3">
        {value}
      </h3>
    </motion.div>
  );
}
