"use client";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DailyStatusEntry } from "@/lib/api/types";

interface DailyStatusChartProps {
  data: DailyStatusEntry[];
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    const day = String(d.getDate()).padStart(2, "0");
    const month = String(d.getMonth() + 1).padStart(2, "0");
    return `${day}.${month}`;
  } catch {
    return dateStr;
  }
}

const SERIES = [
  { key: "normal", color: "#22c55e", label: "Норма" },
  { key: "warning", color: "#eab308", label: "Внимание" },
  { key: "critical", color: "#ef4444", label: "Критично" },
  { key: "unknown", color: "#9ca3af", label: "Неизвестно" },
] as const;

export function DailyStatusChart({ data }: DailyStatusChartProps) {
  const chartData = data.map((entry) => ({
    ...entry,
    label: formatDate(entry.date),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Состояние за 14 дней</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart
            data={chartData}
            margin={{ top: 4, right: 16, left: 0, bottom: 4 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="hsl(var(--border))"
              opacity={0.5}
            />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
                fontSize: "12px",
                color: "hsl(var(--foreground))",
              }}
              labelStyle={{ color: "hsl(var(--muted-foreground))" }}
            />
            <Legend
              wrapperStyle={{ fontSize: "12px", color: "hsl(var(--muted-foreground))" }}
            />
            {SERIES.map(({ key, color, label }) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                name={label}
                stackId="stack"
                fill={color}
                stroke={color}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
