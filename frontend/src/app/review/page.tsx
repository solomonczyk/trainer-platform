"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  getCurrentUser,
  listReviewCases,
  claimReview,
  isAuthenticated,
  type UserResponse,
  type ReviewCaseSummary,
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
  Clock,
  UserCheck,
  Eye,
  FileText,
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

const STATUS_COLORS: Record<string, string> = {
  PENDING_ASSIGNMENT: "bg-yellow-100 text-yellow-800",
  ASSIGNED: "bg-blue-100 text-blue-800",
  IN_REVIEW: "bg-purple-100 text-purple-800",
  CHANGES_REQUESTED: "bg-orange-100 text-orange-800",
  REJECTED: "bg-red-100 text-red-800",
  APPROVED_FOR_PILOT_REVIEW: "bg-green-100 text-green-800",
  ESCALATED: "bg-pink-100 text-pink-800",
  CLOSED: "bg-gray-100 text-gray-800",
};

function StatusBadge({ status }: { status: string }) {
  const colorClass = STATUS_COLORS[status] || "bg-gray-100 text-gray-800";
  const label = STATUS_LABELS[status] || status;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass}`}
    >
      {label}
    </span>
  );
}

export default function ReviewQueuePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [authChecking, setAuthChecking] = useState(true);
  const [cases, setCases] = useState<ReviewCaseSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("");
  const [claimingId, setClaimingId] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login?redirect=/review");
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
        router.push("/login?redirect=/review");
      })
      .finally(() => {
        setAuthChecking(false);
      });
  }, [router]);

  const fetchCases = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number> = { limit: 50 };
      if (filter) params.status = filter;
      const result = await listReviewCases(params);
      setCases(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load review queue");
    } finally {
      setLoading(false);
    }
  }, [user, filter]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleClaim = async (caseId: string) => {
    if (!user) return;
    setClaimingId(caseId);
    setError(null);
    try {
      await claimReview(caseId);
      await fetchCases();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to claim review");
    } finally {
      setClaimingId(null);
    }
  };

  const userCanClaim = (c: ReviewCaseSummary) => {
    return c.status === "ASSIGNED" || c.status === "PENDING_ASSIGNMENT";
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
        <Button onClick={() => router.push("/login?redirect=/review")}>
          {t("nav.login")}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <ClipboardList className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Human Review</h1>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Review generated item candidates for quality and correctness
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>{total} case{total !== 1 ? "s" : ""}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-2">
        {["", "PENDING_ASSIGNMENT", "ASSIGNED", "IN_REVIEW", "CLOSED"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === s
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {s ? STATUS_LABELS[s] || s : "All"}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : cases.length === 0 ? (
        <Card padding="lg">
          <div className="flex flex-col items-center gap-3 py-12 text-center">
            <FileText className="h-12 w-12 text-gray-300" />
            <p className="text-lg font-medium text-gray-500">No review cases found</p>
            <p className="text-sm text-gray-400">
              {filter
                ? `No cases with status "${STATUS_LABELS[filter] || filter}"`
                : "The review queue is empty"}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-3">
          {cases.map((c) => (
            <Card key={c.case_id} padding="md" hover>
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <StatusBadge status={c.status} />
                    <span className="text-xs font-mono text-gray-400 truncate">
                      {c.case_id}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-x-6 gap-y-1 text-sm text-gray-600">
                    <span>Candidate: {c.candidate_id ? c.candidate_id.substring(0, 16) : "N/A"}...</span>
                    <span>Type: {c.review_type}</span>
                    <span>Role: {c.required_reviewer_role}</span>
                    <span>
                      Created: {new Date(c.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/review/${c.case_id}`)}
                  >
                    <Eye className="mr-1 h-3.5 w-3.5" />
                    View
                  </Button>
                  {userCanClaim(c) && (
                    <Button
                      size="sm"
                      onClick={() => handleClaim(c.case_id)}
                      isLoading={claimingId === c.case_id}
                    >
                      <UserCheck className="mr-1 h-3.5 w-3.5" />
                      Claim
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
