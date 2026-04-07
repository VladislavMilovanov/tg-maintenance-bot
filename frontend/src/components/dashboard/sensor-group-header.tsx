import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { SensorGroupDetailResponse } from "@/lib/api/types";

interface SensorGroupHeaderProps {
  sensorGroup: SensorGroupDetailResponse;
  equipmentId: string;
}

export function SensorGroupHeader({ sensorGroup, equipmentId }: SensorGroupHeaderProps) {
  const key = sensorGroup.status as EquipmentStatusType;
  const config = statusConfig[key] ?? statusConfig.unknown;

  return (
    <div className="space-y-2">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm text-muted-foreground flex-wrap" aria-label="Хлебные крошки">
        <Link href="/dashboard" className="hover:text-foreground transition-colors shrink-0">
          Дашборд
        </Link>
        <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 opacity-50" />
        <Link
          href={`/dashboard/equipment/${equipmentId}`}
          className="hover:text-foreground transition-colors truncate max-w-[160px]"
          title={sensorGroup.equipment.name}
        >
          {sensorGroup.equipment.name}
        </Link>
        <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 opacity-50" />
        <span
          className="text-foreground font-medium truncate max-w-[200px]"
          title={sensorGroup.name}
          aria-current="page"
        >
          {sensorGroup.name}
        </span>
      </nav>

      {/* Title row */}
      <div className="flex items-start gap-3 flex-wrap">
        <div className="flex-1 min-w-0">
          <h2 className="text-xl font-bold text-foreground">{sensorGroup.name}</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Тип: <span className="font-medium text-foreground">{sensorGroup.group_type}</span>
          </p>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold ${config.bgColor} ${config.color} flex-shrink-0`}
        >
          <span className={`h-2 w-2 rounded-full ${config.dotColor}`} />
          {config.label}
        </span>
      </div>
    </div>
  );
}
