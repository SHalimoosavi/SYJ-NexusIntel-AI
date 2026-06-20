import Sidebar from "./sidebar";
import Topbar from "./topbar";

export default function CommandLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="
        min-h-screen
        bg-slate-950
        text-white
      "
    >
      <div className="flex">
        <Sidebar />

        <main className="flex-1 p-6">
          <Topbar />

          <div className="mt-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
