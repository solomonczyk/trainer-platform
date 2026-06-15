"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  verifyEmail,
  resendVerification,
  getCurrentUser,
  isAuthenticated,
  setToken,
  clearToken,
  type UserResponse,
} from "@/lib/api/client";
import { t } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardTitle, CardDescription } from "@/components/ui/Card";
import { CheckCircle, AlertCircle, Mail, Loader2, LogOut, User } from "lucide-react";

type PageState =
  | { status: "loading" }
  | { status: "pending" }
  | { status: "verifying" }
  | { status: "success"; verifiedEmail?: string }
  | { status: "error"; message: string }
  | { status: "already_verified" }
  | { status: "token_expired" }
  | { status: "resent" };

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [state, setState] = useState<PageState>({ status: "loading" });
  const [resendEmail, setResendEmail] = useState("");
  const [resending, setResending] = useState(false);
  const [cooldownSec, setCooldownSec] = useState(0);
  const cooldownTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const COOLDOWN_DURATION = 60;

  // Session identity bar — staging/debug only, disabled for production
  const showDebugBar = process.env.NEXT_PUBLIC_APP_ENV !== "production";

  // Session identity — shows who is currently logged in
  const [sessionUser, setSessionUser] = useState<UserResponse | null>(null);
  const [sessionLoading, setSessionLoading] = useState(true);

  // Detect current session on mount
  useEffect(() => {
    if (isAuthenticated()) {
      getCurrentUser()
        .then((u) => setSessionUser(u))
        .catch(() => setSessionUser(null))
        .finally(() => setSessionLoading(false));
    } else {
      setSessionLoading(false);
    }
  }, []);

  // On mount, pre-fill email from query param or check auth
  useEffect(() => {
    const emailParam = searchParams.get("email");
    if (emailParam) {
      setResendEmail(emailParam);
    } else if (isAuthenticated()) {
      getCurrentUser()
        .then((u) => setResendEmail(u.email))
        .catch(() => {});
    }
  }, [searchParams]);

  useEffect(() => {
    if (!token) {
      setState({ status: "pending" });
      return;
    }

    setState({ status: "verifying" });
    verifyEmail(token)
      .then((res) => {
        if (res.access_token) {
          setToken(res.access_token);
        }
        // Show verified email so operator can confirm identity
        setState({ status: "success", verifiedEmail: res.email || undefined });
        // Refresh session identity with new token
        getCurrentUser()
          .then((u) => setSessionUser(u))
          .catch(() => {});
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

  // Poll /me every 5s while on pending/resent/success screens
  useEffect(() => {
    if (state.status !== "pending" && state.status !== "resent" && state.status !== "success") return;
    const interval = setInterval(async () => {
      try {
        const user = await getCurrentUser();
        setSessionUser(user);
        if (user.email_verified) {
          setState((prev) =>
            prev.status === "success" ? prev : { status: "success", verifiedEmail: user.email }
          );
        }
      } catch {
        // Not authenticated — stay on current state
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [state.status]);

  // Cleanup cooldown timer
  useEffect(() => {
    return () => {
      if (cooldownTimer.current) clearInterval(cooldownTimer.current);
    };
  }, []);

  const handleClearSession = useCallback(() => {
    clearToken();
    setSessionUser(null);
    setState({ status: "pending" });
  }, []);

  const handleResend = useCallback(async () => {
    if (!resendEmail.trim() || cooldownSec > 0) return;
    setResending(true);
    try {
      await resendVerification(resendEmail);
      setState({ status: "resent" });
      setCooldownSec(COOLDOWN_DURATION);
      cooldownTimer.current = setInterval(() => {
        setCooldownSec((prev) => {
          if (prev <= 1) {
            if (cooldownTimer.current) clearInterval(cooldownTimer.current);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to resend";
      setState({ status: "error", message: msg });
    } finally {
      setResending(false);
    }
  }, [resendEmail, cooldownSec]);

  const handleCheckStatus = useCallback(async () => {
    try {
      const user = await getCurrentUser();
      setSessionUser(user);
      if (user.email_verified) {
        router.push("/domains");
      } else {
        setState({
          status: "error",
          message: "Email not yet verified. Please check your inbox and click the verification link.",
        });
      }
    } catch {
      setState({
        status: "error",
        message: "Unable to check status. Please ensure you are logged in.",
      });
    }
  }, [router]);

  // ── Session identity bar ────────────────────────────────────
  const SessionBar = ({ extra }: { extra?: React.ReactNode }) => (
    <div className="mb-4 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
      {sessionLoading ? (
        <div className="flex items-center gap-2 text-sm text-text-tertiary">
          <Loader2 className="h-3 w-3 animate-spin" />
          Checking session...
        </div>
      ) : sessionUser ? (
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-sm">
            <User className="h-4 w-4 text-primary-600" />
            <span className="font-medium text-text-primary">{sessionUser.email}</span>
            {sessionUser.email_verified ? (
              <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">Verified</span>
            ) : (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">Unverified</span>
            )}
          </div>
          <button
            onClick={handleClearSession}
            className="flex items-center gap-1 rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50 hover:text-red-700"
            title="Clear session and start fresh"
          >
            <LogOut className="h-3 w-3" />
            Clear
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-sm text-text-tertiary">
          <User className="h-4 w-4" />
          No active session
        </div>
      )}
      {extra}
    </div>
  );

  // ── Loading ─────────────────────────────────────────────────
  if (state.status === "loading") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
      </div>
    );
  }

  // ── Pending — "Check your email" ────────────────────────────
  if (state.status === "pending") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          {showDebugBar && <SessionBar />}
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
            <Mail className="h-8 w-8 text-primary-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailCheckTitle")}</CardTitle>
          <CardDescription className="mt-3">
            {t("auth.verifyEmailCheckDesc")}
          </CardDescription>
          <p className="mt-2 text-xs text-text-tertiary">
            {t("auth.verifyEmailSpamHint")}
          </p>

          <div className="mt-8 space-y-3 border-t border-border pt-6">
            <p className="text-sm font-medium text-text-secondary">
              {t("auth.verifyEmailResendPrompt")}
            </p>
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
              disabled={!resendEmail.trim() || cooldownSec > 0}
            >
              {cooldownSec > 0
                ? t("auth.verifyEmailResendCooldown").replace("{seconds}", String(cooldownSec))
                : t("auth.verifyEmailResendButton")}
            </Button>

            <Button
              variant="outline"
              className="w-full"
              onClick={handleCheckStatus}
            >
              {t("auth.verifyEmailCheckStatus")}
            </Button>
          </div>

          <div className="mt-4">
            <Link
              href="/login"
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              {t("auth.verifyEmailBackToLogin")}
            </Link>
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
          {showDebugBar && <SessionBar
            extra={
              state.verifiedEmail ? (
                <p className="mt-1 text-xs text-green-600">
                  Just verified: {state.verifiedEmail}
                </p>
              ) : null
            }
          />}
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailSuccessTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailSuccessDesc")}</CardDescription>

          {state.verifiedEmail && (
            <p className="mt-2 rounded bg-green-50 px-3 py-1.5 text-sm font-medium text-green-700">
              {state.verifiedEmail}
            </p>
          )}

          <div className="mt-6 space-y-3">
            <Button
              variant="primary"
              className="w-full"
              onClick={handleCheckStatus}
            >
              {t("auth.verifyEmailCheckStatus")}
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={handleClearSession}
            >
              Clear Session
            </Button>
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
          {showDebugBar && <SessionBar />}
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
          {showDebugBar && <SessionBar />}
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
              disabled={!resendEmail.trim() || cooldownSec > 0}
            >
              {cooldownSec > 0
                ? t("auth.verifyEmailResendCooldown").replace("{seconds}", String(cooldownSec))
                : t("auth.verifyEmailResendButton")}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ── Resent confirmation ────────────────────────────────────
  if (state.status === "resent") {
    return (
      <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
        <Card padding="lg" className="w-full max-w-md text-center">
          {showDebugBar && <SessionBar />}
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl">{t("auth.verifyEmailSentTitle")}</CardTitle>
          <CardDescription className="mt-3">{t("auth.verifyEmailSentDesc")}</CardDescription>
          <p className="mt-2 text-xs text-text-tertiary">
            {t("auth.verifyEmailSpamHint")}
          </p>

          <div className="mt-6 space-y-3">
            <Button
              variant="outline"
              className="w-full"
              isLoading={resending}
              onClick={handleResend}
              disabled={cooldownSec > 0}
            >
              {cooldownSec > 0
                ? t("auth.verifyEmailResendCooldown").replace("{seconds}", String(cooldownSec))
                : t("auth.verifyEmailResendButton")}
            </Button>

            <Button
              variant="primary"
              className="w-full"
              onClick={handleCheckStatus}
            >
              {t("auth.verifyEmailCheckStatus")}
            </Button>
          </div>

          <div className="mt-4">
            <Link
              href="/login"
              className="text-sm text-primary-600 hover:text-primary-500"
            >
              {t("auth.verifyEmailBackToLogin")}
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  // ── Error ─────────────────────────────────────────────────
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4 py-12">
      <Card padding="lg" className="w-full max-w-md text-center">
        <SessionBar />
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <AlertCircle className="h-8 w-8 text-red-600" />
        </div>
        <CardTitle className="text-2xl">{t("common.error")}</CardTitle>
        <CardDescription className="mt-3">
          {state.status === "error" ? state.message : ""}
        </CardDescription>
        <div className="mt-6 space-y-3">
          <Link href="/verify-email">
            <Button variant="outline" className="w-full">{t("auth.verifyEmailBackToLogin")}</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
