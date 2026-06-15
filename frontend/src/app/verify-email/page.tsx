"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { verifyEmail, resendVerification, isAuthenticated, logout } from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription } from "@/components/ui/Card";
import { CheckCircle, AlertCircle, Mail, Loader2 } from "lucide-react";

type PageState =
  | { status: "loading" }
  | { status: "pending" }  // no token — show "check your email"
  | { status: "verifying" }
  | { status: "success" }
  | { status: "error"; message: string }
  | { status: "already_verified" }
  | { status: "token_expired" }
  | { status: "resent"; message: string };

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [state, setState] = useState<PageState>({ status: "loading" });
  const [resendEmail, setResendEmail] = useState("");
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (!token) {
      // No token — show "check your email" screen
      // Pre-fill email if user is authenticated
      setState({ status: "pending" });
      return;
    }

    setState({ status: "verifying" });
    verifyEmail(token)
      .then(() => {
        setState({ status: "success" });
        // Auto-redirect after 3 seconds
        setTimeout(() => router.push("/domains"), 3000);
      })
      .catch((err) => {
        const code = err?.code || "";
        if (code === "TOKEN_ALREADY_USED") {
          setState({ status: "already_verified" });
        } else if (code === "TOKEN_EXPIRED") {
          setState({ status: "token_expired" });
        } else {
          setState({ status: "error", message: err?.message || "Verification failed" });
        }
      });
  }, [token, router]);

  const handleResend = useCallback(async () => {
    if (!resendEmail.trim()) return;
    setResending(true);
    try {
      await resendVerification(resendEmail);
      setState({ status: "resent", message: "Verification email sent. Please check your inbox." });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to resend";
      setState({ status: "error", message: msg });
    } finally {
      setResending(false);
    }
  }, [resendEmail]);

  if (state.status === "loading") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  // ── No token — "Check your email" ──────────────────────────
  if (state.status === "pending") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
            <Mail className="h-8 w-8 text-primary-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailCheckTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailCheckDesc")}</CardDescription>

          <div className="mt-8 space-y-4">
            <Link href="/domains">
              <Button variant="outline" className="w-full">
                {t("auth.verifyEmailGoToDomains")}
              </Button>
            </Link>
            <button
              type="button"
              onClick={() => router.push("/login")}
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              {t("auth.backToLogin")}
            </button>
          </div>
        </Card>
      </div>
    );
  }

  // ── Verifying ──────────────────────────────────────────────
  if (state.status === "verifying") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary-600" />
          <CardTitle className="mt-4 text-2xl">{t("auth.verifyEmailVerifying")}</CardTitle>
        </Card>
      </div>
    );
  }

  // ── Success ────────────────────────────────────────────────
  if (state.status === "success") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailSuccessTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailSuccessDesc")}</CardDescription>
          <div className="mt-6">
            <Link href="/domains">
              <Button variant="primary" className="w-full">{t("common.continue")}</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // ── Already verified ───────────────────────────────────────
  if (state.status === "already_verified") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
            <CheckCircle className="h-8 w-8 text-blue-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailAlreadyTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailAlreadyDesc")}</CardDescription>
          <div className="mt-6">
            <Link href="/login">
              <Button variant="primary" className="w-full">{t("auth.loginLink")}</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // ── Token expired ──────────────────────────────────────────
  if (state.status === "token_expired") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100">
            <AlertCircle className="h-8 w-8 text-amber-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailExpiredTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailExpiredDesc")}</CardDescription>
          <div className="mt-6 space-y-3">
            <input
              type="email"
              value={resendEmail}
              onChange={(e) => setResendEmail(e.target.value)}
              placeholder="you@example.com"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            />
            <Button
              variant="primary"
              className="w-full"
              isLoading={resending}
              onClick={handleResend}
              disabled={!resendEmail.trim()}
            >
              {t("auth.resendVerificationButton")}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ── Error / Resent ─────────────────────────────────────────
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
      <Card padding="lg" className="w-full max-w-md text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <AlertCircle className="h-8 w-8 text-red-600" />
        </div>
        <CardTitle className="text-2xl">
          {state.status === "resent" ? t("common.success") : t("common.error")}
        </CardTitle>
        <CardDescription className="mt-3">
          {state.status === "resent" ? state.message : state.status === "error" ? state.message : ""}
        </CardDescription>
        <div className="mt-6">
          <Link href="/login">
            <Button variant="outline" className="w-full">{t("auth.backToLogin")}</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
