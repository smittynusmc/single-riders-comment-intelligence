import type { PaginatedResponse } from "@single-riders/shared-types";

export type FallbackPaginatedResponse<T> = PaginatedResponse<T> & {
  warning?: string;
};

export function buildUnavailablePaginatedResponse<T>(warning: string, limit: number, offset: number): FallbackPaginatedResponse<T> {
  return {
    items: [],
    meta: { total: 0, limit, offset },
    warning,
  };
}
