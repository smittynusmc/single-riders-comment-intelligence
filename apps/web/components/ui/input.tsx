import * as React from "react";

import { cn } from "@/lib/utils/cn";

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-2xl border border-ink/10 bg-white px-4 text-sm text-ink shadow-sm outline-none transition placeholder:text-slate focus:border-gold/40 focus:ring-2 focus:ring-gold/20",
        className,
      )}
      {...props}
    />
  );
}
