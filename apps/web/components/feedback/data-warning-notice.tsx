export function DataWarningNotice({ message }: { message: string }) {
  return (
    <div className="rounded-3xl border border-gold/35 bg-gold/10 px-5 py-4 text-sm text-ink shadow-sm">
      <p className="font-semibold">Some data could not be loaded.</p>
      <p className="mt-1 text-slate">{message}</p>
    </div>
  );
}
