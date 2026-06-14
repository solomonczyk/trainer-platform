"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login, ApiClientError } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription } from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import { AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError(t("common.error"));
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      router.push("/domains");
    } catch (err) {
      if (err instanceof ApiClientError) {
        switch (err.code) {
          case "INVALID_CREDENTIALS":
            setError(t("auth.errorInvalidCredentials"));
            break;
          case "USER_NOT_FOUND":
            setError(t("auth.errorInvalidCredentials"));
            break;
          default:
            setError(err.message || t("common.error"));
        }
      } else {
        setError(t("common.error"));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
      <Card padding="lg" className="w-full max-w-md">
        <div className="mb-6 text-center">
          <CardTitle className="text-h3 text-foreground">{t("auth.loginTitle")}</CardTitle>
          <CardDescription className="mt-2">{t("app.tagline")}</CardDescription>
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2 rounded bg-danger-50 p-3 text-body-sm text-danger-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            id="email"
            label={t("auth.email")}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
          />

          <Input
            id="password"
            label={t("auth.password")}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            autoComplete="current-password"
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            className="w-full"
          >
            {t("auth.loginButton")}
          </Button>
        </form>

        <p className="mt-6 text-center text-body-sm text-text-secondary">
          {t("auth.noAccount")}{" "}
          <Link
            href="/register"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            {t("auth.registerLink")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
