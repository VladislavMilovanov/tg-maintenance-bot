import Link from "next/link";
import { CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { statusConfig } from "@/lib/status-colors";
import type { EquipmentStatusType } from "@/lib/status-colors";
import type { SensorGroupBrief } from "@/lib/api/types";

interface TopNodesProps {
  nodes: SensorGroupBrief[];
  equipmentId: string;
}

export function TopNodes({ nodes, equipmentId }: TopNodesProps) {
  const allNormal = nodes.length > 0 && nodes.every((n) => n.status === "normal");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Узлы оборудования</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {nodes.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">Нет узлов</p>
        ) : (
          <>
            {allNormal && (
              <div className="mx-6 mb-2 mt-3 flex items-center gap-2 text-green-600 dark:text-green-400">
                <CheckCircle className="h-4 w-4 shrink-0" />
                <span className="text-sm">Все узлы в норме</span>
              </div>
            )}
            <div className="divide-y divide-border">
            {nodes.map((node) => {
              const key = node.status as EquipmentStatusType;
              const config = statusConfig[key] ?? statusConfig.unknown;
              const borderColor = config.borderColor;
              return (
                <Link
                  key={node.sensor_group_id}
                  href={`/dashboard/equipment/${equipmentId}/nodes/${node.sensor_group_id}`}
                  className={`flex items-center justify-between px-6 py-4 hover:bg-muted/50 transition-colors border-l-4 ${borderColor}`}
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-base font-medium text-foreground truncate">{node.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{node.group_type}</p>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${config.bgColor} ${config.color} flex-shrink-0 ml-3`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
                    {config.label}
                  </span>
                </Link>
              );
            })}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
