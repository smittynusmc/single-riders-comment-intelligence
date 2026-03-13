import * as React from "react";

import { cn } from "@/lib/utils/cn";

const variants = {
  primary: "bg-ink text-white hover:bg-ink/90",
  secondary: "bg-white text-ink ring-1 ring-ink/10 hover:bg-mist",
  ghost: "text-ink hover:bg-ink/5",
  danger: "bg-coral text-white hover:bg-coral/90",
};

export function Button({
  className,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof variants }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-gold/40 disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
