"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { getDomains, type DomainSummary } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import PageContainer from "@/components/ui/PageContainer";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { BookOpen, Users, ArrowRight, AlertCircle, Layers } from "lucide-react";

const domainIcons: Record<string, React.ReactNode> = {
  it: <BookOpen className="h-8 w-8" />,
  default: <Layers className="h-8 w-8" />,
};

function DomainCard({ domain }: { domain: DomainSummary }) {
  return (
    <Link href={`/domains/${domain.slug}`}>
      <Card hover padding="lg" className="h-full flex flex-col">
        <CardHeader>
          <div className="flex h-12 w-12 items-center justify-center rounded bg-primary-50 text-primary-600">
            {domainIcons[domain.slug] || domainIcons.default}
          </div>
          <div className="flex-1">
            <CardTitle>{domain.name}</CardTitle>
            {domain.description && (
              <CardDescription>{domain.description}</CardDescription>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex-1">
          <div className="flex items-center gap-1 text-body-sm text-text-secondary">
            <Users className="h-4 w-4" />
            <span>
              {domain.trainer_count} {domain.trainer_count === 1 ? t("trainer.title").toLowerCase() : t("trainer.scenarios").toLowerCase()}
            </span>
          </div>
        </CardContent>
        <div className="mt-3 flex items-center text-body-sm font-medium text-primary-600">
          <span>{t("common.next")}</span>
          <ArrowRight className="h-4 w-4" />
        </div>
      </Card>
    </Link>
  );
}

export default function DomainsPage() {
  const {
    data: domains,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["domains"],
    queryFn: getDomains,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" label={t("common.loading")} />
      </div>
    );
  }

  if (isError) {
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
    <PageContainer width="page" padding="default">
      <div className="mb-10 text-center">
        <h1 className="text-display text-foreground">{t("domains.title")}</h1>
        <p className="mt-3 text-body-lg text-text-secondary">{t("domains.subtitle")}</p>
      </div>

      {domains && domains.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {domains.map((domain) => (
            <DomainCard key={domain.id} domain={domain} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <Layers className="mx-auto h-16 w-16 text-text-muted" />
          <p className="mt-4 text-body-lg text-text-secondary">{t("common.comingSoon")}</p>
        </div>
      )}
    </PageContainer>
  );
}
