"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getEvaluation, evaluateAttempt } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import {
  AlertCircle,
  CheckCircle,
  XCircle,
  Award,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  ArrowRight,
  RotateCcw,
  BarChart3,
  Zap,
} from "lucide-react";

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

function scoreBgColor(score: number): string {
  if (score >= 80) return "bg-green-100";
  if (score >= 60) return "bg-yellow-100";
  return "bg-red-100";
}

function ScoreGauge({ score }: { score: number }) {
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center">
      <svg width="160" height="160" className="transform -rotate-90">
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="10"
        />
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={scoreColor(score)}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className={`text-4xl font-bold ${scoreColor(score)}`}>
          {Math.round(score)}
        </span>
        <span className="text-xs text-gray-400">/ 100</span>
      </div>
    </div>
  );
}

export default function EvaluationResultPage() {
  const params = useParams();
  const router = useRouter();
  const attemptId = params?.attemptId as string;

  const {
    data: evaluation,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["evaluation", attemptId],
    queryFn: () => getEvaluation(attemptId),
    enabled: !!attemptId,
  });

  const evaluateMutation = useMutation({
    mutationFn: () => evaluateAttempt(attemptId),
    onSuccess: () => {
      refetch();
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !evaluation) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("scenario.evaluationFailed")}</p>
        <p className="text-sm text-gray-500">
          {t("scenario.evaluationFailedMessage")}
        </p>
        <Button
          variant="outline"
          onClick={() => evaluateMutation.mutate()}
          isLoading={evaluateMutation.isPending}
        >
          {t("scenario.retryEvaluation")}
        </Button>
        <Button variant="ghost" onClick={() => router.back()}>
          {t("common.back")}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">{t("result.title")}</h1>
      </div>

      {/* Overall Score Card */}
      <Card padding="lg" className="mb-8">
        <div className="flex flex-col items-center sm:flex-row sm:items-center gap-6">
          <ScoreGauge score={evaluation.overall_score} />
          <div className="flex flex-col items-center sm:items-start gap-2">
            <span className="text-sm font-medium text-gray-500">
              {t("result.overallScore")}
            </span>
            {evaluation.passed ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-4 py-1.5 text-sm font-semibold text-green-700">
                <CheckCircle className="h-4 w-4" />
                {t("result.passed")}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 px-4 py-1.5 text-sm font-semibold text-red-700">
                <XCircle className="h-4 w-4" />
                {t("result.failed")}
              </span>
            )}
            {evaluation.confidence && (
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Zap className="h-3 w-3" />
                {t("result.confidence")}: {Math.round(evaluation.confidence * 100)}%
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Criteria Breakdown */}
      {evaluation.criteria && evaluation.criteria.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-xl font-semibold text-gray-900">
            {t("result.criteria")}
          </h2>
          <div className="space-y-3">
            {evaluation.criteria.map((criterion) => (
              <Card key={criterion.criterion_id} padding="md">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">
                    {criterion.criterion_id}
                  </h3>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${scoreBgColor(criterion.score)} ${scoreColor(criterion.score)}`}
                  >
                    {Math.round(criterion.score)}%
                  </span>
                </div>
                {criterion.evidence && (
                  <p className="text-sm text-gray-600 mb-1">
                    <span className="font-medium text-gray-700">{t("result.evidence")}:</span>{" "}
                    {criterion.evidence}
                  </p>
                )}
                {criterion.comment && (
                  <p className="text-sm text-gray-600 mb-1">
                    <span className="font-medium text-gray-700">{t("result.comment")}:</span>{" "}
                    {criterion.comment}
                  </p>
                )}
                {criterion.improvement && (
                  <p className="text-sm text-amber-700">
                    <span className="font-medium">{t("result.improvement")}:</span>{" "}
                    {criterion.improvement}
                  </p>
                )}
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {evaluation.strengths && evaluation.strengths.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-green-800">
            <TrendingUp className="h-5 w-5" />
            {t("result.strengths")}
          </h2>
          <ul className="space-y-2">
            {evaluation.strengths.map((strength, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700"
              >
                <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weak Points */}
      {evaluation.weak_points && evaluation.weak_points.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-amber-800">
            <TrendingDown className="h-5 w-5" />
            {t("result.weakPoints")}
          </h2>
          <ul className="space-y-2">
            {evaluation.weak_points.map((weak, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-700"
              >
                <Lightbulb className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{weak}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Critical Errors */}
      {evaluation.critical_errors && evaluation.critical_errors.length > 0 ? (
        <div className="mb-8">
          <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-red-800">
            <XCircle className="h-5 w-5" />
            {t("result.criticalErrors")}
          </h2>
          <ul className="space-y-2">
            {evaluation.critical_errors.map((err, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
              >
                <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{err}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="mb-8">
          <h2 className="mb-2 flex items-center gap-2 text-xl font-semibold text-gray-800">
            <XCircle className="h-5 w-5" />
            {t("result.criticalErrors")}
          </h2>
          <Card padding="md" className="bg-gray-50">
            <p className="text-sm text-gray-500">{t("result.noCriticalErrors")}</p>
          </Card>
        </div>
      )}

      {/* Next Recommendation */}
      {evaluation.next_recommendation && (
        <Card padding="md" className="mb-8 border-primary-200 bg-primary-50">
          <CardHeader>
            <Award className="h-5 w-5 text-primary-600" />
            <CardTitle className="text-sm font-semibold text-primary-800">
              {t("result.nextRecommendation")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-medium text-primary-700">
              {evaluation.next_recommendation.action}
            </p>
            {evaluation.next_recommendation.description && (
              <p className="mt-1 text-sm text-primary-600">
                {evaluation.next_recommendation.description}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <Card padding="md" className="mb-8 bg-gray-50">
        <p className="text-xs text-gray-400">{t("result.disclaimer")}</p>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button
          variant="outline"
          onClick={() => router.back()}
        >
          <RotateCcw className="mr-2 h-4 w-4" />
          {t("result.retryScenario")}
        </Button>
        <Button
          onClick={() => router.push("/me/dashboard")}
        >
          <BarChart3 className="mr-2 h-4 w-4" />
          {t("result.toProgress")}
        </Button>
        <Button
          variant="secondary"
          onClick={() => {
            // Navigate back twice or to a specific next scenario
            router.back();
          }}
        >
          {t("result.nextScenario")}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
