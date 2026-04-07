export type EquipmentStatusType = "normal" | "warning" | "critical" | "unknown";

export const statusConfig: Record<
  EquipmentStatusType,
  { label: string; color: string; bgColor: string; dotColor: string; borderColor: string }
> = {
  normal: {
    label: "Норма",
    color: "text-green-600 dark:text-green-400",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    dotColor: "bg-green-500",
    borderColor: "border-l-green-500",
  },
  warning: {
    label: "Внимание",
    color: "text-yellow-600 dark:text-yellow-400",
    bgColor: "bg-yellow-100 dark:bg-yellow-900/30",
    dotColor: "bg-yellow-500",
    borderColor: "border-l-yellow-500",
  },
  critical: {
    label: "Критично",
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-100 dark:bg-red-900/30",
    dotColor: "bg-red-500",
    borderColor: "border-l-red-500",
  },
  unknown: {
    label: "Неизвестно",
    color: "text-gray-600 dark:text-gray-400",
    bgColor: "bg-gray-100 dark:bg-gray-900/30",
    dotColor: "bg-gray-500",
    borderColor: "border-l-gray-500",
  },
};
