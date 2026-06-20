"use client";

import { motion } from "framer-motion";

type Props = {
  children: React.ReactNode;
};

export default function StaggerContainer({
  children,
}: Props) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: 0.12,
          },
        },
      }}
    >
      {children}
    </motion.div>
  );
}
