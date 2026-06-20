"use client";

import Link from "next/link";

import {
  LayoutDashboard,
  Users,
  Brain,
  Activity,
  Database,
  Search,
  Settings,
} from "lucide-react";

import { motion } from "framer-motion";

const items = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Leads",
    href: "/leads",
    icon: Users,
  },
  {
    name: "Agents",
    href: "/agents",
    icon: Brain,
  },
  {
    name: "Memory",
    href: "/memory",
    icon: Database,
  },
  {
    name: "Opportunities",
    href: "/opportunities",
    icon: Activity,
  },
  {
    name: "Intelligence",
    href: "/intelligence",
    icon: Search,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <motion.aside
      initial={{
        x: -80,
        opacity: 0,
      }}
      animate={{
        x: 0,
        opacity: 1,
      }}
      transition={{
        duration: 0.6,
      }}
      className="
        w-72
        min-h-screen
        border-r
        border-white/10
        bg-black/30
        backdrop-blur-2xl
        p-6
        hidden
        lg:flex
        flex-col
      "
    >
      <motion.div
        initial={{
          opacity: 0,
          y: -20,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          delay: 0.2,
        }}
        className="mb-10"
      >
        <h1
          className="
            text-2xl
            font-black
            text-emerald-400
          "
        >
          SYJ NexusIntel
        </h1>

        <p
          className="
            text-xs
            text-slate-400
            mt-1
          "
        >
          AI Command Center
        </p>
      </motion.div>

      <div className="space-y-3">

        {items.map(
          (item, index) => {

            const Icon =
              item.icon;

            return (
              <motion.div
                key={item.name}
                initial={{
                  opacity: 0,
                  x: -15,
                }}
                animate={{
                  opacity: 1,
                  x: 0,
                }}
                transition={{
                  delay:
                    0.1 +
                    index * 0.08,
                }}
              >
                <Link
                  href={item.href}
                >
                  <motion.div
                    whileHover={{
                      x: 8,
                      scale: 1.02,
                    }}
                    whileTap={{
                      scale: 0.98,
                    }}
                    className="
                      flex
                      items-center
                      gap-3
                      rounded-2xl
                      px-4
                      py-3
                      cursor-pointer
                      border
                      border-transparent
                      hover:border-emerald-500/20
                      hover:bg-emerald-500/5
                      transition-all
                    "
                  >
                    <Icon
                      size={18}
                      className="
                        text-emerald-400
                      "
                    />

                    <span>
                      {item.name}
                    </span>

                  </motion.div>
                </Link>
              </motion.div>
            );
          }
        )}

      </div>

      <div className="mt-auto">

        <motion.div
          animate={{
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
          }}
          className="
            rounded-2xl
            border
            border-emerald-500/20
            bg-emerald-500/5
            p-4
          "
        >
          <p
            className="
              text-xs
              text-slate-400
            "
          >
            SYSTEM STATUS
          </p>

          <div
            className="
              flex
              items-center
              gap-2
              mt-2
            "
          >
            <div
              className="
                h-2
                w-2
                rounded-full
                bg-emerald-500
              "
            />

            <span
              className="
                text-sm
                text-emerald-400
              "
            >
              All Agents Active
            </span>

          </div>
        </motion.div>

      </div>

    </motion.aside>
  );
}
