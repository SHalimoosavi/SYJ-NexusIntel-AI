"use client";

import { motion } from "framer-motion";

type Props = {
  children: React.ReactNode;
  delay?: number;
};

export default function ScaleIn({
  children,
  delay = 0,
}: Props) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        scale: 0.9,
      }}
      animate={{
        opacity: 1,
        scale: 1,
      }}
      transition={{
        duration: 0.5,
        delay,
      }}
    >
      {children}
    </motion.div>
  );
}
