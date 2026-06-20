"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

type KPIProps = {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
};

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
}: KPIProps) {
  return (
    <motion.div
      whileHover={{
        scale: 1.03,
        y: -4,
      }}
      className="
        glass
        rounded-3xl
        p-6
        border
        border-white/10
        backdrop-blur-xl
      "
    >
      <div className="flex items-center justify-between">
        <p className="text-slate-400 text-sm">
          {title}
        </p>

        <Icon
          size={22}
          className="text-emerald-400"
        />
      </div>

      <h2 className="text-4xl font-bold mt-4">
        {value}
      </h2>

      <p className="text-slate-500 text-sm mt-2">
        {subtitle}
      </p>
    </motion.div>
  );
}
