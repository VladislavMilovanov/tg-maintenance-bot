// ── Enums ──────────────────────────────────────────────────────────────────

export type Channel = "telegram" | "web";

export type UserRole = "user" | "admin" | "operator" | "engineer";

export type EquipmentStatus = "normal" | "warning" | "critical" | "unknown";

// ── Shared building blocks ─────────────────────────────────────────────────

export interface ErrorDetail {
  field: string;
  issue: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: ErrorDetail[] | null;
  trace_id?: string | null;
}

export interface ClientUser {
  external_id: string;
  display_name?: string | null;
  role?: UserRole | null;
}

export interface LocationBrief {
  location_id: string;
  name: string;
}

export interface ActorBrief {
  actor_id: string;
  display_name: string | null;
}

export interface EquipmentBrief {
  equipment_id: string;
  name: string;
}

// ── Auth ───────────────────────────────────────────────────────────────────

export interface AuthLoginRequest {
  telegram_username: string;
}

export interface AuthLoginResponse {
  access_token: string;
  token_type: string;
  actor_id: string;
  display_name: string | null;
  role: string;
}

export interface AuthMeResponse {
  actor_id: string;
  external_id: string;
  display_name: string | null;
  role: UserRole | null;
}

// ── Assistant ──────────────────────────────────────────────────────────────

export interface AssistantMessagePayload {
  text: string;
}

export interface EquipmentContext {
  equipment_id?: string | null;
  sensor_ids?: string[];
  sensor_group_ids?: string[];
}

export interface AssistantMessageRequest {
  channel: Channel;
  user: ClientUser;
  conversation_id?: string | null;
  message: AssistantMessagePayload;
  equipment_context?: EquipmentContext | null;
}

export interface AssistantResponseMeta {
  fallback_used: boolean;
  trace_id?: string | null;
}

export interface ContextUsed {
  equipment_id?: string | null;
  sensor_ids?: string[];
  sensor_group_ids?: string[];
  sources?: string[];
}

export interface AssistantMessageResponse {
  answer: string;
  conversation_id: string;
  context_used?: ContextUsed | null;
  meta: AssistantResponseMeta;
}

// ── Equipment State Records ────────────────────────────────────────────────

export interface StateRecordAuthor {
  external_id: string;
  display_name?: string | null;
  role?: UserRole | null;
}

export interface EquipmentStateRecordCreateRequest {
  equipment_id: string;
  status: EquipmentStatus;
  comment?: string | null;
  idempotency_key?: string | null;
  observed_at: string;
  channel: Channel;
  author: StateRecordAuthor;
}

export interface EquipmentStateRecordResponse {
  record_id: string;
  equipment_id: string;
  status: EquipmentStatus;
  comment: string | null;
  observed_at: string;
  created_at: string;
  channel: Channel;
  author: StateRecordAuthor;
}

// ── Dashboard ──────────────────────────────────────────────────────────────

export interface StatusSummary {
  normal: number;
  warning: number;
  critical: number;
  unknown: number;
}

export interface TrendInfo {
  critical_delta: number;
  warning_delta: number;
  direction: string;
}

export interface DailyStatusEntry {
  date: string;
  normal: number;
  warning: number;
  critical: number;
  unknown: number;
}

export interface WorstPerformerEntry {
  equipment_id: string;
  name: string;
  current_status: EquipmentStatus;
  location_name: string;
  last_changed_at: string | null;
  duration_in_status_hours: number | null;
  last_comment: string | null;
}

export interface PlantOverviewResponse {
  plant_status: EquipmentStatus;
  status_summary: StatusSummary;
  daily_history: DailyStatusEntry[];
  worst_performers: WorstPerformerEntry[];
  trend?: TrendInfo | null;
}

export interface StateChangeEntry {
  equipment_id: string;
  equipment_name: string;
  old_status: EquipmentStatus | null;
  new_status: EquipmentStatus;
  changed_at: string;
}

export interface StateFeedResponse {
  items: StateChangeEntry[];
  total: number;
}

export interface ActionFeedEntry {
  record_id: string;
  equipment_id: string;
  equipment_name: string;
  status: EquipmentStatus;
  comment: string | null;
  author_name: string | null;
  observed_at: string;
  channel: Channel;
}

export interface ActionFeedResponse {
  items: ActionFeedEntry[];
  total: number;
}

// ── Equipment ──────────────────────────────────────────────────────────────

export interface SensorGroupBrief {
  sensor_group_id: string;
  name: string;
  status: EquipmentStatus;
  group_type: string;
}

export interface SensorEntry {
  sensor_id: string;
  name: string;
  sensor_type: string;
  last_observed_at: string | null;
}

export interface EquipmentListItem {
  equipment_id: string;
  name: string;
  equipment_code: string | null;
  current_status: EquipmentStatus;
  location: LocationBrief;
  owner: ActorBrief | null;
}

export interface EquipmentListResponse {
  items: EquipmentListItem[];
  total: number;
}

export interface EquipmentDetailResponse {
  equipment_id: string;
  name: string;
  equipment_code: string | null;
  current_status: EquipmentStatus;
  location: LocationBrief;
  owner: ActorBrief | null;
  maintenance_progress: number | null;
  top_nodes: SensorGroupBrief[];
  sensor_groups_count: number;
  last_state_change: string | null;
  duration_in_status_hours: number | null;
}

export interface EquipmentHistoryEntry {
  record_id: string;
  status: EquipmentStatus;
  comment: string | null;
  observed_at: string;
  created_at: string;
  channel: Channel;
  author: StateRecordAuthor;
}

export interface EquipmentHistoryResponse {
  items: EquipmentHistoryEntry[];
  total: number;
}

// ── Sensor Groups ──────────────────────────────────────────────────────────

export interface SensorGroupDetailResponse {
  sensor_group_id: string;
  name: string;
  status: EquipmentStatus;
  group_type: string;
  image_url: string | null;
  equipment: EquipmentBrief;
  sensors: SensorEntry[];
}

// ── Locations ──────────────────────────────────────────────────────────────

export interface LocationTreeNode {
  location_id: string;
  name: string;
  location_type: string;
  status: EquipmentStatus;
  equipment_count: number;
  children: LocationTreeNode[];
}

export interface LocationTreeResponse {
  locations: LocationTreeNode[];
}

// ── Admin ──────────────────────────────────────────────────────────────────

export interface AdminKpis {
  total_equipment: number;
  critical_count: number;
  warning_count: number;
  clients_count: number;
}

export interface ActivityChartEntry {
  date: string;
  actions_count: number;
}

export interface ProgressMatrixEntry {
  location_name: string;
  total: number;
  normal: number;
  warning: number;
  critical: number;
}

export interface AdminDashboardResponse {
  kpis: AdminKpis;
  activity_chart: ActivityChartEntry[];
  progress_matrix: ProgressMatrixEntry[];
}

export interface AdminClientEntry {
  actor_id: string;
  external_id: string;
  display_name: string | null;
  role: UserRole | null;
  equipment_count: number;
  last_activity_at: string | null;
}

export interface AdminClientsResponse {
  items: AdminClientEntry[];
  total: number;
}

export interface AdminEventEntry {
  event_type: string;
  equipment_id: string | null;
  equipment_name: string | null;
  actor_name: string | null;
  description: string;
  occurred_at: string;
}

export interface AdminEventsResponse {
  items: AdminEventEntry[];
  total: number;
}

// ── Pagination helper ──────────────────────────────────────────────────────

export interface PaginationParams {
  limit?: number;
  offset?: number;
}

// ── Text-to-SQL ────────────────────────────────────────────────────────────

export interface TextToSqlRequest {
  question: string;
}

export interface TextToSqlResponse {
  answer: string;
  sql_query: string | null;
  row_count: number;
  columns: string[];
  rows: unknown[][];
  error: string | null;
}
