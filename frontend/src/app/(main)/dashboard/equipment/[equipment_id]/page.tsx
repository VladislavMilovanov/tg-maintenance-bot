import { EquipmentDetail } from "@/components/dashboard/equipment-detail";

export default async function EquipmentPage({
  params,
}: {
  params: Promise<{ equipment_id: string }>;
}) {
  const { equipment_id } = await params;
  return <EquipmentDetail equipmentId={equipment_id} />;
}
