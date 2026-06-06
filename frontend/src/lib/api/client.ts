"use client";

/**
 * Canonical API base URL resolver.
 *
 * Reads the single canonical variable NEXT_PUBLIC_API_BASE_URL.
 *
 * Behavior by environment:
 *  - development (NEXT_PUBLIC_APP_ENV == "development" or unset):
 *    If NEXT_PUBLIC_API_BASE_URL is not set, falls back to http://localhost:8000
 *    for convenient local development.
 *  - staging / production / any other value of NEXT_PUBLIC_APP_ENV:
 *    If NEXT_PUBLIC_API_BASE_URL is not set, logs a fatal error and returns
 *    an empty string so every API call fails with a clear network error
 *    rather than silently routing to localhost.
 *
 * NEXT_PUBLIC_API_URL is also checked as a fallback for backward compatibility
 * during migration from the old variable name.
 */
function getApiBaseUrl(): string {
  // Canonical variable
  let url = process.env.NEXT_PUBLIC_API_BASE_URL;

  // Backward-compat fallback during migration
  if (!url) {
    url = process.env.NEXT_PUBLIC_API_URL;
  }

  if (url) return url;

  const env = process.env.NEXT_PUBLIC_APP_ENV || "development";

  // Allow localhost fallback only in local / development environments
  if (env === "local" || env === "development") {
    return "http://localhost:8000";
  }

  // Staging / production — a missing API URL is a fatal configuration error.
  // This makes the problem visible immediately rather than silently proxying
  // to localhost.
  console.error(
    `[API Client] Fatal: NEXT_PUBLIC_API_BASE_URL is not set ` +
      `(environment="${env}"). API calls will fail. ` +
      `Set NEXT_PUBLIC_API_BASE_URL to a valid backend URL.`,
  );
  return "";
}

const API_BASE = getApiBaseUrl();

// Export for testing
export { getApiBaseUrl };

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    request_id: string;
  };
}

export class ApiClientError extends Error {
  public code: string;
  public details: Record<string, unknown>;
  public requestId: string;

  constructor(err: ApiError["error"]) {
    super(err.message);
    this.name = "ApiClientError";
    this.code = err.code;
    this.details = err.details;
    this.requestId = err.request_id;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function setToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("access_token");
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: { skipAuth?: boolean }
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (!options?.skipAuth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      error: { code: "UNKNOWN", message: "Unknown error", details: {}, request_id: "" },
    }));
    throw new ApiClientError(errorData.error);
  }

  return response.json();
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
};

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  display_name?: string;
  preferred_locale: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export async function register(email: string, password: string, displayName?: string) {
  const res = await request<TokenResponse>(
    "POST",
    "/api/v1/auth/register",
    { email, password, display_name: displayName },
    { skipAuth: true }
  );
  setToken(res.access_token);
  return res;
}

export async function login(email: string, password: string) {
  const res = await request<TokenResponse>(
    "POST",
    "/api/v1/auth/login",
    { email, password },
    { skipAuth: true }
  );
  setToken(res.access_token);
  return res;
}

export function logout() {
  clearToken();
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

export async function getCurrentUser() {
  return api.get<UserResponse>("/api/v1/me");
}

export async function updateProfile(data: { display_name?: string; preferred_locale?: string }) {
  return api.patch<UserResponse>("/api/v1/me", data);
}

// ---------------------------------------------------------------------------
// Domains
// ---------------------------------------------------------------------------

export interface DomainSummary {
  id: string;
  slug: string;
  name: string;
  description?: string;
  icon?: string;
  sort_order: number;
  trainer_count: number;
}

export interface TrainerSummary {
  id: string;
  trainer_product_id: string;
  slug: string;
  name: string;
  description?: string;
  product_type: string;
}

export interface DomainDetail {
  id: string;
  slug: string;
  name: string;
  description?: string;
  icon?: string;
  trainers: TrainerSummary[];
}

export async function getDomains() {
  return api.get<DomainSummary[]>("/api/v1/domains");
}

export async function getDomain(slug: string) {
  return api.get<DomainDetail>(`/api/v1/domains/${slug}`);
}

// ---------------------------------------------------------------------------
// Trainers
// ---------------------------------------------------------------------------

export interface TrainerDetail {
  id: string;
  trainer_product_id: string;
  slug: string;
  name: string;
  description?: string;
  product_type: string;
  target_audience?: string[];
  supported_locales?: string[];
  default_locale?: string;
  status: string;
  scenario_count: number;
  is_enrolled: boolean;
}

export interface EnrollResponse {
  enrollment_id: string;
  status: string;
  message: string;
}

export async function getTrainer(slug: string) {
  return api.get<TrainerDetail>(`/api/v1/trainers/${slug}`);
}

export async function enrollTrainer(slug: string) {
  return api.post<EnrollResponse>(`/api/v1/trainers/${slug}/enroll`);
}

// ---------------------------------------------------------------------------
// Scenarios
// ---------------------------------------------------------------------------

export interface ScenarioSummary {
  id: string;
  scenario_id: string;
  title_key: string;
  goal_key: string;
  difficulty: string;
  estimated_duration_minutes: number;
  track?: string;
  module?: string;
}

export interface ScenarioDetail {
  id: string;
  scenario_id: string;
  title_key: string;
  goal_key: string;
  trainer_product_id: string;
  difficulty: string;
  estimated_duration_minutes: number;
  target_skills?: string[];
  user_role: string;
  ai_role: string;
  steps?: ScenarioStep[];
  hints?: string[];
  status: string;
}

export interface ScenarioStep {
  step_id: string;
  order: number;
  prompt_key: string;
  expected_actions?: string[];
}

export async function getTrainerScenarios(trainerSlug: string) {
  return api.get<ScenarioSummary[]>(`/api/v1/trainers/${trainerSlug}/scenarios`);
}

export async function getScenario(scenarioId: string) {
  return api.get<ScenarioDetail>(`/api/v1/scenarios/${scenarioId}`);
}

// ---------------------------------------------------------------------------
// Runtime
// ---------------------------------------------------------------------------

export interface StartScenarioResponse {
  session_id: string;
  attempt_id: string;
  scenario: ScenarioDetail;
  status: string;
}

export interface SubmitMessageResponse {
  message_id: string;
  status: string;
}

export interface CompleteSessionResponse {
  attempt_id: string;
  status: string;
  message: string;
}

export async function startScenario(scenarioId: string) {
  return api.post<StartScenarioResponse>(`/api/v1/scenarios/${scenarioId}/start`);
}

export async function submitMessage(sessionId: string, content: string) {
  return api.post<SubmitMessageResponse>(`/api/v1/sessions/${sessionId}/messages`, { content });
}

export async function completeSession(sessionId: string) {
  return api.post<CompleteSessionResponse>(`/api/v1/sessions/${sessionId}/complete`);
}

// ---------------------------------------------------------------------------
// Evaluations
// ---------------------------------------------------------------------------

export interface CriterionResult {
  criterion_id: string;
  score: number;
  evidence: string;
  comment: string;
  improvement: string;
}

export interface EvaluationResult {
  id: string;
  attempt_id: string;
  overall_score: number;
  passed: boolean;
  criteria: CriterionResult[];
  strengths: string[];
  weak_points: string[];
  critical_errors: string[];
  next_recommendation?: {
    action: string;
    description: string;
  };
  confidence: number;
  ai_model_used?: string;
  ai_cost_usd?: number;
  ai_latency_ms?: number;
  validation_status: string;
}

export async function evaluateAttempt(attemptId: string) {
  return api.post<EvaluationResult>(`/api/v1/attempts/${attemptId}/evaluate`);
}

export async function getEvaluation(attemptId: string) {
  return api.get<EvaluationResult>(`/api/v1/attempts/${attemptId}/evaluation`);
}

// ---------------------------------------------------------------------------
// Progress
// ---------------------------------------------------------------------------

export interface SkillScore {
  skill_id: string;
  skill_name: string;
  score: number;
  level: string;
  attempts_count: number;
}

export interface ProgressSummary {
  trainer_slug: string;
  trainer_name: string;
  average_score: number;
  completed_scenarios: number;
  total_attempts: number;
  readiness_status: string;
  skill_scores: SkillScore[];
}

export async function getAllProgress() {
  return api.get<{ progress_list: ProgressSummary[] }>("/api/v1/me/progress");
}

export async function getTrainerProgress(trainerSlug: string) {
  return api.get<ProgressSummary>(`/api/v1/me/progress/${trainerSlug}`);
}

// ---------------------------------------------------------------------------
// Activity System Types
// ---------------------------------------------------------------------------

export interface ActivityResponse {
  activity_id: string;
  module_id: string;
  activity_type: 'single_choice' | 'multiple_choice' | 'numeric' | 'fill_blanks' | 'matching';
  evaluation_mode: string;
  difficulty: string;
  title_key: string;
  description_key: string | null;
  payload: Record<string, unknown>;
  order: number;
  version: string;
}

export interface ActivityStartResponse {
  activity_id: string;
  activity_type: string;
  title_key: string;
  description_key: string | null;
  difficulty: string;
  module_id: string;
  prompt: Record<string, unknown>;
}

export interface ActivitySubmitRequest {
  activity_id: string;
  answer: unknown;
  idempotency_key?: string;
}

export interface ActivitySubmitResponse {
  attempt_id: string;
  activity_id: string;
  status: 'correct' | 'partial' | 'incorrect';
  score: number;
  passed: boolean;
  feedback: Record<string, unknown> | null;
  explanation_key: string;
  evaluation_mode: string;
  is_retry: boolean;
}

export interface ModuleActivitiesResponse {
  module_id: string;
  activities: ActivityResponse[];
  total_count: number;
}

// --- Activity Endpoints ---

export async function getModuleActivities(trainerSlug: string, moduleId: string): Promise<ModuleActivitiesResponse> {
  return api.get<ModuleActivitiesResponse>(`/api/v1/trainers/${trainerSlug}/modules/${moduleId}/activities`);
}

export async function startActivity(trainerSlug: string, activityId: string): Promise<ActivityStartResponse> {
  return api.get<ActivityStartResponse>(`/api/v1/trainers/${trainerSlug}/activities/${activityId}/start`);
}

export async function submitActivity(trainerSlug: string, body: ActivitySubmitRequest): Promise<ActivitySubmitResponse> {
  return api.post<ActivitySubmitResponse>(`/api/v1/trainers/${trainerSlug}/activities/submit`, body);
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export async function sendAnalyticsEvent(
  eventType: string,
  data?: {
    session_id?: string;
    trainer_slug?: string;
    scenario_id?: string;
    properties?: Record<string, unknown>;
  }
) {
  try {
    await api.post("/api/v1/analytics/events", {
      event_type: eventType,
      ...data,
    });
  } catch {
    // Analytics failures should never break the UI
  }
}
