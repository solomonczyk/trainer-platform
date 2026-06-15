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

// ---------------------------------------------------------------------------
// Canonical Error Model
// ---------------------------------------------------------------------------

export interface AppError {
  code: string;
  message: string;
  status?: number;
  details?: Record<string, unknown>;
  correlationId?: string;
  retryable: boolean;
  fieldErrors?: Record<string, string[]>;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    request_id: string;
  };
}

/**
 * Normalize an unknown backend error payload into a safe AppError.
 *
 * Supports all response shapes used by the application:
 *   {"error": {"code":"...", "message":"...", ...}}
 *   {"detail": "string message"}
 *   {"detail": {"message":"...", "code":"..."}}
 *   {"errors": [{"message":"..."}]}
 *   NetworkError / non-JSON / empty response
 */
export function normalizeApiError(error: unknown): AppError {
  // Already an ApiClientError — extract its fields
  if (error instanceof ApiClientError) {
    return {
      code: error.code,
      message: error.message,
      details: error.details,
      correlationId: error.requestId,
      retryable: error.status ? error.status >= 500 : false,
    };
  }

  // Plain Error (TypeError, network failure, etc.)
  if (error instanceof Error) {
    const isNetwork =
      error.message?.includes('fetch') ||
      error.message?.includes('network') ||
      error.message?.includes('Failed to fetch') ||
      error.message?.includes('NetworkError') ||
      error.name === 'TypeError';
    return {
      code: isNetwork ? 'NETWORK_ERROR' : 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred',
      retryable: isNetwork,
      details: { name: error.name },
    };
  }

  // Non-Error object — attempt to parse as JSON error response
  if (error && typeof error === 'object') {
    const obj = error as Record<string, unknown>;

    // {"error": {"code":"...", "message":"...", ...}} — canonical backend format
    const errObj = obj.error;
    if (errObj && typeof errObj === 'object') {
      const e = errObj as Record<string, unknown>;
      return {
        code: String(e.code ?? 'UNKNOWN'),
        message: String(e.message ?? (e.detail as string) ?? 'Unknown error'),
        details: (e.details as Record<string, unknown>) ?? {},
        correlationId: String(e.request_id ?? ''),
        retryable: false,
      };
    }

    // {"detail": "string"} — FastAPI/Starlette HTTPException format
    if (typeof obj.detail === 'string') {
      return {
        code: 'HTTP_ERROR',
        message: obj.detail,
        retryable: false,
        details: {},
      };
    }

    // {"detail": {"message":"...", "code":"..."}}
    if (obj.detail && typeof obj.detail === 'object' && !Array.isArray(obj.detail)) {
      const d = obj.detail as Record<string, unknown>;
      return {
        code: String(d.code ?? 'DETAIL_ERROR'),
        message: String(d.message ?? d.detail ?? 'Unknown error'),
        details: d,
        retryable: false,
      };
    }

    // {"errors": [{"message": "..."}]}
    if (Array.isArray(obj.errors) && obj.errors.length > 0) {
      const msgs = obj.errors.map((e: unknown) => {
        if (e && typeof e === 'object') return String((e as Record<string, unknown>).message ?? '');
        return String(e);
      }).filter(Boolean);
      return {
        code: 'VALIDATION_ERROR',
        message: msgs.join('; ') || 'Validation error',
        fieldErrors: obj.errors.reduce((acc: Record<string, string[]>, e: unknown) => {
          if (e && typeof e === 'object') {
            const errItem = e as Record<string, unknown>;
            let field = errItem.field;
            if (!field && Array.isArray(errItem.loc)) {
              const locParts = errItem.loc as unknown[];
              field = locParts.length > 0 ? String(locParts[locParts.length - 1]) : undefined;
            }
            if (field && typeof field === 'string') {
              acc[field] = acc[field] || [];
              acc[field].push(String(errItem.message ?? 'Invalid'));
            }
          }
          return acc;
        }, {}),
        retryable: false,
      };
    }

    // Unknown object shape — attempt to extract anything useful
    const maybeMsg = obj.message ?? obj.error_message ?? obj.msg;
    if (maybeMsg) {
      return {
        code: typeof obj.code === 'string' ? obj.code : 'UNKNOWN_ERROR',
        message: typeof maybeMsg === 'string' ? maybeMsg : String(maybeMsg),
        status: typeof obj.status === 'number' ? obj.status : undefined,
        details: typeof obj.details === 'object' && obj.details !== null
          ? (obj.details as Record<string, unknown>)
          : undefined,
        retryable: typeof obj.retryable === 'boolean' ? obj.retryable : false,
      };
    }
  }

  // String or primitive error
  if (typeof error === 'string') {
    return {
      code: 'UNKNOWN_ERROR',
      message: error,
      retryable: false,
    };
  }

  // Fallback
  return {
    code: 'UNKNOWN',
    message: 'An unexpected error occurred',
    retryable: false,
  };
}

export class ApiClientError extends Error {
  public code: string;
  public details: Record<string, unknown>;
  public requestId: string;
  public status: number | undefined;

  /**
   * Safe constructor — never throws even if `err` is undefined/null/malformed.
   */
  constructor(err: unknown) {
    const normalized = normalizeApiError(err);
    super(normalized.message);
    this.name = "ApiClientError";
    this.code = normalized.code;
    this.details = normalized.details ?? {};
    this.requestId = normalized.correlationId ?? "";
    this.status = normalized.status;
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
    // Try to parse JSON body; fall back to status text
    const rawError: unknown = await response.json().catch(() => null);
    const normalized = normalizeApiError(rawError ?? response.statusText);
    // Preserve HTTP status for retryability detection
    normalized.status = response.status;
    throw new ApiClientError(normalized);
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
  email_verified: boolean;
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
// Email Verification
// ---------------------------------------------------------------------------

export async function verifyEmail(token: string) {
  return request<{ message: string; email_verified: boolean }>(
    "POST",
    "/api/v1/auth/verify-email",
    { token },
    { skipAuth: true }
  );
}

export async function resendVerification(email: string) {
  return request<{ message: string }>(
    "POST",
    "/api/v1/auth/resend-verification",
    { email },
    { skipAuth: true }
  );
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
  target_skills?: Array<string | { skill_id: string; weight: number }>;
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

// ---------------------------------------------------------------------------
// Human Review
// ---------------------------------------------------------------------------

export interface ReviewCaseSummary {
  case_id: string;
  candidate_id: string;
  review_handoff_id: string;
  validation_run_id: string;
  status: string;
  review_type: string;
  required_reviewer_role: string;
  created_by: string;
  created_at: string;
  opened_at: string | null;
  completed_at: string | null;
  version: number;
}

export interface AssignmentSummary {
  assignment_id: string;
  reviewer_user_id: string;
  reviewer_role: string;
  assigned_by: string;
  assigned_at: string;
  claimed_at: string | null;
  released_at: string | null;
  status: string;
  reason: string | null;
}

export interface DecisionSummary {
  decision_id: string;
  decision: string;
  reviewer_user_id: string;
  reviewer_role: string;
  reason: string;
  findings_json: Record<string, unknown> | null;
  candidate_hash: string;
  correlation_id: string | null;
  created_at: string;
}

export interface ReviewCaseDetail {
  case_id: string;
  candidate_id: string;
  review_handoff_id: string;
  validation_run_id: string;
  status: string;
  review_type: string;
  required_reviewer_role: string;
  created_by: string;
  created_at: string;
  opened_at: string | null;
  completed_at: string | null;
  version: number;
  candidate: Record<string, unknown> | null;
  assignments: AssignmentSummary[];
  decisions: DecisionSummary[];
}

export interface ReviewCaseListResponse {
  items: ReviewCaseSummary[];
  total: number;
}

export interface ReviewAssignRequest {
  reviewer_user_id: string;
  reviewer_role: string;
  reason?: string;
}

export interface ReviewClaimRequest {
  reason?: string;
}

export interface ReviewReleaseRequest {
  reason: string;
}

export interface ReviewAssignmentResponse {
  assignment_id: string;
  review_case_id: string;
  reviewer_user_id: string;
  reviewer_role: string;
  status: string;
  message: string;
}

export interface ReviewDecisionSubmit {
  decision: "APPROVED_FOR_PILOT_REVIEW" | "REJECTED" | "CHANGES_REQUESTED" | "ESCALATED";
  reason: string;
  findings_json?: Record<string, unknown>;
  evidence_confirmed: boolean;
}

export interface ReviewDecisionResponse {
  decision_id: string;
  review_case_id: string;
  candidate_id: string;
  decision: string;
  status: string;
  message: string;
}

export interface ReviewHistoryEntry {
  event_type: string;
  actor_id: string;
  actor_role: string | null;
  previous_status: string | null;
  new_status: string | null;
  reason: string | null;
  correlation_id: string | null;
  decision_id: string | null;
  event_timestamp: string;
}

export interface ReviewHistoryResponse {
  case_id: string;
  events: ReviewHistoryEntry[];
}

export async function createReviewCase(handoffId: string, reviewType = "expert_review") {
  return api.post<ReviewCaseSummary>("/api/v1/certification/review-cases", {
    handoff_id: handoffId,
    review_type: reviewType,
  });
}

export async function listReviewCases(params?: {
  status?: string;
  reviewer_user_id?: string;
  assigned_to?: string;
  skip?: number;
  limit?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set("status", params.status);
  if (params?.reviewer_user_id) searchParams.set("reviewer_user_id", params.reviewer_user_id);
  if (params?.assigned_to) searchParams.set("assigned_to", params.assigned_to);
  if (params?.skip) searchParams.set("skip", String(params.skip));
  if (params?.limit) searchParams.set("limit", String(params.limit));
  const qs = searchParams.toString();
  const path = `/api/v1/certification/review-cases${qs ? `?${qs}` : ""}`;
  return api.get<ReviewCaseListResponse>(path);
}

export async function getReviewCase(caseId: string) {
  return api.get<ReviewCaseDetail>(`/api/v1/certification/review-cases/${caseId}`);
}

export async function assignReviewer(caseId: string, body: ReviewAssignRequest) {
  return api.post<ReviewAssignmentResponse>(
    `/api/v1/certification/review-cases/${caseId}/assign`,
    body,
  );
}

export async function claimReview(caseId: string, body?: ReviewClaimRequest) {
  return api.post<ReviewAssignmentResponse>(
    `/api/v1/certification/review-cases/${caseId}/claim`,
    body || {},
  );
}

export async function releaseReviewer(caseId: string, body: ReviewReleaseRequest) {
  return api.post<ReviewAssignmentResponse>(
    `/api/v1/certification/review-cases/${caseId}/release`,
    body,
  );
}

export async function submitReviewDecision(caseId: string, body: ReviewDecisionSubmit) {
  return api.post<ReviewDecisionResponse>(
    `/api/v1/certification/review-cases/${caseId}/decision`,
    body,
  );
}

export async function getReviewHistory(caseId: string) {
  return api.get<ReviewHistoryResponse>(
    `/api/v1/certification/review-cases/${caseId}/history`,
  );
}

export async function getReviewEvidence(caseId: string) {
  return api.get<Record<string, unknown>>(
    `/api/v1/certification/review-cases/${caseId}/evidence`,
  );
}

// ---------------------------------------------------------------------------
// Quest Engine (Layer 010 — Immersive Simulator)
// ---------------------------------------------------------------------------

export interface QuestDefinition {
  quest_id: string;
  trainer_slug: string;
  version: string;
  locale: string;
  title_key: string;
  summary_key: string;
  learner_role_key: string;
  mission_key: string;
  setting_key: string;
  estimated_minutes: number;
  initial_state: Record<string, number>;
  steps: QuestStepDefinition[];
  outcomes: QuestOutcomeDefinition[];
  debrief_contract: { sections: string[]; skill_dimensions: string[] };
  characters: Array<{ id: string; name_key: string; role_key: string }>;
  tags: string[];
}

export interface QuestStepDefinition {
  step_id: string;
  step_type: 'single_choice' | 'multiple_choice' | 'free_text' | 'ordering' | 'matching' | 'evidence_select' | 'decision' | 'dialogue' | 'branching';
  story_context_key: string;
  prompt_key: string;
  interaction: Record<string, unknown>;
  evaluation_mode: 'deterministic' | 'ai_rubric' | 'hybrid';
  consequences: Record<string, number>;
  next_step_rules: { default?: string; by_choice?: Record<string, string>; by_flag?: Record<string, string> };
  learning_objectives: string[];
  skill_bindings: string[];
  feedback?: {
    incorrect_explanation_key?: string;
    correct_approach_key?: string;
    reinforcement_key?: string;
    partial_missing_key?: string;
    takeaway_key?: string;
  };
}

export interface QuestOutcomeDefinition {
  outcome_id: string;
  title_key: string;
  summary_key: string;
  min_decision_quality?: number;
  min_team_trust?: number;
  min_client_trust?: number;
  is_default?: boolean;
}

export interface QuestStartResponse {
  session_id: string;
  quest: QuestDefinition;
  current_step: QuestStepDefinition;
  narrative_state: Record<string, number>;
  status: string;
}

export interface QuestAnswerRequest {
  step_id: string;
  answer: unknown;
  idempotency_key?: string;
  locale?: string;
}

export interface QuestAnswerResponse {
  step_id: string;
  status: string;
  score?: number;
  max_score?: number;
  correct?: boolean;
  feedback_key?: string;
  feedback_data?: Record<string, unknown> | null;
  consequence_updates?: Record<string, number> | null;
  narrative_state: Record<string, number>;
  next_step?: QuestStepDefinition | null;
  next_step_id?: string;
  evaluation_mode?: string;
  timed_out: boolean;
  correlation_id?: string;
}

export interface QuestStepResponse {
  session_id: string;
  step: QuestStepDefinition;
  narrative_state: Record<string, number>;
  completed_step_ids: string[];
  answers: Record<string, unknown>;
  step_result?: { status: string; score?: number; max_score?: number; correct?: boolean; feedback_key?: string } | null;
}

export interface QuestOutcomeResponse {
  session_id: string;
  outcome_id: string;
  outcome_title_key: string;
  outcome_summary_key: string;
  narrative_state: Record<string, number>;
  debrief: Record<string, unknown>;
  status: string;
}

export interface QuestProgressResponse {
  session_found: boolean;
  session_id?: string;
  quest?: QuestDefinition;
  current_step?: QuestStepDefinition;
  narrative_state?: Record<string, number>;
  completed_step_ids?: string[];
  answers?: Record<string, unknown>;
  step_results?: Record<string, unknown>;
  status?: string;
  outcome?: { outcome_id: string; title_key: string; summary_key: string };
  debrief?: Record<string, unknown>;
}

export async function listQuests() {
  return api.get<{ quests: Record<string, unknown> }>('/api/v1/quests');
}

export async function startQuest(questId: string, locale = 'ru-RU') {
  return api.post<QuestStartResponse>(`/api/v1/quests/${questId}/start`, { locale });
}

export async function getQuestStep(sessionId: string) {
  return api.get<QuestStepResponse>(`/api/v1/quests/sessions/${sessionId}/step`);
}

export async function submitQuestAnswer(sessionId: string, body: QuestAnswerRequest) {
  return api.post<QuestAnswerResponse>(`/api/v1/quests/sessions/${sessionId}/answer`, body);
}

export async function retryQuestEvaluation(sessionId: string, body: { step_id: string; locale?: string; idempotency_key?: string }) {
  return api.post<QuestAnswerResponse>(`/api/v1/quests/sessions/${sessionId}/retry`, body);
}

export async function completeQuest(sessionId: string) {
  return api.post<QuestOutcomeResponse>(`/api/v1/quests/sessions/${sessionId}/complete`);
}

export async function getQuestProgress(sessionId: string) {
  return api.get<QuestProgressResponse>(`/api/v1/quests/sessions/${sessionId}/progress`);
}
