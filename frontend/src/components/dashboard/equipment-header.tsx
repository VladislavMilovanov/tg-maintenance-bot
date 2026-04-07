import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { EquipmentDetailResponse } from "@/lib/api/types";

interface EquipmentHeaderProps {
  equipment: EquipmentDetailResponse;
}

function formatDuration(hours: number | null): string | null {
  if (hours === null) return null;
  if (hours >= 24) return `${Math.floor(hours / 24)} дн.`;
  return `${hours} ч.`;
}

export function EquipmentHeader({ equipment }: EquipmentHeaderProps) {
  const key = equipment.current_status as EquipmentStatusType;
  const config = statusConfig[key] ?? statusConfig.unknown;
  const duration = formatDuration(equipment.duration_in_status_hours);

  return (
    <div className="space-y-2">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground flex-wrap" aria-label="Хлебные крошки">
        <Link href="/dashboard" className="hover:text-foreground transition-colors">
          Дашборд
        </Link>
        <ChevronRight className="h-3.5 w-3.5 flex-shrink-0" />
        <span className="truncate max-w-[160px]">{equipment.location.name}</span>
        <ChevronRight className="h-3.5 w-3.5 flex-shrink-0" />
        <span className="text-foreground font-medium truncate max-w-[200px]">{equipment.name}</span>
      </nav>

      {/* Title row */}
      <div className="flex items-start gap-3 flex-wrap">
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-foreground">
            {equipment.name}
            {equipment.equipment_code && (
              <span className="ml-2 text-sm font-mono font-normal text-muted-foreground">
                {equipment.equipment_code}
              </span>
            )}
          </h2>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold ${config.bgColor} ${config.color}`}
          >
            <span className={`h-2 w-2 rounded-full ${config.dotColor}`} />
            {config.label}
          </span>
          {duration && (
            <span className="text-xs text-muted-foreground">
              В этом статусе {duration}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
