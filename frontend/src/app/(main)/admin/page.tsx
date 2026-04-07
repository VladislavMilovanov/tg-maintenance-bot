import { AdminDashboard } from "@/components/admin/admin-dashboard";

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-foreground">Панель администратора</h1>
      <AdminDashboard />
    </div>
  );
}
