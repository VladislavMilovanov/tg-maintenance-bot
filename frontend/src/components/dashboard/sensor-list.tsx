import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { SensorEntry } from "@/lib/api/types";

interface SensorListProps {
  sensors: SensorEntry[];
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

export function SensorList({ sensors }: SensorListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Датчики</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {sensors.length === 0 ? (
          <p className="px-6 py-4 text-sm text-muted-foreground">Датчики не найдены</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Название</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Тип</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Последнее наблюдение</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {sensors.map((sensor) => (
                  <tr key={sensor.sensor_id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-3 font-medium text-foreground">{sensor.name}</td>
                    <td className="px-6 py-3 text-muted-foreground">{sensor.sensor_type}</td>
                    <td className="px-6 py-3 text-muted-foreground whitespace-nowrap">
                      {formatDate(sensor.last_observed_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
