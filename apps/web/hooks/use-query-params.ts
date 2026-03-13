"use client";

import { useSearchParams } from "next/navigation";

export function useQueryParams() {
  const searchParams = useSearchParams();
  return Object.fromEntries(searchParams.entries());
}
