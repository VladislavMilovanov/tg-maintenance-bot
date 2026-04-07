"use client";

import { Server, AlertTriangle, AlertCircle, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AdminKpis } from "@/lib/api/types";

interface KpiCardsProps {
  kpis: AdminKpis;
}

interface KpiCardConfig {
  label: string;
  value: number;
  icon: React.ElementType;
  iconClass: string;
}

export function KpiCards({ kpis }: KpiCardsProps) {
  const cards: KpiCardConfig[] = [
    {
      label: "Всего оборудования",
      value: kpis.total_equipment,
      icon: Server,
      iconClass: "text-muted-foreground",
    },
    {
      label: "Критических",
      value: kpis.critical_count,
      icon: AlertTriangle,
      iconClass: "text-red-500",
    },
    {
      label: "Предупреждений",
      value: kpis.warning_count,
      icon: AlertCircle,
      iconClass: "text-yellow-500",
    },
    {
      label: "Клиентов",
      value: kpis.clients_count,
      icon: Users,
      iconClass: "text-muted-foreground",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.label}
              </CardTitle>
              <Icon className={`h-4 w-4 ${card.iconClass}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-foreground">
                {card.value}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
