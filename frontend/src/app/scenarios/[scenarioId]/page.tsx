"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getScenario, startScenario, submitMessage, completeSession } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { AlertCircle, Play, Send, CheckCircle, Clock, BarChart3, Lightbulb, ArrowLeft } from "lucide-react";
import Link from "next/link";

type ScenarioState = "idle" | "ready" | "submitting" | "evaluating" | "completed";

export default function ScenarioPage() {
  const params = useParams();
  const router = useRouter();
  const scenarioId = params?.scenarioId as string;

  const [state, setState] = useState<ScenarioState>("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  const {
    data: scenario,
    isLoading,
    isError,
    error: queryError,
    refetch,
  } = useQuery({
    queryKey: ["scenario", scenarioId],
    queryFn: () => getScenario(scenarioId),
    enabled: !!scenarioId,
  });

  const startMutation = useMutation({
    mutationFn: () => startScenario(scenarioId),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setAttemptId(data.attempt_id);
      setState("ready");
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
    },
  });

  const submitMutation = useMutation({
    mutationFn: (content: string) => {
      if (!sessionId) throw new Error("No session");
      return submitMessage(sessionId, content);
    },
    onSuccess: () => {
      setAnswer("");
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => {
      if (!sessionId) throw new Error("No session");
      return completeSession(sessionId);
    },
    onSuccess: () => {
      setState("evaluating");
    },
    onError: (err: Error) => {
      setError(err.message || t("common.error"));
    },
  });

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
    setState("submitting");
    completeMutation.mutate();
  };

  const handleViewResults = useCallback(() => {
    if (attemptId) {
      router.push(`/attempts/${attemptId}/result`);
    }
  }, [attemptId, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !scenario) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.error")}</p>
        <p className="text-sm text-gray-500">{(queryError as Error)?.message}</p>
        <Button variant="outline" onClick={() => refetch()}>
          {t("common.retry")}
        </Button>
      </div>
    );
  }

  // Idle state — show scenario intro
  if (state === "idle") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <Card padding="lg">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">{scenario.title_key}</h1>
            {scenario.goal_key && (
              <p className="mt-2 text-gray-500">{scenario.goal_key}</p>
            )}
          </div>

          <div className="mb-6 flex flex-wrap gap-3">
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
              <BarChart3 className="h-3.5 w-3.5" />
              {scenario.difficulty}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
              <Clock className="h-3.5 w-3.5" />
              {scenario.estimated_duration_minutes} {t("trainer.minutes")}
            </span>
          </div>

          <div className="mb-6 space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700">{t("scenario.userRole")}</h3>
              <p className="mt-1 text-sm text-gray-600">{scenario.user_role}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-700">{t("scenario.aiRole")}</h3>
              <p className="mt-1 text-sm text-gray-600">{scenario.ai_role}</p>
            </div>
          </div>

          {scenario.steps && scenario.steps.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">{t("scenario.intro")}</h3>
              <ol className="list-inside list-decimal space-y-1 text-sm text-gray-600">
                {scenario.steps
                  .sort((a, b) => a.order - b.order)
                  .map((step) => (
                    <li key={step.step_id}>{step.prompt_key}</li>
                  ))}
              </ol>
            </div>
          )}

          {scenario.target_skills && scenario.target_skills.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">{t("trainer.skills")}</h3>
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

          {scenario.hints && scenario.hints.length > 0 && (
            <div className="mb-6 rounded-lg bg-yellow-50 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-yellow-800">
                <Lightbulb className="h-4 w-4" />
                {t("scenario.hints")}
              </div>
              <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-yellow-700">
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

  // Ready / submitting state — show the scenario runner
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      <Card padding="lg">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">{scenario.title_key}</h1>
          <p className="mt-1 text-sm text-gray-500">{scenario.goal_key}</p>
        </div>

        {/* Submit answer area */}
        <div className="mb-6">
          <label
            htmlFor="answer"
            className="block text-sm font-semibold text-gray-700 mb-2"
          >
            {t("scenario.yourAnswer")}
          </label>
          <textarea
            id="answer"
            rows={6}
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder={t("scenario.answerPlaceholder")}
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
            {t("scenario.complete")}
          </Button>
        </div>
      </Card>

      {/* Evaluating overlay */}
      {state === "evaluating" && (
        <div className="mt-6">
          <Card padding="lg" className="text-center border-primary-200 bg-primary-50">
            <div className="flex flex-col items-center gap-3">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
              <p className="text-lg font-medium text-primary-800">
                {t("scenario.evaluating")}
              </p>
              <Button onClick={handleViewResults}>
                {t("scenario.evaluateNow")}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Completed state */}
      {state === "completed" && (
        <div className="mt-6">
          <Card padding="lg" className="text-center border-green-200 bg-green-50">
            <div className="flex flex-col items-center gap-3">
              <CheckCircle className="h-12 w-12 text-green-500" />
              <p className="text-lg font-medium text-green-800">
                {t("result.progressUpdated")}
              </p>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => router.back()}>
                  {t("scenario.backToList")}
                </Button>
                <Button onClick={handleViewResults}>
                  {t("result.title")}
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
