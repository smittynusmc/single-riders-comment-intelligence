import * as React from "react";

import { cn } from "@/lib/utils/cn";

const variants = {
  default: "bg-ink/5 text-ink",
  success: "bg-spruce/10 text-spruce",
  warning: "bg-gold/15 text-gold",
  danger: "bg-coral/10 text-coral",
};

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: keyof typeof variants }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium uppercase tracking-[0.18em]",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
