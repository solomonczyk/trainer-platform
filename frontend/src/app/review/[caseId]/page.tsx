"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  getCurrentUser,
  getReviewCase,
  claimReview,
  submitReviewDecision,
  getReviewHistory,
  getReviewEvidence,
  isAuthenticated,
  type UserResponse,
  type ReviewCaseDetail,
  type ReviewHistoryEntry,
} from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import {
  ClipboardList,
  Shield,
  AlertCircle,
  CheckCircle,
  ArrowLeft,
  UserCheck,
  History,
  Eye,
  FileText,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  ChevronUp,
  ChevronDown,
} from "lucide-react";

const STATUS_LABELS: Record<string, string> = {
  PENDING_ASSIGNMENT: "Pending Assignment",
  ASSIGNED: "Assigned",
  IN_REVIEW: "In Review",
  CHANGES_REQUESTED: "Changes Requested",
  REJECTED: "Rejected",
  APPROVED_FOR_PILOT_REVIEW: "Approved for Pilot Review",
  ESCALATED: "Escalated",
  CLOSED: "Closed",
};

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    PENDING_ASSIGNMENT: "bg-yellow-100 text-yellow-800",
    ASSIGNED: "bg-blue-100 text-blue-800",
    IN_REVIEW: "bg-purple-100 text-purple-800",
    CHANGES_REQUESTED: "bg-orange-100 text-orange-800",
    REJECTED: "bg-red-100 text-red-800",
    APPROVED_FOR_PILOT_REVIEW: "bg-green-100 text-green-800",
    ESCALATED: "bg-pink-100 text-pink-800",
    CLOSED: "bg-gray-100 text-gray-800",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
        colors[status] || "bg-gray-100 text-gray-800"
      }`}
    >
      {STATUS_LABELS[status] || status}
    </span>
  );
}

function Section({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Card padding="md" className="mb-4">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between text-left"
      >
        <CardTitle className="text-sm font-semibold text-gray-900">{title}</CardTitle>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>
      {open && <div className="mt-3">{children}</div>}
    </Card>
  );
}

function HistoryTimeline({ events }: { events: ReviewHistoryEntry[] }) {
  if (!events || events.length === 0) {
    return <p className="text-sm text-gray-400">No history events</p>;
  }

  return (
    <div className="space-y-3">
      {events.map((e, i) => (
        <div key={i} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className="h-2 w-2 rounded-full bg-primary-400" />
            {i < events.length - 1 && <div className="w-px flex-1 bg-gray-200" />}
          </div>
          <div className="flex-1 pb-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-900">
                {e.event_type.replace(/_/g, " ")}
              </span>
              <span className="text-xs text-gray-400">
                {new Date(e.event_timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-xs text-gray-500">
              by {e.actor_id} {e.actor_role ? `(${e.actor_role})` : ""}
            </p>
            {e.reason && <p className="mt-0.5 text-sm text-gray-600">{e.reason}</p>}
            {e.previous_status && e.new_status && (
              <p className="text-xs text-gray-400">
                {e.previous_status} → {e.new_status}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function ReviewCaseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const caseId = params.caseId as string;

  const [user, setUser] = useState<UserResponse | null>(null);
  const [authChecking, setAuthChecking] = useState(true);
  const [reviewCase, setReviewCase] = useState<ReviewCaseDetail | null>(null);
  const [history, setHistory] = useState<ReviewHistoryEntry[]>([]);
  const [evidence, setEvidence] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Decision form state
  const [decision, setDecision] = useState<string>("");
  const [reason, setReason] = useState("");
  const [findings, setFindings] = useState("");
  const [evidenceConfirmed, setEvidenceConfirmed] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push(`/login?redirect=/review/${caseId}`);
      return;
    }

    getCurrentUser()
      .then((u) => {
        setUser(u);
        const allowedRoles = [
          "platform_admin",
          "expert_reviewer",
          "psychometric_reviewer",
          "domain_owner",
          "qa_reviewer",
        ];
        if (!allowedRoles.includes(u.role)) {
          router.push("/");
        }
      })
      .catch(() => {
        router.push(`/login?redirect=/review/${caseId}`);
      })
      .finally(() => {
        setAuthChecking(false);
      });
  }, [router, caseId]);

  useEffect(() => {
    if (!user || !caseId) return;

    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [caseData, historyData, evidenceData] = await Promise.all([
          getReviewCase(caseId),
          getReviewHistory(caseId).catch(() => ({ case_id: caseId, events: [] })),
          getReviewEvidence(caseId).catch(() => null),
        ]);
        setReviewCase(caseData);
        setHistory(historyData.events || []);
        setEvidence(evidenceData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load review case");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [user, caseId]);

  const handleClaim = async () => {
    if (!caseId) return;
    setError(null);
    try {
      await claimReview(caseId);
      const caseData = await getReviewCase(caseId);
      setReviewCase(caseData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to claim review");
    }
  };

  const handleSubmitDecision = async () => {
    if (!caseId || !decision || !reason.trim() || !evidenceConfirmed) return;

    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      let parsedFindings: Record<string, unknown> | undefined;
      if (findings.trim()) {
        try {
          parsedFindings = JSON.parse(findings);
        } catch {
          parsedFindings = { notes: findings.trim() };
        }
      }

      const result = await submitReviewDecision(caseId, {
        decision: decision as "APPROVED_FOR_PILOT_REVIEW" | "REJECTED" | "CHANGES_REQUESTED" | "ESCALATED",
        reason: reason.trim(),
        findings_json: parsedFindings,
        evidence_confirmed: evidenceConfirmed,
      });

      setSubmitSuccess(result.message);
      // Reload case data
      const [caseData, historyData] = await Promise.all([
        getReviewCase(caseId),
        getReviewHistory(caseId).catch(() => ({ case_id: caseId, events: [] })),
      ]);
      setReviewCase(caseData);
      setHistory(historyData.events || []);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit decision");
    } finally {
      setSubmitting(false);
    }
  };

  if (authChecking) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Shield className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.forbidden")}</p>
        <Button onClick={() => router.push(`/login?redirect=/review/${caseId}`)}>
          {t("nav.login")}
        </Button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    );
  }

  if (error && !reviewCase) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="flex flex-col items-center gap-4">
          <AlertCircle className="h-12 w-12 text-red-400" />
          <p className="text-lg font-medium text-gray-900">Error loading case</p>
          <p className="text-sm text-gray-500">{error}</p>
          <Button variant="outline" onClick={() => router.push("/review")}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to Queue
          </Button>
        </div>
      </div>
    );
  }

  if (!reviewCase) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="flex flex-col items-center gap-4">
          <FileText className="h-12 w-12 text-gray-300" />
          <p className="text-lg font-medium text-gray-500">Case not found</p>
          <Button variant="outline" onClick={() => router.push("/review")}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to Queue
          </Button>
        </div>
      </div>
    );
  }

  const isMyAssignment = reviewCase.assignments?.some(
    (a) => a.reviewer_user_id === user.id && (a.status === "ASSIGNED" || a.status === "CLAIMED")
  );
  const isClaimedByMe = reviewCase.assignments?.some(
    (a) => a.reviewer_user_id === user.id && a.status === "CLAIMED"
  );
  const canClaim = reviewCase.status === "ASSIGNED" && isMyAssignment;
  const canDecide = reviewCase.status === "IN_REVIEW" && isClaimedByMe;
  const hasDecision = reviewCase.decisions && reviewCase.decisions.length > 0;

  const candidateData = reviewCase.candidate as Record<string, unknown> | null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push("/review")}
          className="mb-4 flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Queue
        </button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <ClipboardList className="h-6 w-6 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Review Case</h1>
              <StatusBadge status={reviewCase.status} />
            </div>
            <p className="text-sm font-mono text-gray-400">
              {reviewCase.case_id}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {canClaim && (
              <Button onClick={handleClaim}>
                <UserCheck className="mr-1.5 h-4 w-4" />
                Claim & Start Review
              </Button>
            )}
          </div>
        </div>
      </div>

      {submitError && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {submitError}
        </div>
      )}

      {submitSuccess && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          {submitSuccess}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-4">
          {/* Candidate Content */}
          <Section title="Candidate Content">
            {candidateData ? (
              <div className="space-y-3">
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Item Type
                  </span>
                  <p className="text-sm text-gray-900">
                    {String(candidateData.item_type || "N/A")}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Difficulty
                  </span>
                  <p className="text-sm text-gray-900">
                    {String(candidateData.difficulty || "N/A")}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Domain / Competency
                  </span>
                  <p className="text-sm text-gray-900">
                    {String(candidateData.domain_id || "N/A")} / {String(candidateData.competency_id || "N/A")}
                  </p>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Stem
                  </span>
                  <div className="mt-1 rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm text-gray-900 whitespace-pre-wrap">
                    {String(candidateData.stem || "N/A")}
                  </div>
                </div>
                {(() => {
                  const opts = candidateData.options;
                  if (!opts || !Array.isArray(opts)) return null;
                  return (
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Options
                      </span>
                      <div className="mt-1 space-y-1">
                        {(opts as Array<unknown>).map((opt: unknown, i: number) => (
                          <div
                            key={i}
                            className="rounded border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-900"
                          >
                            {typeof opt === "object" && opt !== null
                              ? String((opt as Record<string, unknown>).text || JSON.stringify(opt))
                              : String(opt)}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })()}
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Rationale
                  </span>
                  <p className="mt-1 text-sm text-gray-700">
                    {String(candidateData.rationale || "None provided")}
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-400">No candidate data available</p>
            )}
          </Section>

          {/* Validation Summary */}
          <Section title="Validation Summary">
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Validation Status:</span>{" "}
                {String(candidateData?.validation_status || "N/A")}
              </p>
              <p>
                <span className="font-medium">Candidate Status:</span>{" "}
                {String(candidateData?.status || "N/A")}
              </p>
            </div>
          </Section>

          {/* Evidence Panel */}
          <Section title="Evidence & Provenance">
            {evidence ? (
              <div className="space-y-3 text-sm">
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                    Candidate Hash
                  </span>
                  <p className="font-mono text-xs text-gray-700">
                    {String(evidence.candidate_hash || "N/A")}
                  </p>
                </div>
                {(() => {
                  const prov = evidence.provenance;
                  if (!prov || typeof prov !== "object") return null;
                  return (
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Provenance
                      </span>
                      <div className="mt-1 rounded bg-gray-50 p-2 font-mono text-xs text-gray-600">
                        {JSON.stringify(prov, null, 2)}
                      </div>
                    </div>
                  );
                })()}
                {(() => {
                  const sb = evidence.source_bindings;
                  if (!sb || !Array.isArray(sb)) return null;
                  return (
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Source Bindings
                      </span>
                      <div className="mt-1 space-y-1">
                        {(sb as Array<unknown>).map(
                          (s: unknown, i: number) => (
                            <div key={i} className="rounded bg-gray-50 p-2 text-xs text-gray-600">
                              {JSON.stringify(s)}
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  );
                })()}
                {(() => {
                  const dd = evidence.duplicate_detection;
                  if (!dd) return null;
                  return (
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Duplicate Detection
                      </span>
                      <div className="mt-1 rounded bg-gray-50 p-2 font-mono text-xs text-gray-600">
                        {JSON.stringify(dd)}
                      </div>
                    </div>
                  );
                })()}
                {(() => {
                  const sg = evidence.safety_gate;
                  if (!sg) return null;
                  return (
                    <div>
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Safety Gate
                      </span>
                      <div className="mt-1 rounded bg-gray-50 p-2 font-mono text-xs text-gray-600">
                        {JSON.stringify(sg)}
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : (
              <p className="text-sm text-gray-400">Evidence not available</p>
            )}
          </Section>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Assignment State */}
          <Card padding="md">
            <CardHeader>
              <UserCheck className="h-4 w-4 text-primary-600" />
              <CardTitle className="text-sm font-semibold text-gray-900">Assignment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {reviewCase.assignments && reviewCase.assignments.length > 0 ? (
                  reviewCase.assignments.map((a) => (
                    <div key={a.assignment_id} className="rounded bg-gray-50 p-2">
                      <p className="font-medium">
                        {a.reviewer_user_id.substring(0, 12)}...
                      </p>
                      <p className="text-xs text-gray-500">{a.reviewer_role}</p>
                      <p className="text-xs text-gray-400">
                        Status: {a.status}
                        {a.claimed_at && ` — Claimed ${new Date(a.claimed_at).toLocaleDateString()}`}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400">Not yet assigned</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Previous Decisions */}
          <Card padding="md">
            <CardHeader>
              <ThumbsUp className="h-4 w-4 text-primary-600" />
              <CardTitle className="text-sm font-semibold text-gray-900">Decisions</CardTitle>
            </CardHeader>
            <CardContent>
              {hasDecision ? (
                <div className="space-y-2">
                  {reviewCase.decisions.map((d) => (
                    <div key={d.decision_id} className="rounded bg-gray-50 p-2">
                      <StatusBadge status={d.decision} />
                      <p className="mt-1 text-xs text-gray-600">{d.reason}</p>
                      <p className="text-xs text-gray-400">
                        by {d.reviewer_user_id.substring(0, 12)}... on{" "}
                        {new Date(d.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No decisions yet</p>
              )}
            </CardContent>
          </Card>

          {/* Decision Form */}
          {canDecide && !hasDecision && (
            <Card padding="md">
              <CardHeader>
                <FileText className="h-4 w-4 text-primary-600" />
                <CardTitle className="text-sm font-semibold text-gray-900">Submit Decision</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Decision *
                    </label>
                    <select
                      value={decision}
                      onChange={(e) => setDecision(e.target.value)}
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    >
                      <option value="">Select decision...</option>
                      <option value="APPROVED_FOR_PILOT_REVIEW">
                        Approved for Pilot Review
                      </option>
                      <option value="REJECTED">Rejected</option>
                      <option value="CHANGES_REQUESTED">Changes Requested</option>
                      <option value="ESCALATED">Escalated</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reason *
                    </label>
                    <textarea
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      rows={4}
                      placeholder="Explain your decision..."
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Structured Findings (optional, JSON or notes)
                    </label>
                    <textarea
                      value={findings}
                      onChange={(e) => setFindings(e.target.value)}
                      rows={3}
                      placeholder='{"key": "value"} or free text...'
                      className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    />
                  </div>

                  <label className="flex items-start gap-2">
                    <input
                      type="checkbox"
                      checked={evidenceConfirmed}
                      onChange={(e) => setEvidenceConfirmed(e.target.checked)}
                      className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-600">
                      I confirm that I have reviewed the candidate content, validation results,
                      provenance, source bindings, and evidence before making this decision. *
                    </span>
                  </label>

                  <Button
                    className="w-full"
                    onClick={handleSubmitDecision}
                    isLoading={submitting}
                    disabled={!decision || !reason.trim() || !evidenceConfirmed}
                  >
                    <CheckCircle className="mr-1.5 h-4 w-4" />
                    Submit Decision
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Decision submitted message */}
          {canDecide && hasDecision && (
            <Card padding="md" className="border-green-200 bg-green-50">
              <CardContent>
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-sm font-medium">
                    Decision submitted. This case is closed for further review.
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* History */}
          <Card padding="md">
            <CardHeader>
              <History className="h-4 w-4 text-primary-600" />
              <CardTitle className="text-sm font-semibold text-gray-900">History</CardTitle>
            </CardHeader>
            <CardContent>
              <HistoryTimeline events={history} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
