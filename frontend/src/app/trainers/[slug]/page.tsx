"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
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
} from "lucide-react";

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
              <h1 className="text-3xl font-bold text-gray-900">{trainer.name}</h1>
              {trainer.description && (
                <p className="mt-1 text-gray-500">{trainer.description}</p>
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
          </div>

          {trainer.is_enrolled ? (
            <Button
              onClick={() => router.push(`/trainers/${slug}/scenarios`)}
            >
              {t("trainer.startScenario")}
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
                  <li key={idx}>{item}</li>
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

      {/* View Scenarios CTA (if enrolled) */}
      {trainer.is_enrolled && trainer.scenario_count > 0 && (
        <div className="mt-8 text-center">
          <Button
            size="lg"
            onClick={() => router.push(`/trainers/${slug}/scenarios`)}
          >
            {t("trainer.startScenario")}
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      )}
    </div>
  );
}
