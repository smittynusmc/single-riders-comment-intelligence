import { cn } from "@/lib/utils/cn";

export function PageHeader({
  title,
  description,
  className,
}: {
  title: string;
  description: string;
  className?: string;
}) {
  return (
    <div className={cn("mb-6 flex flex-col gap-2", className)}>
      <p className="text-xs uppercase tracking-[0.24em] text-slate">Internal Admin</p>
      <h2 className="font-display text-3xl font-semibold text-ink">{title}</h2>
      <p className="max-w-3xl text-sm leading-6 text-slate">{description}</p>
    </div>
  );
}
