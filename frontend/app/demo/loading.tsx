export default function Loading() {
  return (
    <div
      className="
        min-h-screen
        flex
        items-center
        justify-center
      "
    >
      <div
        className="
          h-16
          w-16
          rounded-full
          border-4
          border-emerald-500
          border-t-transparent
          animate-spin
        "
      />
    </div>
  );
}
