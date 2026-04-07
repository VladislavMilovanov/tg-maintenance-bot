import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { WorstPerformerEntry } from "@/lib/api/types";

interface WorstPerformersProps {
  items: WorstPerformerEntry[];
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateStr;
  }
}

export function WorstPerformers({ items }: WorstPerformersProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Проблемное оборудование</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {items.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">
            Проблемного оборудования нет
          </p>
        ) : (
          <div className="divide-y divide-border">
            {items.map((item) => {
              const key = item.current_status as EquipmentStatusType;
              const config = statusConfig[key] ?? statusConfig.unknown;
              return (
                <div key={item.equipment_id} className="flex items-center justify-between px-6 py-3 gap-3">
                  <div className="min-w-0 flex-1">
                    <Link
                      href={`/dashboard/equipment/${item.equipment_id}`}
                      className="text-sm font-medium text-foreground hover:underline truncate block"
                    >
                      {item.name}
                    </Link>
                    <p className="text-xs text-muted-foreground truncate">{item.location_name}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
                      {config.label}
                    </span>
                    <span className="text-xs text-muted-foreground">{formatDate(item.last_changed_at)}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
