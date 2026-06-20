"use client";

import { useEffect } from "react";
import { useMotionValue } from "framer-motion";
import { animate } from "framer-motion";
import { useState } from "react";

type Props = {
  value: number;
};

export default function AnimatedCounter({
  value,
}: Props) {

  const [display, setDisplay] =
    useState(0);

  const motionValue =
    useMotionValue(0);

  useEffect(() => {

    const controls = animate(
      motionValue,
      value,
      {
        duration: 1.5,
      }
    );

    const unsubscribe =
      motionValue.on(
        "change",
        (latest) => {
          setDisplay(
            Math.floor(latest)
          );
        }
      );

    return () => {
      controls.stop();
      unsubscribe();
    };

  }, [value, motionValue]);

  return <>{display}</>;
}
