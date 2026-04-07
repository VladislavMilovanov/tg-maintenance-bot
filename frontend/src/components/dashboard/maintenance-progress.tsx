import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface MaintenanceProgressProps {
  progress: number | null;
  dueAt: string | null;
  completedAt: string | null;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

function getProgressColor(progress: number, dueAt: string | null): string {
  if (!dueAt) return "bg-green-500";
  const now = Date.now();
  const due = new Date(dueAt).getTime();
  const diff = due - now;
  const dayMs = 24 * 60 * 60 * 1000;

  if (diff < 0) return "bg-red-500"; // overdue
  if (diff < 7 * dayMs) return "bg-yellow-500"; // < 7 days
  return "bg-green-500";
}

export function MaintenanceProgress({ progress, dueAt, completedAt }: MaintenanceProgressProps) {
  const pct = progress ?? 0;
  const barColor = getProgressColor(pct, dueAt);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Техническое обслуживание</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress bar */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-muted-foreground">Прогресс</span>
            <span className="font-semibold">{pct}%</span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-muted overflow-hidden">
            <div
              role="progressbar"
              aria-valuenow={Math.min(pct, 100)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`Прогресс технического обслуживания: ${pct}%`}
              className={`h-full rounded-full transition-all ${barColor}`}
              style={{ width: `${Math.min(pct, 100)}%` }}
            />
          </div>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Срок выполнения</p>
            <p className="text-sm font-medium">{formatDate(dueAt)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Выполнено</p>
            <p className="text-sm font-medium">{formatDate(completedAt)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
