"use client";

import { useState, useCallback, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import {
  getScenario,
  startScenario,
  submitMessage,
  completeSession,
  getEvaluation,
  evaluateAttempt,
  sendAnalyticsEvent,
} from "@/lib/api/client";
import type { EvaluationResult, CriterionResult } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import {
  AlertCircle,
  Play,
  Send,
  CheckCircle,
  XCircle,
  Clock,
  BarChart3,
  Lightbulb,
  ArrowLeft,
  Award,
  TrendingUp,
  TrendingDown,
  RotateCcw,
  Loader2,
} from "lucide-react";

type PageState =
  | "loading"
  | "idle"
  | "ready"
  | "submitting"
  | "evaluating"
  | "evaluated"
  | "error"
  | "retry_blocked"
  | "not_found";

export default function Phase2ScenarioPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const scenarioId = params?.scenarioId as string;

  const [state, setState] = useState<PageState>("loading");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState("");

  const {
    data: scenario,
    isLoading: scenarioLoading,
    isError: scenarioError,
    error: scenarioQueryError,
    refetch: refetchScenario,
  } = useQuery({
    queryKey: ["scenario", scenarioId],
    queryFn: () => getScenario(scenarioId),
    enabled: !!scenarioId,
  });

  useEffect(() => {
    if (!scenarioLoading && scenario) {
      setState("idle");
      sendAnalyticsEvent("ba_phase2_scenario_opened", {
        trainer_slug: slug,
        scenario_id: scenarioId,
      });
    }
    if (!scenarioLoading && scenarioError) {
      setState("not_found");
    }
  }, [scenarioLoading, scenario, scenarioError, slug, scenarioId]);

  const startMutation = useMutation({
    mutationFn: () => startScenario(scenarioId),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setAttemptId(data.attempt_id);
      setState("ready");
      sendAnalyticsEvent("ba_phase2_scenario_started", {
        trainer_slug: slug,
        scenario_id: scenarioId,
      });
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
      setState("error");
    },
  });

  const submitMutation = useMutation({
    mutationFn: (content: string) => {
      if (!sessionId) throw new Error(t("common.error"));
      return submitMessage(sessionId, content);
    },
    onSuccess: () => {
      setAnswer("");
      sendAnalyticsEvent("ba_phase2_submission_created", {
        trainer_slug: slug,
        scenario_id: scenarioId,
      });
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => {
      if (!sessionId) throw new Error(t("common.error"));
      return completeSession(sessionId);
    },
    onSuccess: () => {
      setState("evaluating");
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: () => {
      if (!attemptId) throw new Error(t("common.error"));
      return evaluateAttempt(attemptId);
    },
    onSuccess: (data) => {
      setEvaluation(data);
      setState("evaluated");
      sendAnalyticsEvent("ba_phase2_evaluation_completed", {
        trainer_slug: slug,
        scenario_id: scenarioId,
        properties: {
          overall_score: data.overall_score,
          passed: data.passed,
        },
      });
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
      sendAnalyticsEvent("ba_phase2_evaluation_failed", {
        trainer_slug: slug,
        scenario_id: scenarioId,
        properties: {
          error: err.message?.substring(0, 100),
        },
      });
      setState("error");
    },
  });

  const checkEvaluation = useMutation({
    mutationFn: () => {
      if (!attemptId) throw new Error(t("common.error"));
      return getEvaluation(attemptId);
    },
    onSuccess: (data) => {
      setEvaluation(data);
      setState("evaluated");
      sendAnalyticsEvent("ba_phase2_result_viewed", {
        trainer_slug: slug,
        scenario_id: scenarioId,
        properties: {
          overall_score: data.overall_score,
          passed: data.passed,
        },
      });
    },
    onError: () => {
      // Evaluation not ready yet, keep polling
    },
  });

  // Auto-trigger evaluation after completion
  useEffect(() => {
    if (state === "evaluating" && attemptId) {
      const timer = setTimeout(() => {
        evaluateMutation.mutate();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [state, attemptId]);

  const handleStart = () => {
    setError("");
    startMutation.mutate();
  };

  const handleSubmitAnswer = () => {
    if (!answer.trim()) {
      setError(t("scenario.emptyAnswerError"));
      return;
    }
    setError("");
    submitMutation.mutate(answer);
  };

  const handleComplete = () => {
    setError("");
    completeMutation.mutate();
  };

  const handleRetryEvaluation = () => {
    setError("");
    evaluateMutation.mutate();
  };

  const handleRetryScenario = () => {
    sendAnalyticsEvent("ba_phase2_retry_requested", {
      trainer_slug: slug,
      scenario_id: scenarioId,
    });
    setState("idle");
    setSessionId(null);
    setAttemptId(null);
    setAnswer("");
    setEvaluation(null);
    setError("");
  };

  const handleViewProgress = () => {
    router.push(`/me/progress/${slug}`);
  };

  // Loading state
  if (scenarioLoading || state === "loading") {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  // Not found / error
  if (state === "not_found" || !scenario) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
          <AlertCircle className="h-12 w-12 text-red-400" />
          <p className="text-lg font-medium text-gray-900">
            {t("common.notFound")}
          </p>
          <Button variant="outline" onClick={() => router.back()}>
            {t("common.back")}
          </Button>
        </div>
      </div>
    );
  }

  // ============ IDLE STATE ============
  if (state === "idle") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <button
          onClick={() => router.push(`/trainers/${slug}/phase2`)}
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("ba_phase2.back_to_scenarios")}
        </button>

        <Card padding="lg">
          {/* Title */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              {t(scenario.title_key) !== scenario.title_key
                ? t(scenario.title_key)
                : scenario.title_key}
            </h1>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                <BarChart3 className="h-3 w-3" />
                {scenario.difficulty || "intermediate"}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700">
                <Clock className="h-3 w-3" />
                {scenario.estimated_duration_minutes || 30} {t("trainer.minutes")}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-700">
                {t("ba_phase2.phase_2_badge")}
              </span>
            </div>
          </div>

          {/* Business Context */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h2 className="text-sm font-semibold text-gray-700 mb-2">
              {t("ba_phase2.business_context")}
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              {scenario.goal_key}
            </p>
          </div>

          {/* Task */}
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-2">
              {t("ba_phase2.task")}
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              {scenario.steps?.[0]?.prompt_key || scenario.goal_key}
            </p>
          </div>

          {/* Target Skills */}
          {scenario.target_skills && scenario.target_skills.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                {t("trainer.skills")}
              </h3>
              <div className="flex flex-wrap gap-2">
                {scenario.target_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* User Role */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-1">
              {t("scenario.userRole")}
            </h3>
            <p className="text-sm text-gray-600">
              {scenario.user_role || t("ba_phase2.default_role")}
            </p>
          </div>

          {/* Constraints / Hints */}
          {scenario.hints && scenario.hints.length > 0 && (
            <div className="mb-6 rounded-lg bg-amber-50 p-4 border border-amber-200">
              <div className="flex items-center gap-2 text-sm font-medium text-amber-800">
                <Lightbulb className="h-4 w-4" />
                {t("scenario.hints")}
              </div>
              <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-amber-700">
                {scenario.hints.map((hint, idx) => (
                  <li key={idx}>{hint}</li>
                ))}
              </ul>
            </div>
          )}

          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          <Button
            size="lg"
            onClick={handleStart}
            isLoading={startMutation.isPending}
            className="w-full sm:w-auto"
          >
            <Play className="mr-2 h-5 w-5" />
            {t("scenario.start")}
          </Button>
        </Card>
      </div>
    );
  }

  // ============ READY / SUBMITTING STATE ============
  if (state === "ready" || state === "submitting") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <Card padding="lg">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              {t(scenario.title_key) !== scenario.title_key
                ? t(scenario.title_key)
                : scenario.title_key}
            </h1>
            <div className="mt-2 flex flex-wrap gap-2">
              {scenario.target_skills?.slice(0, 3).map((skill, idx) => (
                <span
                  key={idx}
                  className="rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Business Context Reminder */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600 border border-gray-200">
            <span className="font-medium text-gray-700">
              {t("ba_phase2.business_context")}:
            </span>{" "}
            {scenario.goal_key?.substring(0, 200)}
            {(scenario.goal_key?.length || 0) > 200 ? "..." : ""}
          </div>

          {/* Answer area */}
          <div className="mb-6">
            <label
              htmlFor="answer"
              className="block text-sm font-semibold text-gray-700 mb-2"
            >
              {t("ba_phase2.your_answer")}
            </label>
            <textarea
              id="answer"
              rows={8}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder={t("ba_phase2.answer_placeholder")}
              disabled={state === "submitting"}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-50 disabled:bg-gray-50"
            />
            <div className="mt-2 flex justify-end">
              <Button
                size="sm"
                onClick={handleSubmitAnswer}
                isLoading={submitMutation.isPending}
                disabled={state === "submitting"}
              >
                <Send className="mr-1.5 h-4 w-4" />
                {t("scenario.submit")}
              </Button>
            </div>
          </div>

          {submitMutation.isSuccess && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
              <CheckCircle className="h-4 w-4" />
              {t("scenario.answerSaved")}
            </div>
          )}

          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-400">{t("scenario.ready")}</p>
            <Button
              onClick={handleComplete}
              isLoading={completeMutation.isPending}
              disabled={state === "submitting"}
            >
              {t("ba_phase2.complete")}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ============ EVALUATING STATE ============
  if (state === "evaluating") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <Card padding="lg" className="text-center border-primary-200 bg-primary-50">
          <div className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-12 w-12 animate-spin text-primary-600" />
            <h2 className="text-xl font-semibold text-primary-800">
              {t("ba_phase2.evaluating_title")}
            </h2>
            <p className="text-sm text-primary-600 max-w-md">
              {t("ba_phase2.evaluating_desc")}
            </p>

            {evaluateMutation.isPending ? (
              <div className="flex items-center gap-2 text-sm text-primary-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                {t("ba_phase2.evaluating_progress")}
              </div>
            ) : error ? (
              <div className="flex flex-col items-center gap-3">
                <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  {error}
                </div>
                <Button onClick={handleRetryEvaluation}>
                  {t("scenario.retryEvaluation")}
                </Button>
              </div>
            ) : (
              <Button
                onClick={handleRetryEvaluation}
                variant="outline"
                size="sm"
              >
                {t("scenario.evaluateNow")}
              </Button>
            )}
          </div>
        </Card>
      </div>
    );
  }

  // ============ EVALUATED STATE ============
  if (state === "evaluated" && evaluation) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            {t("result.title")}
          </h1>
          <p className="mt-2 text-gray-500">
            {t(scenario.title_key) !== scenario.title_key
              ? t(scenario.title_key)
              : scenario.title_key}
          </p>
        </div>

        {/* Overall Score Card */}
        <Card padding="lg" className="mb-8">
          <div className="flex flex-col items-center sm:flex-row sm:items-center gap-6">
            {/* Score Gauge */}
            <div className="relative flex items-center justify-center">
              <svg width="140" height="140" className="transform -rotate-90">
                <circle
                  cx="70" cy="70" r="50"
                  fill="none" stroke="#e5e7eb" strokeWidth="8"
                />
                <circle
                  cx="70" cy="70" r="50"
                  fill="none" stroke="currentColor" strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 50}
                  strokeDashoffset={2 * Math.PI * 50 * (1 - evaluation.overall_score / 100)}
                  className={
                    evaluation.overall_score >= 80
                      ? "text-green-500"
                      : evaluation.overall_score >= 60
                      ? "text-yellow-500"
                      : "text-red-500"
                  }
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span
                  className={`text-3xl font-bold ${
                    evaluation.overall_score >= 80
                      ? "text-green-600"
                      : evaluation.overall_score >= 60
                      ? "text-yellow-600"
                      : "text-red-600"
                  }`}
                >
                  {Math.round(evaluation.overall_score)}
                </span>
                <span className="text-xs text-gray-400">/ 100</span>
              </div>
            </div>

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
              {evaluation.ai_model_used && (
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <Award className="h-3 w-3" />
                  {t("ba_phase2.evaluated_by")}: {evaluation.ai_model_used}
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
                      {criterion.criterion_id.replace(/_/g, " ")}
                    </h3>
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        criterion.score >= 80
                          ? "bg-green-100 text-green-700"
                          : criterion.score >= 60
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {Math.round(criterion.score)}%
                    </span>
                  </div>
                  {criterion.evidence && (
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-medium text-gray-700">
                        {t("result.evidence")}:
                      </span>{" "}
                      {criterion.evidence}
                    </p>
                  )}
                  {criterion.comment && (
                    <p className="text-sm text-gray-600 mb-1">
                      <span className="font-medium text-gray-700">
                        {t("result.comment")}:
                      </span>{" "}
                      {criterion.comment}
                    </p>
                  )}
                  {criterion.improvement && (
                    <p className="text-sm text-amber-700">
                      <span className="font-medium">
                        {t("result.improvement")}:
                      </span>{" "}
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

        {/* Improvement Areas */}
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
          <Button variant="outline" onClick={handleRetryScenario}>
            <RotateCcw className="mr-2 h-4 w-4" />
            {t("ba_phase2.retry")}
          </Button>
          <Button onClick={handleViewProgress}>
            <BarChart3 className="mr-2 h-4 w-4" />
            {t("result.toProgress")}
          </Button>
          <Button
            variant="secondary"
            onClick={() => router.push(`/trainers/${slug}/phase2`)}
          >
            {t("ba_phase2.back_to_scenarios")}
          </Button>
        </div>
      </div>
    );
  }

  // ============ ERROR STATE ============
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <Card padding="lg" className="text-center">
        <div className="flex flex-col items-center gap-4 py-6">
          <AlertCircle className="h-12 w-12 text-red-400" />
          <h2 className="text-xl font-semibold text-gray-900">
            {t("common.error")}
          </h2>
          {error && <p className="text-sm text-gray-500">{error}</p>}

          <div className="flex gap-3 mt-2">
            {attemptId && evaluateMutation.isError && (
              <Button
                onClick={handleRetryEvaluation}
                isLoading={evaluateMutation.isPending}
              >
                {t("scenario.retryEvaluation")}
              </Button>
            )}
            <Button variant="outline" onClick={() => router.back()}>
              {t("common.back")}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
