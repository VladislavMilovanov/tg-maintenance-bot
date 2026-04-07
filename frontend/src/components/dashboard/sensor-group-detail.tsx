"use client";

import { useState, useEffect } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { getSensorGroupDetail } from "@/lib/api/endpoints";
import type { SensorGroupDetailResponse } from "@/lib/api/types";
import { SensorGroupHeader } from "./sensor-group-header";
import { NodeImage } from "./node-image";
import { SensorList } from "./sensor-list";
import { AiDiagnosis } from "./ai-diagnosis";

interface SensorGroupDetailProps {
  equipmentId: string;
  sensorGroupId: string;
}

export function SensorGroupDetail({ equipmentId, sensorGroupId }: SensorGroupDetailProps) {
  const [sensorGroup, setSensorGroup] = useState<SensorGroupDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getSensorGroupDetail(sensorGroupId)
      .then((data) => {
        if (!cancelled) {
          setSensorGroup(data);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Ошибка загрузки узла");
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [sensorGroupId]);

  if (loading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-16 w-full rounded-xl" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Skeleton className="h-64 w-full rounded-xl" />
          <Skeleton className="h-64 w-full rounded-xl" />
        </div>
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-6 py-8 text-center">
        <p className="text-sm font-medium text-destructive">{error}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Проверьте соединение с сервером и попробуйте обновить страницу.
        </p>
      </div>
    );
  }

  if (!sensorGroup) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <SensorGroupHeader sensorGroup={sensorGroup} equipmentId={equipmentId} />

      {/* Image + Sensor list in 2 cols on large screens */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <NodeImage imageUrl={sensorGroup.image_url} name={sensorGroup.name} />
        <SensorList sensors={sensorGroup.sensors} />
      </div>

      {/* AI Diagnosis */}
      <AiDiagnosis
        equipmentId={equipmentId}
        sensorGroupId={sensorGroupId}
        status={sensorGroup.status}
      />
    </div>
  );
}
