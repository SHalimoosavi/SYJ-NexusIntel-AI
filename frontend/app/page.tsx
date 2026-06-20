import Sidebar from "@/components/layout/sidebar";
import Navbar from "@/components/layout/navbar";

import BentoGrid from "@/components/dashboard/bento-grid";

export default function Home() {
  return (
    <main className="gradient-bg min-h-screen flex">

      <Sidebar />

      <section className="flex-1 p-6">

        <Navbar />

        <div className="mt-8">

          <div className="mb-10">

            <h1 className="text-5xl font-bold">
              SYJ NexusIntel AI
            </h1>

            <p className="mt-3 text-slate-400">
              AI Powered Business Intelligence Platform
            </p>

          </div>

          <BentoGrid />

        </div>

      </section>

    </main>
  );
}
