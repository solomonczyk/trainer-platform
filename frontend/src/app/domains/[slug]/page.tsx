"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getDomain } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import PageContainer from "@/components/ui/PageContainer";
import { ArrowLeft, Users, AlertCircle, GraduationCap } from "lucide-react";

export default function DomainDetailPage() {
  const params = useParams();
  const slug = params?.slug as string;

  const {
    data: domain,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["domain", slug],
    queryFn: () => getDomain(slug),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  if (isError || !domain) {
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

  return (
    <PageContainer>
      {/* Back Link */}
      <Link
        href="/domains"
        className="mb-6 inline-flex items-center gap-1.5 text-label text-text-secondary hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        {t("domains.backToDomains")}
      </Link>

      {/* Domain Header */}
      <div className="mb-10">
        <div className="flex items-center gap-4">
          {domain.icon && (
            <div className="flex h-14 w-14 items-center justify-center rounded bg-primary-50 text-primary-600 text-2xl">
              {domain.icon}
            </div>
          )}
          <div>
            <h1 className="text-h2 text-foreground">
              {t(`domains.${domain.slug}`) !== `domains.${domain.slug}`
                ? t(`domains.${domain.slug}`)
                : domain.name}
            </h1>
            {domain.description && (
              <p className="mt-2 text-body-lg text-text-secondary">
                {t(`domains.${domain.slug}Description`) !== `domains.${domain.slug}Description`
                  ? t(`domains.${domain.slug}Description`)
                  : domain.description}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Trainers Section */}
      <h2 className="mb-6 text-h3 text-foreground">
        {t("domains.trainersIn")}
      </h2>

      {domain.trainers && domain.trainers.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {domain.trainers.map((trainer) => (
            <Link key={trainer.id} href={`/trainers/${trainer.slug}`}>
              <Card hover padding="md" className="h-full">
                <CardHeader>
                  <div className="flex h-10 w-10 items-center justify-center rounded bg-muted text-text-secondary">
                    <GraduationCap className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-body font-semibold">
                      {t(`trainer.${trainer.slug.replace(/-/g, '_')}`) !== `trainer.${trainer.slug.replace(/-/g, '_')}`
                        ? t(`trainer.${trainer.slug.replace(/-/g, '_')}`)
                        : trainer.name}
                    </CardTitle>
                    {trainer.description && (
                      <CardDescription className="line-clamp-2">
                        {t(`trainer.${trainer.slug.replace(/-/g, '_')}_desc`) !== `trainer.${trainer.slug.replace(/-/g, '_')}_desc`
                          ? t(`trainer.${trainer.slug.replace(/-/g, '_')}_desc`)
                          : trainer.description}
                      </CardDescription>
                    )}
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card padding="lg" className="text-center">
          <Users className="mx-auto h-12 w-12 text-text-muted" />
          <p className="mt-3 text-body text-text-secondary">{t("common.comingSoon")}</p>
        </Card>
      )}
    </PageContainer>
  );
}
