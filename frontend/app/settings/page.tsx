import CommandLayout from "@/components/layout/command-layout";

export default function SettingsPage() {
  return (
    <CommandLayout>
      <h1 className="text-4xl font-black">
        Settings
      </h1>

      <p className="text-slate-400 mt-3">
        Platform Configuration
      </p>
    </CommandLayout>
  );
}
