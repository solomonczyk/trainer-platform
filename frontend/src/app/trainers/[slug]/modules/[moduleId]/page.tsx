"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getTrainer, enrollTrainer, getModuleActivities, isAuthenticated } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardContent } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { AlertCircle, CheckCircle } from "lucide-react";

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
      return t("ba_trainer.activity_type_single_choice");
    case "multiple_choice":
      return t("ba_trainer.activity_type_multiple_choice");
    case "matching":
      return t("ba_trainer.activity_type_matching");
    case "ordering":
      return t("ba_trainer.activity_type_ordering");
    case "evidence_select":
      return t("ba_trainer.activity_type_evidence_select");
    case "free_text":
      return t("ba_trainer.activity_type_free_text");
    case "fill_blanks":
      return t("ba_trainer.activity_type_fill_blanks");
    case "numeric":
      return t("ba_trainer.activity_type_numeric");
    default:
      return type.replace(/_/g, " ");
  }
};

export default function ModuleActivitiesPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;
  const moduleId = params?.moduleId as string;

  const queryClient = useQueryClient();

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

  const {
    data: moduleData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["module-activities", slug, moduleId],
    queryFn: () => getModuleActivities(slug, moduleId),
    enabled: !!trainer,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner />
      </div>
    );
  }

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

  // Enrollment gate
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

  // Module title with readable fallback (never show raw moduleId)
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
  const moduleTitle =
    t(`modules.${moduleId}.title`) !== `modules.${moduleId}.title`
      ? t(`modules.${moduleId}.title`)
      : (MODULE_FALLBACK_TITLES[moduleId] || moduleId.replace(/_/g, ' '));
  const moduleDesc = t(`modules.${moduleId}.description`);

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Back Link */}
      <button
        onClick={() => router.push(`/trainers/${slug}`)}
        className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
      >
        ← {t("ba_trainer.back_to_modules")}
      </button>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {moduleTitle}
        </h1>
        {moduleDesc && moduleDesc !== `modules.${moduleId}.description` && (
          <p className="text-gray-500">{moduleDesc}</p>
        )}
        <p className="text-sm text-gray-400 mt-2">
          {t("ba_trainer.total_activities")}: {moduleData.total_count}
        </p>
      </div>

      {/* Activities List */}
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
    </div>
  );
}
