"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { getTrainer, enrollTrainer, isAuthenticated, ApiClientError } from "@/lib/api/client";
import { t, ti, pluralize } from "@/lib/i18n";
import { useAuth } from "@/lib/auth/AuthContext";
import { AuthRequiredGate } from "@/components/auth/AuthRequiredGate";
import { EmailVerificationRequiredGate } from "@/components/auth/EmailVerificationRequiredGate";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import PageContainer from "@/components/ui/PageContainer";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  BookOpen,
  Users,
  ArrowRight,
  GraduationCap,
  Zap,
  ListChecks,
  Star,
  Play,
  Award,
  Lightbulb,
  Layers,
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
  const { user, status, clearSession } = useAuth();
  const slug = params?.slug as string;
  const [showAllModules, setShowAllModules] = useState(false);

  // ── Auth gates ─────────────────────────────────────────────────────────

  const isAuthenticatedState = status === "authenticated";
  const isVerified = user?.email_verified === true;

  // Protected query — disabled unless authenticated AND verified.
  // Never retries 401.
  const {
    data: trainer,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["trainer", slug],
    queryFn: () => getTrainer(slug),
    enabled: !!slug && isAuthenticatedState && isVerified,
    retry: (failureCount, err) => {
      if (err instanceof ApiClientError && err.status === 401) return false;
      return failureCount < 1;
    },
  });

  const enrollMutation = useMutation({
    mutationFn: () => enrollTrainer(slug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["trainer", slug] });
    },
  });

  // ── Render order: 1) loading → 2) unauthenticated → 3) unverified → 4) content ──

  // 1. Auth bootstrap still in flight
  if (status === "loading") {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  // 2. Not authenticated — show auth gate, never call protected APIs
  if (status === "unauthenticated") {
    return <AuthRequiredGate redirectTo={`/trainers/${slug}`} />;
  }

  // 3. Authenticated but email not verified
  if (user && user.email_verified === false) {
    return <EmailVerificationRequiredGate />;
  }

  // ── At this point the user IS authenticated AND verified ─────────────────

  // If a 401 sneaks through (defensive), clear session and show gate.
  // This prevents generic "Error loading" for auth failures.
  if (isError && error instanceof ApiClientError && error.status === 401) {
    clearSession();
    return <AuthRequiredGate redirectTo={`/trainers/${slug}`} />;
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  if (isError || !trainer) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-text-danger" />
        <p className="text-h3 text-foreground">{t("common.error")}</p>
        <p className="text-body-sm text-text-secondary">{(error as Error)?.message}</p>
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
    <PageContainer>
      {/* Trainer Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded bg-primary-50 text-primary-600">
              <GraduationCap className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-h2 text-foreground">
                {t(`trainer.${trainer.trainer_product_id}`) !== `trainer.${trainer.trainer_product_id}`
                  ? t(`trainer.${trainer.trainer_product_id}`)
                  : trainer.name}
              </h1>
              {trainer.description && (
                <p className="mt-1 text-body-sm text-text-secondary">
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
      <Card padding="lg" variant="default" className="mb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {trainer.is_enrolled ? (
              <Badge variant="success" size="sm">
                <CheckCircle className="h-4 w-4" />
                {t("trainer.enrolled")}
              </Badge>
            ) : (
              <Badge variant="default" size="sm">
                {t("trainer.notEnrolled")}
              </Badge>
            )}
            <span className="flex items-center gap-1 text-body-sm text-text-secondary">
              <BookOpen className="h-4 w-4" />
              {trainer.scenario_count} {t("trainer.scenarios").toLowerCase()}
            </span>
            <span className="flex items-center gap-1 text-body-sm text-primary-600">
              <Zap className="h-4 w-4" />
              {t("trainer.questsAvailable")}
            </span>
          </div>

          {trainer.is_enrolled ? (
            <Button
              onClick={() => router.push(`/trainers/${slug}/quests`)}
            >
              {t("trainer.startQuest")}
              <ArrowRight className="h-4 w-4" />
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
          <div className="mt-4 flex items-center gap-2 rounded bg-success-50 p-3 text-body-sm text-success-700">
            <CheckCircle className="h-4 w-4" />
            {t("trainer.enrolledMessage")}
          </div>
        )}

        {enrollMutation.isError && (
          <div className="mt-4 flex items-center gap-2 rounded bg-danger-50 p-3 text-body-sm text-danger-700">
            <AlertCircle className="h-4 w-4" />
            {enrollMutation.error?.message || t("common.error")}
          </div>
        )}
      </Card>

      {/* Recommended First Quest — shown when enrolled (PRIMARY ACTION) */}
      {trainer.is_enrolled && (
        <>
          {(() => {
            const isQA = slug.includes('qa') || trainer.trainer_product_id?.includes('qa');
            const questId = isQA ? 'qa_bug_report_structure_v1' : 'ba_payment_requirements_conflict';
            const titleKey = isQA ? 'recommended_quest.for_qa' : 'recommended_quest.for_ba';
            const reasonKey = isQA ? 'recommended_quest.for_qa_reason' : 'recommended_quest.for_ba_reason';
            const skillsKey = isQA ? 'recommended_quest.for_qa_skills' : 'recommended_quest.for_ba_skills';
            const questSteps = isQA ? 5 : 6;
            const questMinutes = isQA ? 15 : 20;

            return (
              <Card padding="lg" variant="elevated" className="mb-8 border-2 border-selected shadow-elevated bg-gradient-to-br from-primary-50 to-purple-50">
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700">
                      <Star className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-h3 text-primary-900">
                        {t('recommended_quest.title')}
                      </CardTitle>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col lg:flex-row lg:items-center gap-5">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-h2 text-foreground mb-3 leading-tight">
                        {t(titleKey)}
                      </h3>
                      <p className="text-body text-text-secondary mb-4 leading-relaxed">
                        {t(reasonKey)}
                      </p>
                      <div className="flex flex-wrap items-center gap-4 mb-4">
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                          <Clock className="h-4 w-4 text-text-muted" />
                          {t('recommended_quest.estimated_time_label').replace('{minutes}', String(questMinutes))}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-text-secondary">
                          <Layers className="h-4 w-4 text-text-muted" />
                          {t('recommended_quest.steps_label').replace('{count}', String(questSteps))}
                        </span>
                        <span className="inline-flex items-center gap-1.5 text-body-sm font-medium text-primary-700">
                          <Award className="h-4 w-4" />
                          {t(skillsKey)}
                        </span>
                      </div>
                      {/* Why this quest */}
                      <div className="rounded bg-white/60 p-4 border border-primary-200 mb-3">
                        <div className="flex items-start gap-2">
                          <Lightbulb className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                          <div>
                            <p className="text-caption font-bold uppercase tracking-wider text-primary-700 mb-1">
                              {t('recommended_quest.why_this_title')}
                            </p>
                            <p className="text-body-sm text-primary-800">
                              {isQA
                                ? t('recommended_quest.for_qa_why')
                                : t('recommended_quest.for_ba_why')}
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-3">
                        <Button
                          onClick={() => router.push(`/trainers/${slug}/quests/${questId}`)}
                          size="lg"
                          className="shadow-md px-6"
                        >
                          <Play className="h-5 w-5" />
                          {t('recommended_quest.start_recommended')}
                          <ArrowRight className="h-5 w-5" />
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => router.push(`/trainers/${slug}/quests`)}
                          size="md"
                        >
                          {t('recommended_quest.browse_all')}
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })()}
        </>
      )}

      {/* BA Trainer Phase 1 Modules Section — collapsed by default, shows first 4 */}
      {trainer.trainer_product_id === 'business_analyst_interview_trainer' && (
        <Card padding="lg" variant="default" className="mb-8">
          <CardHeader>
            <button
              type="button"
              onClick={() => setShowAllModules(!showAllModules)}
              className="w-full flex items-center justify-between gap-2 cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring rounded"
            >
              <div className="flex items-center gap-2">
                <ListChecks className="h-5 w-5 text-text-muted" />
                <CardTitle>{t('ba_trainer.modules')}</CardTitle>
              </div>
              <div className="flex items-center gap-2">
                <CardDescription>
                  {t('ba_trainer.module_activities')} — {t('ba_trainer.phase_1_badge')}
                </CardDescription>
                <svg
                  className={`w-5 h-5 text-text-muted transition-transform duration-200 ${showAllModules ? 'rotate-180' : ''}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>
          </CardHeader>
          <CardContent>
            {trainer.is_enrolled ? (
              <div className="space-y-3">
                {(showAllModules ? BA_MODULES : BA_MODULES.slice(0, 4)).map((mod) => (
                  <Link key={mod.module_id} href={`/trainers/${slug}/modules/${mod.module_id}`}>
                    <div className="flex items-center justify-between p-3 rounded border border-default hover:border-interactive transition-colors cursor-pointer">
                      <div>
                        <div className="font-medium text-foreground">
                          {t(`modules.${mod.module_id}.title`) !== `modules.${mod.module_id}.title`
                            ? t(`modules.${mod.module_id}.title`)
                            : mod.title}
                        </div>
                        <div className="text-body-sm text-text-secondary">
                          {t(`modules.${mod.module_id}.description`) !== `modules.${mod.module_id}.description`
                            ? t(`modules.${mod.module_id}.description`)
                            : mod.description}
                        </div>
                      </div>
                      <div className="text-body-sm text-text-muted whitespace-nowrap ml-4">
                        {pluralize(mod.activity_count, t('ba_trainer.activity_label_one'), t('ba_trainer.activity_label_few'), t('ba_trainer.activity_label_many'))}
                      </div>
                    </div>
                  </Link>
                ))}
                {BA_MODULES.length > 4 && (
                  <button
                    type="button"
                    onClick={() => setShowAllModules(!showAllModules)}
                    className="w-full text-center py-2 text-body-sm font-medium text-primary-600 hover:text-primary-700 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-ring rounded"
                  >
                    {showAllModules
                      ? t('ba_trainer.show_less_modules')
                      : ti('ba_trainer.show_n_modules', { n: String(BA_MODULES.length) })}
                  </button>
                )}
              </div>
            ) : (
              <div className="text-center py-6">
                <p className="text-body-sm text-text-secondary mb-4">
                  {t('trainer.notEnrolled')}
                </p>
                <Button
                  onClick={handleEnroll}
                  isLoading={enrollMutation.isPending}
                >
                  {t('trainer.enroll')}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Quest Catalog Section — secondary entry */}
      {trainer.is_enrolled && (
        <Card padding="lg" variant="default" className="mb-8 border-interactive">
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
            <div className="rounded bg-primary-50 p-4 mb-4 border border-primary-200">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-body-sm font-medium text-primary-800">
                    {t('trainer.immersiveExperience')}
                  </p>
                  <p className="mt-1 text-body-sm text-primary-700">
                    {t('trainer.immersiveExperienceDesc')}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* BA Trainer Phase 2 Scenarios Section */}
      {trainer.trainer_product_id === 'business_analyst_interview_trainer' && (
        <Card padding="lg" variant="default" className="mb-8 border-interactive">
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
            {trainer.is_enrolled ? (
              <>
                <div className="rounded bg-primary-50 p-4 mb-4 border border-primary-200">
                  <div className="flex items-start gap-3">
                    <Zap className="h-5 w-5 text-primary-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-body-sm font-medium text-primary-800">
                        {t('ba_phase2.how_it_works_title')}
                      </p>
                      <p className="mt-1 text-body-sm text-primary-700">
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
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <div className="text-center py-6">
                <p className="text-body-sm text-text-secondary mb-4">
                  {t('trainer.notEnrolled')}
                </p>
                <Button
                  onClick={handleEnroll}
                  isLoading={enrollMutation.isPending}
                >
                  {t('trainer.enroll')}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Details Grid */}
      <div className="grid gap-6 sm:grid-cols-2">
        {/* Target Audience */}
        {trainer.target_audience && trainer.target_audience.length > 0 && (
          <Card padding="md" variant="default">
            <CardHeader>
              <Users className="h-5 w-5 text-text-muted" />
              <CardTitle className="text-label text-text-secondary">
                {t("trainer.targetAudience")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-inside list-disc space-y-1 text-body-sm text-text-secondary">
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

        {/* Duration Estimate */}
        <Card padding="md" variant="default">
          <CardHeader>
            <Clock className="h-5 w-5 text-text-muted" />
            <CardTitle className="text-label text-text-secondary">
              {t("trainer.duration")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-body-sm text-text-secondary">
              {trainer.scenario_count} {t("trainer.scenarios").toLowerCase()}
            </p>
          </CardContent>
        </Card>
      </div>

    </PageContainer>
  );
}
