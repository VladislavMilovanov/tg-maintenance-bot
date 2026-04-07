import { PlantDashboard } from "@/components/dashboard/plant-dashboard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Обзор площадки</h1>
      <PlantDashboard />
    </div>
  );
}
