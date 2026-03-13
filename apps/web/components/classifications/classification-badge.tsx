import { Badge } from "@/components/ui/badge";
import { formatTitle } from "@/lib/utils/format";

export function ClassificationBadge({
  value,
  tone = "default",
}: {
  value: string;
  tone?: "default" | "success" | "warning" | "danger";
}) {
  return <Badge variant={tone}>{formatTitle(value)}</Badge>;
}
