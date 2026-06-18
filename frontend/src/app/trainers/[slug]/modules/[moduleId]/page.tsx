"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getTrainer, enrollTrainer, getModuleActivities, isAuthenticated } from "@/lib/api/client";
import { t, pluralize } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardContent } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { AlertCircle, CheckCircle, Play, ListChecks, ArrowLeft } from "lucide-react";
import { ModuleQuizEngine } from "@/features/module-quiz";
import type { QuizResultItem } from "@/features/module-quiz";
import ModuleQuizResult from "@/features/module-quiz/ModuleQuizResult";

/* ------------------------------------------------------------------ */
/*  Page modes                                                        */
/* ------------------------------------------------------------------ */

type PageMode =
  | "start_screen"
  | "quiz"
  | "result"
  | "bank_mode";

/* ------------------------------------------------------------------ */
/*  Helper helpers (carried over from old module list)                */
/* ------------------------------------------------------------------ */

const difficultyVariant = (
  difficulty: string,
): "success" | "warning" | "danger" | "default" => {
  switch (difficulty) {
    case "junior":
      return "success";
    case "middle":
      return "warning";
    case "senior":
      return "danger";
    default:
      return "default";
  }
};

const difficultyLabel = (difficulty: string) => {
  switch (difficulty) {
    case "junior":
      return t("ba_trainer.difficulty_junior");
    case "middle":
      return t("ba_trainer.difficulty_middle");
    case "senior":
      return t("ba_trainer.difficulty_senior");
    default:
      return difficulty;
  }
};

const activityTypeIcon = (type: string) => {
  switch (type) {
    case "single_choice":
      return "⊙";
    case "multiple_choice":
      return "☐";
    case "numeric":
      return "#";
    case "fill_blanks":
      return "___";
    case "matching":
      return "⇄";
    default:
      return "?";
  }
};

const activityTypeLabel = (type: string) => {
  switch (type) {
    case "single_choice":
      return t("activity_type.single_choice");
    case "multiple_choice":
      return t("activity_type.multiple_choice");
    case "matching":
      return t("activity_type.matching");
    case "ordering":
      return t("activity_type.ordering");
    case "evidence_select":
      return t("activity_type.evidence_select");
    case "free_text":
      return t("activity_type.free_text");
    case "fill_blanks":
      return t("activity_type.fill_blanks");
    case "numeric":
      return t("activity_type.numeric");
    default:
      return type.replace(/_/g, " ");
  }
};

/* ------------------------------------------------------------------ */
/*  Fallback titles (same as before)                                  */
/* ------------------------------------------------------------------ */

const MODULE_FALLBACK_TITLES: Record<string, string> = {
  ba_hr_screening: 'HR Screening & Self-Presentation',
  ba_basics_stakeholders: 'BA Basics & Stakeholders',
  ba_requirements_elicitation: 'Requirements Elicitation & Analysis',
  ba_documentation_artifacts: 'Documentation & Artifacts',
  ba_process_data_modeling: 'Process & Data Modeling',
  ba_methodologies: 'Methodologies',
  ba_metrics_prioritization: 'Metrics, Estimation & Prioritization',
  ba_communication_conflict: 'Communication & Conflict',
  ba_technical_aspects: 'Technical Aspects (SQL, API, Prototypes)',
  ba_real_cases: 'Real-World Case Studies',
};

/* ------------------------------------------------------------------ */
/*  Module name helper                                                */
/* ------------------------------------------------------------------ */

function moduleTitleText(moduleId: string): string {
  const translated = t(`modules.${moduleId}.title`);
  if (translated !== `modules.${moduleId}.title`) return translated;
  return MODULE_FALLBACK_TITLES[moduleId] || moduleId.replace(/_/g, ' ');
}

function moduleDescText(moduleId: string): string {
  const translated = t(`modules.${moduleId}.description`);
  return translated !== `modules.${moduleId}.description` ? translated : '';
}

/* ------------------------------------------------------------------ */
/*  Page component                                                    */
/* ------------------------------------------------------------------ */

export default function ModuleActivitiesPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const moduleId = params?.moduleId as string;

  const queryClient = useQueryClient();

  // ── Page mode ─────────────────────────────────────────────────────
  const [mode, setMode] = useState<PageMode>("start_screen");
  const [quizResults, setQuizResults] = useState<QuizResultItem[]>([]);

  // ── Trainer query ─────────────────────────────────────────────────
  const { data: trainer } = useQuery({
    queryKey: ["trainer", slug],
    queryFn: () => getTrainer(slug),
    enabled: !!slug,
  });

  const enrollMutation = useMutation({
    mutationFn: () => enrollTrainer(slug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainer", slug] });
    },
  });

  // ── Module activities query ───────────────────────────────────────
  const {
    data: moduleData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["module-activities", slug, moduleId],
    queryFn: () => getModuleActivities(slug, moduleId),
    enabled: !!trainer,
  });

  // ── Loading state ─────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    );
  }

  // ── Error state ───────────────────────────────────────────────────
  if (error || !moduleData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <div className="text-red-500 text-4xl mb-4">!</div>
            <p className="text-red-600 mb-4">{t("ba_trainer.error_loading")}</p>
            <Button variant="outline" onClick={() => router.back()}>
              {t("common.back")}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // ── Enrollment gate ───────────────────────────────────────────────
  if (trainer && !trainer.is_enrolled) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full border-amber-200 bg-amber-50">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-amber-500 mb-4" />
            <h2 className="text-xl font-semibold text-amber-900 mb-2">
              {t("common.notEnrolled.title")}
            </h2>
            <p className="text-sm text-amber-700 mb-4">
              {t("common.notEnrolled.description")}
            </p>
            <Button
              onClick={() => {
                if (!isAuthenticated()) {
                  router.push(`/login?redirect=/trainers/${slug}/modules/${moduleId}`);
                  return;
                }
                enrollMutation.mutate();
              }}
              isLoading={enrollMutation.isPending}
            >
              {t("trainer.enroll")}
            </Button>
            {enrollMutation.isSuccess && (
              <div className="flex items-center justify-center gap-2 mt-4 text-sm text-green-700">
                <CheckCircle className="h-4 w-4" />
                {t("trainer.enrolledMessage")}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // ── Derived data ──────────────────────────────────────────────────
  const moduleTitle = moduleTitleText(moduleId);
  const moduleDesc = moduleDescText(moduleId);

  // ── Callbacks ─────────────────────────────────────────────────────
  const handleQuizFinish = (results: QuizResultItem[]) => {
    setQuizResults(results);
    setMode("result");
  };

  const handleRepeat = () => {
    setQuizResults([]);
    setMode("quiz");
  };

  const handleBack = () => {
    router.push(`/trainers/${slug}`);
  };

  // ── RENDER: QUIZ MODE ─────────────────────────────────────────────
  if (mode === "quiz") {
    const activities = moduleData.activities;

    if (activities.length === 0) {
      return (
        <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
          <button
            onClick={() => setMode("start_screen")}
            className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            {t("quiz.back_to_modules")}
          </button>
          <Card padding="md" className="text-center">
            <p className="text-gray-500">{t("ba_trainer.no_activities")}</p>
          </Card>
        </div>
      );
    }

    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
        <button
          onClick={() => setMode("start_screen")}
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("quiz.back_to_modules")}
        </button>

        {/* Quiz engine - manages sequential question flow */}
        <ModuleQuizEngine
          slug={slug}
          moduleId={moduleId}
          activities={activities}
          onFinish={handleQuizFinish}
          onExit={() => setMode("start_screen")}
        />
      </div>
    );
  }

  // ── RENDER: RESULT MODE ───────────────────────────────────────────
  if (mode === "result") {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
        <ModuleQuizResult
          results={quizResults}
          moduleTitle={moduleTitle}
          onRepeat={handleRepeat}
          onBack={handleBack}
          onBank={() => setMode("bank_mode")}
        />
      </div>
    );
  }

  // ── RENDER: BANK MODE (old activity list) ─────────────────────────
  if (mode === "bank_mode") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        {/* Back link */}
        <button
          onClick={() => setMode("start_screen")}
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t("quiz.back_to_modules")}
        </button>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            {moduleTitle}
          </h1>
          <p className="text-sm text-gray-500">
            {t("ba_trainer.bank_mode_desc")}
          </p>
        </div>

        {/* Activities list */}
        <div className="space-y-3">
          {moduleData.activities.length === 0 ? (
            <Card padding="md" className="text-center">
              <p className="text-gray-500">{t("ba_trainer.no_activities")}</p>
            </Card>
          ) : (
            moduleData.activities.map((activity) => (
              <button
                key={activity.activity_id}
                onClick={() =>
                  router.push(
                    `/trainers/${slug}/activities/${activity.activity_id}`,
                  )
                }
                className="w-full text-left"
              >
                <Card padding="md" className="transition-shadow hover:shadow-md">
                  <div className="flex items-center gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-mono text-sm">
                      {activity.order}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">
                        {t(activity.title_key) !== activity.title_key
                          ? t(activity.title_key)
                          : activity.title_key}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={difficultyVariant(activity.difficulty)}>
                          {difficultyLabel(activity.difficulty)}
                        </Badge>
                        <span className="text-xs text-gray-400 flex items-center gap-1">
                          <span className="font-mono">
                            {activityTypeIcon(activity.activity_type)}
                          </span>
                          {activityTypeLabel(activity.activity_type)}
                        </span>
                      </div>
                    </div>
                    <div className="flex-shrink-0 text-gray-400">
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>
                </Card>
              </button>
            ))
          )}
        </div>

        {/* Back to quiz mode */}
        <div className="mt-8 text-center">
          <Button onClick={() => setMode("start_screen")}>
            <Play className="h-4 w-4" />
            {t("quiz.start_test")}
          </Button>
        </div>
      </div>
    );
  }

  // ── RENDER: START SCREEN (default) ────────────────────────────────
  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Back Link */}
      <button
        onClick={handleBack}
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("quiz.back_to_modules")}
      </button>

      {/* Module Info Card */}
      <Card className="mb-6">
        <CardContent className="pt-8 text-center space-y-4">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-2">
            <Play className="h-8 w-8" />
          </div>

          <h1 className="text-2xl font-bold text-gray-900">
            {moduleTitle}
          </h1>

          {moduleDesc && (
            <p className="text-gray-500 max-w-md mx-auto">
              {moduleDesc}
            </p>
          )}

          <p className="text-sm text-gray-400">
            {pluralize(
              moduleData.total_count,
              t("ba_trainer.activity_label_one"),
              t("ba_trainer.activity_label_few"),
              t("ba_trainer.activity_label_many"),
            )}
          </p>

          {/* Start button — primary action */}
          <div className="pt-4">
            <Button
              size="lg"
              onClick={() => {
                if (moduleData.activities.length === 0) return;
                setMode("quiz");
              }}
              disabled={moduleData.activities.length === 0}
            >
              <Play className="h-5 w-5" />
              {t("quiz.start_test")}
            </Button>
          </div>

          {/* Bank mode link — secondary */}
          {moduleData.activities.length > 0 && (
            <div className="pt-2">
              <button
                onClick={() => setMode("bank_mode")}
                className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors"
              >
                <ListChecks className="h-4 w-4" />
                {t("quiz.question_bank")}
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
