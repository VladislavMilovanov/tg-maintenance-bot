import { SensorGroupDetail } from "@/components/dashboard/sensor-group-detail";

export default async function SensorGroupPage({
  params,
}: {
  params: Promise<{ equipment_id: string; sensor_group_id: string }>;
}) {
  const { equipment_id, sensor_group_id } = await params;
  return (
    <SensorGroupDetail
      equipmentId={equipment_id}
      sensorGroupId={sensor_group_id}
    />
  );
}
