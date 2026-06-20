"use client";

import { motion } from "framer-motion";

import AnimatedCounter from "./animated-counter";

type Props = {
  title: string;
  value: string | number;
  subtitle: string;
  icon: any;
};

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
}: Props) {

  const numericValue =
    Number(
      String(value)
        .replace("$", "")
        .replace(",", "")
    );

  const isNumber =
    !Number.isNaN(
      numericValue
    );

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
      whileHover={{
        y: -5,
      }}
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
      <div className="flex justify-between">

        <div>

          <p className="text-slate-400">
            {title}
          </p>

          <h3
            className="
              text-4xl
              font-black
              mt-3
            "
          >
            {isNumber ? (
              <>
                {String(value)
                  .includes("$")
                  ? "$"
                  : ""}
                <AnimatedCounter
                  value={
                    numericValue
                  }
                />
              </>
            ) : (
              value
            )}
          </h3>

          <p
            className="
              text-sm
              text-slate-500
              mt-2
            "
          >
            {subtitle}
          </p>

        </div>

        <Icon
          size={34}
          className="
            text-emerald-400
          "
        />

      </div>
    </motion.div>
  );
}
