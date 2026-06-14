"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { isAuthenticated, getCurrentUser, type UserResponse } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardDescription, CardTitle } from "@/components/ui/Card";
import { GraduationCap, Brain, TrendingUp, ArrowRight } from "lucide-react";

export default function LandingPage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isAuthenticated()) {
      getCurrentUser()
        .then(setUser)
        .catch(() => setUser(null));
    }
  }, []);

  const features = [
    {
      icon: GraduationCap,
      title: t("landing.feature1Title"),
      description: t("landing.feature1Desc"),
    },
    {
      icon: Brain,
      title: t("landing.feature2Title"),
      description: t("landing.feature2Desc"),
    },
    {
      icon: TrendingUp,
      title: t("landing.feature3Title"),
      description: t("landing.feature3Desc"),
    },
  ];

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  const ctaHref = user ? "/domains" : "/register";
  const ctaLabel = user ? (t("nav.domains") || "Домены") : (t("landing.startButton") || "Начать обучение");

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 py-24 sm:py-32">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-20" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              {t("landing.heroTitle")}
            </h1>
            <p className="mt-6 text-lg leading-8 text-primary-100 sm:text-xl">
              {t("landing.heroSubtitle")}
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link href={ctaHref}>
                <Button
                  size="lg"
                  className="bg-white text-primary-700 hover:bg-primary-50 focus:ring-white"
                >
                  {ctaLabel}
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-bold text-gray-900 sm:text-4xl">
            {t("landing.features")}
          </h2>
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <Card key={index} padding="lg" className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-primary-100 text-primary-600">
                  <feature.icon className="h-7 w-7" />
                </div>
                <CardTitle className="mt-5 text-gray-900">{feature.title}</CardTitle>
                <CardDescription className="mt-2">{feature.description}</CardDescription>
              </Card>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
}
