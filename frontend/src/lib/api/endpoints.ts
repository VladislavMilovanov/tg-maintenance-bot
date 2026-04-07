import { request } from "./client";
import type {
  AuthLoginRequest,
  AuthLoginResponse,
  AuthMeResponse,
  AssistantMessageRequest,
  AssistantMessageResponse,
  EquipmentStateRecordCreateRequest,
  EquipmentStateRecordResponse,
  PlantOverviewResponse,
  StateFeedResponse,
  ActionFeedResponse,
  EquipmentListResponse,
  EquipmentDetailResponse,
  EquipmentHistoryResponse,
  SensorGroupDetailResponse,
  LocationTreeResponse,
  AdminDashboardResponse,
  AdminClientsResponse,
  AdminEventsResponse,
  TextToSqlRequest,
  TextToSqlResponse,
  EquipmentStatus,
  PaginationParams,
} from "./types";

// ── Helpers ────────────────────────────────────────────────────────────────

function buildQuery(
  params: Record<string, string | number | undefined | null>,
): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null,
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
}

// ── Auth ───────────────────────────────────────────────────────────────────

export async function login(data: AuthLoginRequest): Promise<AuthLoginResponse> {
  return request<AuthLoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getMe(): Promise<AuthMeResponse> {
  return request<AuthMeResponse>("/api/v1/auth/me");
}

// ── Assistant ──────────────────────────────────────────────────────────────

export async function createAssistantMessage(
  data: AssistantMessageRequest,
): Promise<AssistantMessageResponse> {
  return request<AssistantMessageResponse>("/api/v1/assistant/messages", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── Equipment State Records ────────────────────────────────────────────────

export async function createEquipmentStateRecord(
  data: EquipmentStateRecordCreateRequest,
): Promise<EquipmentStateRecordResponse> {
  return request<EquipmentStateRecordResponse>("/api/v1/equipment-state-records", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ── Dashboard ──────────────────────────────────────────────────────────────

export async function getPlantOverview(params?: {
  location_id?: string | null;
}): Promise<PlantOverviewResponse> {
  const qs = buildQuery({ location_id: params?.location_id });
  return request<PlantOverviewResponse>(`/api/v1/dashboard/plant${qs}`);
}

export async function getStateFeed(
  params?: PaginationParams,
): Promise<StateFeedResponse> {
  const qs = buildQuery({ limit: params?.limit, offset: params?.offset });
  return request<StateFeedResponse>(`/api/v1/dashboard/state-feed${qs}`);
}

export async function getActionFeed(
  params?: PaginationParams,
): Promise<ActionFeedResponse> {
  const qs = buildQuery({ limit: params?.limit, offset: params?.offset });
  return request<ActionFeedResponse>(`/api/v1/dashboard/action-feed${qs}`);
}

// ── Equipment ──────────────────────────────────────────────────────────────

export async function listEquipment(params?: {
  location_id?: string | null;
  status?: EquipmentStatus | null;
  limit?: number;
  offset?: number;
}): Promise<EquipmentListResponse> {
  const qs = buildQuery({
    location_id: params?.location_id,
    status: params?.status,
    limit: params?.limit,
    offset: params?.offset,
  });
  return request<EquipmentListResponse>(`/api/v1/equipment${qs}`);
}

export async function getEquipmentDetail(
  equipmentId: string,
): Promise<EquipmentDetailResponse> {
  return request<EquipmentDetailResponse>(`/api/v1/equipment/${equipmentId}`);
}

export async function getEquipmentHistory(
  equipmentId: string,
  params?: PaginationParams,
): Promise<EquipmentHistoryResponse> {
  const qs = buildQuery({ limit: params?.limit, offset: params?.offset });
  return request<EquipmentHistoryResponse>(
    `/api/v1/equipment/${equipmentId}/history${qs}`,
  );
}

// ── Sensor Groups ──────────────────────────────────────────────────────────

export async function getSensorGroupDetail(
  sensorGroupId: string,
): Promise<SensorGroupDetailResponse> {
  return request<SensorGroupDetailResponse>(
    `/api/v1/sensor-groups/${sensorGroupId}`,
  );
}

// ── Locations ──────────────────────────────────────────────────────────────

export async function getLocationTree(): Promise<LocationTreeResponse> {
  return request<LocationTreeResponse>("/api/v1/locations/tree");
}

// ── Admin ──────────────────────────────────────────────────────────────────

export async function getAdminDashboard(): Promise<AdminDashboardResponse> {
  return request<AdminDashboardResponse>("/api/v1/admin/dashboard");
}

export async function listAdminClients(
  params?: PaginationParams,
): Promise<AdminClientsResponse> {
  const qs = buildQuery({ limit: params?.limit, offset: params?.offset });
  return request<AdminClientsResponse>(`/api/v1/admin/clients${qs}`);
}

export async function listAdminEvents(
  params?: PaginationParams,
): Promise<AdminEventsResponse> {
  const qs = buildQuery({ limit: params?.limit, offset: params?.offset });
  return request<AdminEventsResponse>(`/api/v1/admin/events${qs}`);
}

// ── Text-to-SQL ────────────────────────────────────────────────────────────

export async function queryTextToSql(
  data: TextToSqlRequest,
): Promise<TextToSqlResponse> {
  return request<TextToSqlResponse>("/api/v1/query/text-to-sql", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
