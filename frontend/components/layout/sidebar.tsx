"use client";

import {
  LayoutDashboard,
  Users,
  Search,
  Shield,
  FileText,
  Settings,
} from "lucide-react";

const items = [
  {
    name: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Leads",
    icon: Users,
  },
  {
    name: "Intelligence",
    icon: Search,
  },
  {
    name: "Technology",
    icon: Shield,
  },
  {
    name: "Reports",
    icon: FileText,
  },
  {
    name: "Settings",
    icon: Settings,
  },
];

export default function Sidebar() {
  return (
    <aside className="glass w-64 border-r border-white/10 p-6 hidden lg:flex flex-col">
      <div className="mb-10">
        <h1 className="text-xl font-bold text-emerald-400">
          SYJ NexusIntel
        </h1>
        <p className="text-xs text-slate-400">
          AI Command Center
        </p>
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.name}
              className="flex items-center gap-3 w-full p-3 rounded-xl hover:bg-white/5 transition"
            >
              <Icon size={18} />
              {item.name}
            </button>
          );
        })}
      </div>
    </aside>
  );
}
