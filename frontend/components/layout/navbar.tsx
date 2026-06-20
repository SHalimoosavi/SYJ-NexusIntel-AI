export default function Navbar() {
  return (
    <div className="glass flex items-center justify-between px-6 py-4 rounded-2xl">
      <div>
        <h2 className="text-xl font-semibold">
          Command Center
        </h2>
        <p className="text-sm text-slate-400">
          Business Intelligence Platform
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="h-10 w-10 rounded-full bg-emerald-500" />
      </div>
    </div>
  );
}
