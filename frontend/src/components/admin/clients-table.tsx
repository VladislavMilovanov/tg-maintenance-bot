"use client";

import { useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { listAdminClients } from "@/lib/api/endpoints";
import type { AdminClientEntry, AdminClientsResponse } from "@/lib/api/types";

const PAGE_SIZE = 10;

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    return d.toLocaleString("ru-RU", {
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

function roleBadgeVariant(
  role: AdminClientEntry["role"],
): "default" | "secondary" | "outline" {
  if (role === "admin") return "default";
  if (role === "operator") return "secondary";
  return "outline";
}

function roleLabel(role: AdminClientEntry["role"]): string {
  const map: Record<string, string> = {
    admin: "Администратор",
    operator: "Оператор",
    engineer: "Инженер",
    user: "Пользователь",
  };
  return role ? (map[role] ?? role) : "—";
}

export function ClientsTable() {
  const [data, setData] = useState<AdminClientsResponse | null>(null);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPage = useCallback(async (pageIndex: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await listAdminClients({
        limit: PAGE_SIZE,
        offset: pageIndex * PAGE_SIZE,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки данных");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPage(page);
  }, [page, fetchPage]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Клиенты</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {error && (
          <div className="px-4 py-6 text-sm text-destructive">{error}</div>
        )}

        {loading && !data && (
          <div className="px-4 py-4 space-y-2">
            {Array.from({ length: PAGE_SIZE }).map((_, i) => (
              <Skeleton key={i} className="h-8 w-full" />
            ))}
          </div>
        )}

        {!error && (loading || data) && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Имя</TableHead>
                <TableHead>ID</TableHead>
                <TableHead>Роль</TableHead>
                <TableHead>Оборудование</TableHead>
                <TableHead>Последняя активность</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading && !data
                ? null
                : (data?.items ?? []).map((client) => (
                    <TableRow key={client.actor_id}>
                      <TableCell className="font-medium">
                        {client.display_name ?? "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground font-mono text-xs">
                        {client.external_id}
                      </TableCell>
                      <TableCell>
                        <Badge variant={roleBadgeVariant(client.role)}>
                          {roleLabel(client.role)}
                        </Badge>
                      </TableCell>
                      <TableCell>{client.equipment_count}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDate(client.last_activity_at)}
                      </TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
        )}

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-border">
          <span className="text-sm text-muted-foreground">
            Страница {page + 1} из {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0 || loading}
            >
              <ChevronLeft className="h-4 w-4" />
              Назад
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1 || loading}
            >
              Вперёд
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
