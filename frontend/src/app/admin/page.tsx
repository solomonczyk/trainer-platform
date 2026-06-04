"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getCurrentUser, getDomains, isAuthenticated, type UserResponse } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { AlertCircle, Shield, Database, RefreshCw, Activity, CheckCircle, XCircle, Server, Users, BookOpen, FileText, Globe, Layers, Award } from "lucide-react";
import { useRouter } from "next/navigation";

interface SeedCounts {
  domains: number;
  trainers: number;
  scenarios: number;
  rubrics: number;
  locales: number;
  skills: number;
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  color: string;
}) {
  return (
    <Card padding="md" className="flex items-center gap-4">
      <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-xl font-bold text-gray-900">{value}</p>
      </div>
    </Card>
  );
}

export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [authChecking, setAuthChecking] = useState(true);
  const [seedCounts, setSeedCounts] = useState<SeedCounts | null>(null);
  const [loadingSeed, setLoadingSeed] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login?redirect=/admin");
      return;
    }

    getCurrentUser()
      .then((u) => {
        setUser(u);
        if (u.role !== "admin") {
          router.push("/");
        }
      })
      .catch(() => {
        router.push("/login?redirect=/admin");
      })
      .finally(() => {
        setAuthChecking(false);
      });
  }, [router]);

  // Fetch seed counts via domains
  const {
    data: domainsData,
    isLoading: domainsLoading,
    refetch: refetchDomains,
  } = useQuery({
    queryKey: ["admin-domains"],
    queryFn: getDomains,
    enabled: !!user && user.role === "admin",
  });

  useEffect(() => {
    if (domainsData) {
      const totalTrainers = domainsData.reduce((sum, d) => sum + d.trainer_count, 0);
      setSeedCounts({
        domains: domainsData.length,
        trainers: totalTrainers,
        scenarios: 0,
        rubrics: 0,
        locales: 0,
        skills: 0,
      });
      setLoadingSeed(false);
    } else if (!domainsLoading) {
      setLoadingSeed(false);
    }
  }, [domainsData, domainsLoading]);

  if (authChecking) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (!user || user.role !== "admin") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Shield className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.forbidden")}</p>
        <Button onClick={() => router.push("/")}>
          {t("nav.home")}
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">{t("admin.title")}</h1>
          </div>
          <p className="mt-2 text-gray-500">
            {user.display_name || user.email}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetchDomains()}
          isLoading={domainsLoading}
        >
          <RefreshCw className="mr-1.5 h-4 w-4" />
          {t("admin.refresh")}
        </Button>
      </div>

      {/* Seed Status Section */}
      <div className="mb-10">
        <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-gray-900">
          <Database className="h-5 w-5 text-gray-400" />
          {t("admin.seedStatus")}
        </h2>

        {loadingSeed ? (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
            {t("common.loading")}
          </div>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              icon={<Layers className="h-5 w-5 text-white" />}
              label={t("admin.domains")}
              value={seedCounts?.domains ?? 0}
              color="bg-blue-500"
            />
            <StatCard
              icon={<Users className="h-5 w-5 text-white" />}
              label={t("admin.trainers")}
              value={seedCounts?.trainers ?? 0}
              color="bg-green-500"
            />
            <StatCard
              icon={<BookOpen className="h-5 w-5 text-white" />}
              label={t("admin.scenarios")}
              value={seedCounts?.scenarios ?? 0}
              color="bg-purple-500"
            />
            <StatCard
              icon={<FileText className="h-5 w-5 text-white" />}
              label={t("admin.rubrics")}
              value={seedCounts?.rubrics ?? 0}
              color="bg-orange-500"
            />
            <StatCard
              icon={<Globe className="h-5 w-5 text-white" />}
              label={t("admin.locales")}
              value={seedCounts?.locales ?? 0}
              color="bg-teal-500"
            />
            <StatCard
              icon={<Award className="h-5 w-5 text-white" />}
              label={t("admin.skills")}
              value={seedCounts?.skills ?? 0}
              color="bg-pink-500"
            />
          </div>
        )}
      </div>

      {/* System Health */}
      <div className="mb-10">
        <h2 className="mb-4 flex items-center gap-2 text-xl font-semibold text-gray-900">
          <Activity className="h-5 w-5 text-gray-400" />
          {t("admin.systemHealth")}
        </h2>
        <Card padding="md">
          <div className="flex items-center gap-3">
            {domainsData ? (
              <CheckCircle className="h-6 w-6 text-green-500" />
            ) : (
              <XCircle className="h-6 w-6 text-red-500" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-900">
                {domainsData ? "API Connected" : "API Disconnected"}
              </p>
              <p className="text-xs text-gray-400">
                {domainsData
                  ? `${domainsData.length} domains loaded successfully`
                  : "Unable to reach the backend API"}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="mb-10">
        <h2 className="mb-4 text-xl font-semibold text-gray-900">Actions</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Card padding="md" hover onClick={() => router.push("/domains")}>
            <CardHeader>
              <Layers className="h-5 w-5 text-primary-600" />
              <CardTitle className="text-sm font-medium text-gray-900">
                {t("nav.domains")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500">
                View and manage domain catalog
              </p>
            </CardContent>
          </Card>

          <Card padding="md" hover onClick={() => router.push("/me/dashboard")}>
            <CardHeader>
              <Server className="h-5 w-5 text-primary-600" />
              <CardTitle className="text-sm font-medium text-gray-900">
                {t("nav.myProgress")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-500">
                View user progress and analytics
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
