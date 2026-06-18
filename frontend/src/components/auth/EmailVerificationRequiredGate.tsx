"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { t } from "@/lib/i18n";
import { resendVerification } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";
import PageContainer from "@/components/ui/PageContainer";
import Button from "@/components/ui/Button";
import { AlertCircle, CheckCircle, Mail } from "lucide-react";

/**
 * Email verification gate.
 *
 * Shown when the user IS authenticated but their email is NOT verified.
 * Offers to resend the verification email or return to login.
 */
export function EmailVerificationRequiredGate() {
  const router = useRouter();
  const { user } = useAuth();
  const [resending, setResending] = useState(false);
  const [resent, setResent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleResend = async () => {
    if (!user?.email) return;
    setResending(true);
    setError(null);
    try {
      await resendVerification(user.email);
      setResent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setResending(false);
    }
  };

  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="mx-auto max-w-md rounded-xl border bg-white p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-amber-100 text-amber-600">
            <Mail className="h-8 w-8" />
          </div>

          <h1 className="text-xl font-semibold text-foreground">
            {t("auth.verificationRequiredTitle")}
          </h1>

          <p className="mt-2 text-sm text-text-secondary">
            {t("auth.verificationRequiredDesc")}
          </p>

          {resent && (
            <div className="mt-4 flex items-center gap-2 rounded bg-success-50 p-3 text-body-sm text-success-700">
              <CheckCircle className="h-4 w-4 flex-shrink-0" />
              {t("auth.verificationResent")}
            </div>
          )}

          {error && (
            <div className="mt-4 flex items-center gap-2 rounded bg-danger-50 p-3 text-body-sm text-danger-700">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <div className="mt-6 flex flex-col gap-3">
            <Button
              onClick={handleResend}
              isLoading={resending}
              size="lg"
            >
              {t("auth.resendVerificationButton")}
            </Button>

            <Button
              variant="outline"
              onClick={() => router.push("/login")}
            >
              {t("auth.backToLogin")}
            </Button>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
