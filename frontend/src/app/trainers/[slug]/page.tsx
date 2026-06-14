"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getTrainer, enrollTrainer, isAuthenticated } from "@/lib/api/client";
import { t, ti } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  BookOpen,
  Globe,
  Users,
  ArrowRight,
  GraduationCap,
  Zap,
  ListChecks,
} from "lucide-react";

const BA_MODULES = [
  { module_id: 'ba_hr_screening', title: 'HR Screening & Self-Presentation', description: 'HR questions, self-presentation, motivation, salary expectations', activity_count: 20 },
  { module_id: 'ba_basics_stakeholders', title: 'BA Basics & Stakeholders', description: 'Role of BA, BABOK, stakeholder types, RACI matrix', activity_count: 19 },
  { module_id: 'ba_requirements_elicitation', title: 'Requirements Elicitation & Analysis', description: 'Elicitation techniques, requirements analysis, validation', activity_count: 20 },
  { module_id: 'ba_documentation_artifacts', title: 'Documentation & Artifacts', description: 'User stories, Use cases, BRD, SRS, Acceptance criteria', activity_count: 19 },
  { module_id: 'ba_process_data_modeling', title: 'Process & Data Modeling', description: 'BPMN, UML, ERD, Data Flow Diagrams, Event Storming', activity_count: 15 },
  { module_id: 'ba_methodologies', title: 'Methodologies', description: 'Scrum, Kanban, SAFe, Waterfall, methodology comparison', activity_count: 16 },
  { module_id: 'ba_metrics_prioritization', title: 'Metrics, Estimation & Prioritization', description: 'MoSCoW, Kano, WSJF, Story Points, ROI, NPV', activity_count: 16 },
  { module_id: 'ba_communication_conflict', title: 'Communication & Conflict', description: 'Facilitation, negotiation, expectation management, conflict resolution', activity_count: 17 },
  { module_id: 'ba_technical_aspects', title: 'Technical Aspects (SQL, API, Prototypes)', description: 'SQL queries, REST API, JSON, prototyping, architecture', activity_count: 19 },
  { module_id: 'ba_real_cases', title: 'Real-World Case Studies', description: 'Complex scenarios with full analysis cycle', activity_count: 7 },
];

export default function TrainerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const slug = params?.slug as string;

  const {
    data: trainer,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !trainer) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.error")}</p>
        <p className="text-sm text-gray-500">{(error as Error)?.message}</p>
        <Button variant="outline" onClick={() => refetch()}>
          {t("common.retry")}
        </Button>
      </div>
    );
  }

  const handleEnroll = () => {
    if (!isAuthenticated()) {
      router.push(`/login?redirect=/trainers/${slug}`);
      return;
    }
    enrollMutation.mutate();
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Trainer Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
              <GraduationCap className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {t(`trainer.${trainer.trainer_product_id}`) !== `trainer.${trainer.trainer_product_id}`
                  ? t(`trainer.${trainer.trainer_product_id}`)
                  : trainer.name}
              </h1>
              {trainer.description && (
                <p className="mt-1 text-gray-500">
                  {t(`trainer.${trainer.trainer_product_id}_desc`) !== `trainer.${trainer.trainer_product_id}_desc`
                    ? t(`trainer.${trainer.trainer_product_id}_desc`)
                    : trainer.description}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Enroll / Status Section */}
      <Card padding="lg" className="mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {trainer.is_enrolled ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-700">
                <CheckCircle className="h-4 w-4" />
                {t("trainer.enrolled")}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-600">
                {t("trainer.notEnrolled")}
              </span>
            )}
            <span className="flex items-center gap-1 text-sm text-gray-500">
              <BookOpen className="h-4 w-4" />
              {trainer.scenario_count} {t("trainer.scenarios").toLowerCase()}
            </span>
            <span className="flex items-center gap-1 text-sm text-primary-500">
              <Zap className="h-4 w-4" />
              {t("trainer.questsAvailable")}
            </span>
          </div>

          {trainer.is_enrolled ? (
            <Button
              onClick={() => router.push(`/trainers/${slug}/quests`)}
            >
              {t("trainer.startQuest")}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          ) : (
            <Button
              onClick={handleEnroll}
              isLoading={enrollMutation.isPending}
            >
              {t("trainer.enroll")}
            </Button>
          )}
        </div>

        {enrollMutation.isSuccess && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
            <CheckCircle className="h-4 w-4" />
            {t("trainer.enrolledMessage")}
          </div>
        )}

        {enrollMutation.isError && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="h-4 w-4" />
            {enrollMutation.error?.message || t("common.error")}
          </div>
        )}
      </Card>

      {/* BA Trainer Phase 1 Modules Section */}
      {trainer.trainer_product_id === 'business_analyst_interview_trainer' && (
        <Card padding="lg" className="mb-8">
          <CardHeader>
            <div className="flex items-center gap-2">
              <ListChecks className="h-5 w-5 text-gray-400" />
              <CardTitle>{t('ba_trainer.modules')}</CardTitle>
            </div>
            <CardDescription>
              {t('ba_trainer.module_activities')} — {t('ba_trainer.phase_1_badge')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {BA_MODULES.map((mod) => (
                <Link key={mod.module_id} href={`/trainers/${slug}/modules/${mod.module_id}`}>
                  <div className="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-gray-100">
                        {t(`modules.${mod.module_id}.title`) !== `modules.${mod.module_id}.title`
                          ? t(`modules.${mod.module_id}.title`)
                          : mod.title}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {t(`modules.${mod.module_id}.description`) !== `modules.${mod.module_id}.description`
                          ? t(`modules.${mod.module_id}.description`)
                          : mod.description}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400 whitespace-nowrap ml-4">
                      {mod.activity_count} {t('ba_trainer.activity_label')}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quest Catalog Section — primary entry */}
      {trainer.is_enrolled && (
        <Card padding="lg" className="mb-8 border-primary-200">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary-600" />
              <CardTitle>{t('trainer.questCatalog')}</CardTitle>
            </div>
            <CardDescription>
              {t('trainer.questCatalogDesc')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg bg-primary-50 p-4 mb-4 border border-primary-100">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary-800">
                    {t('trainer.immersiveExperience')}
                  </p>
                  <p className="mt-1 text-sm text-primary-700">
                    {t('trainer.immersiveExperienceDesc')}
                  </p>
                </div>
              </div>
            </div>
            <Button
              onClick={() => router.push(`/trainers/${slug}/quests`)}
              className="w-full sm:w-auto"
            >
              {t('trainer.startQuest')}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* BA Trainer Phase 2 Scenarios Section */}
      {trainer.trainer_product_id === 'business_analyst_interview_trainer' && (
        <Card padding="lg" className="mb-8 border-primary-200">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary-600" />
              <CardTitle>{t('ba_phase2.title')}</CardTitle>
            </div>
            <CardDescription>
              {t('ba_phase2.description')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg bg-primary-50 p-4 mb-4 border border-primary-100">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary-800">
                    {t('ba_phase2.how_it_works_title')}
                  </p>
                  <p className="mt-1 text-sm text-primary-700">
                    {t('ba_phase2.how_it_works_desc')}
                  </p>
                </div>
              </div>
            </div>
            <Button
              onClick={() => router.push(`/trainers/${slug}/phase2`)}
              className="w-full sm:w-auto"
            >
              {t('ba_phase2.start')}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Details Grid */}
      <div className="grid gap-6 sm:grid-cols-2">
        {/* Target Audience */}
        {trainer.target_audience && trainer.target_audience.length > 0 && (
          <Card padding="md">
            <CardHeader>
              <Users className="h-5 w-5 text-gray-400" />
              <CardTitle className="text-sm font-medium text-gray-700">
                {t("trainer.targetAudience")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
                {trainer.target_audience.map((item, idx) => (
                  <li key={idx}>
                    {t(`trainer.audience_${item}`) !== `trainer.audience_${item}`
                      ? t(`trainer.audience_${item}`)
                      : item.replace(/_/g, " ")}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Supported Locales */}
        {trainer.supported_locales && trainer.supported_locales.length > 0 && (
          <Card padding="md">
            <CardHeader>
              <Globe className="h-5 w-5 text-gray-400" />
              <CardTitle className="text-sm font-medium text-gray-700">
                {t("trainer.locale")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {trainer.supported_locales.map((locale, idx) => (
                  <span
                    key={idx}
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      locale === trainer.default_locale
                        ? "bg-primary-100 text-primary-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {locale}
                    {locale === trainer.default_locale && (
                      <span className="ml-1 text-primary-500">(default)</span>
                    )}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Duration Estimate */}
        <Card padding="md">
          <CardHeader>
            <Clock className="h-5 w-5 text-gray-400" />
            <CardTitle className="text-sm font-medium text-gray-700">
              {t("trainer.duration")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              {trainer.scenario_count} {t("trainer.scenarios").toLowerCase()}
            </p>
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
