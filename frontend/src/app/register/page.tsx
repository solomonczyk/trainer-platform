"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, ApiClientError } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription } from "@/components/ui/Card";
import PasswordInput from "@/components/ui/PasswordInput";
import Input from "@/components/ui/Input";
import { AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): string | null => {
    if (!email.trim()) return t("common.error");
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return t("common.error");
    if (password.length < 6) return t("common.error");
    if (password !== confirmPassword) return t("common.error");
    return null;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    try {
      await register(email.toLowerCase().trim(), password, displayName.trim() || undefined);
      router.push(`/verify-email?email=${encodeURIComponent(email.toLowerCase().trim())}`);
    } catch (err) {
      if (err instanceof ApiClientError) {
        switch (err.code) {
          case "CONFLICT":
          case "EMAIL_TAKEN":
            setError(t("auth.errorEmailTaken"));
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
          <CardTitle className="text-h3 text-foreground">{t("auth.registerTitle")}</CardTitle>
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
            id="displayName"
            label={t("auth.displayName")}
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="John Doe"
            autoComplete="name"
          />

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

          <PasswordInput
            id="password"
            label={t("auth.password")}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t("auth.passwordPlaceholder")}
            required
            minLength={6}
            autoComplete="new-password"
          />

          <PasswordInput
            id="confirmPassword"
            label={t("auth.confirmPassword")}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t("auth.confirmPasswordPlaceholder")}
            required
            autoComplete="new-password"
          />
          {password !== confirmPassword && confirmPassword.length > 0 && (
            <p className="-mt-3 text-body-xs text-danger-500">{t("common.error")}</p>
          )}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            className="w-full"
          >
            {t("auth.registerButton")}
          </Button>
        </form>

        <p className="mt-6 text-center text-body-sm text-text-secondary">
          {t("auth.hasAccount")}{" "}
          <Link
            href="/login"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            {t("auth.loginLink")}
          </Link>
        </p>
      </Card>
    </div>
  );
}
