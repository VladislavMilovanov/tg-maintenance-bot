"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";
import type { ProgressMatrixEntry } from "@/lib/api/types";

interface ProgressMatrixProps {
  data: ProgressMatrixEntry[];
}

interface StatusCellProps {
  count: number;
  total: number;
  colorClass: string;
  bgClass: string;
}

function StatusCell({ count, total, colorClass, bgClass }: StatusCellProps) {
  if (count === 0) {
    return (
      <span className="text-muted-foreground text-sm">0</span>
    );
  }
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-sm font-medium px-2 py-0.5 rounded-md",
        colorClass,
        bgClass,
      )}
    >
      {count}
      <span className="text-xs opacity-70">({pct}%)</span>
    </span>
  );
}

export function ProgressMatrix({ data }: ProgressMatrixProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Матрица прогресса</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {data.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-muted-foreground">
            Нет данных
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Локация</TableHead>
                <TableHead>Всего</TableHead>
                <TableHead>Норма</TableHead>
                <TableHead>Внимание</TableHead>
                <TableHead>Критично</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((entry) => (
                <TableRow key={entry.location_name}>
                  <TableCell className="font-medium">
                    {entry.location_name}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {entry.total}
                  </TableCell>
                  <TableCell>
                    <StatusCell
                      count={entry.normal}
                      total={entry.total}
                      colorClass="text-green-700 dark:text-green-400"
                      bgClass="bg-green-100 dark:bg-green-900/30"
                    />
                  </TableCell>
                  <TableCell>
                    <StatusCell
                      count={entry.warning}
                      total={entry.total}
                      colorClass="text-yellow-700 dark:text-yellow-400"
                      bgClass="bg-yellow-100 dark:bg-yellow-900/30"
                    />
                  </TableCell>
                  <TableCell>
                    <StatusCell
                      count={entry.critical}
                      total={entry.total}
                      colorClass="text-red-700 dark:text-red-400"
                      bgClass="bg-red-100 dark:bg-red-900/30"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
