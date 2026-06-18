"use client";

import Link from "next/link";
import { t } from "@/lib/i18n";
import PageContainer from "@/components/ui/PageContainer";
import Button from "@/components/ui/Button";

interface AuthRequiredGateProps {
  redirectTo?: string;
  /** Override heading text (e.g. "Sign in required for this trainer"). Defaults to auth.sign_in_required. */
  headingKey?: string;
  /** Override description text. Defaults to auth.sign_in_required_description. */
  descriptionKey?: string;
}

/**
 * Reusable auth gate shown when the user is unauthenticated and
 * tries to access a protected route.
 *
 * Renders a centered card with localized heading, description, and
 * a "Sign In" button that preserves the intended redirect.
 */
export function AuthRequiredGate({
  redirectTo,
  headingKey = "auth.sign_in_required",
  descriptionKey = "auth.sign_in_required_description",
}: AuthRequiredGateProps) {
  const href = redirectTo
    ? `/login?redirect=${encodeURIComponent(redirectTo)}`
    : "/login";

  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="mx-auto max-w-md rounded-xl border bg-white p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 text-text-muted">
            <svg
              className="h-8 w-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
              />
            </svg>
          </div>

          <h1 className="text-xl font-semibold text-foreground">
            {t(headingKey)}
          </h1>

          <p className="mt-2 text-sm text-text-secondary">
            {t(descriptionKey)}
          </p>

          <Link href={href} className="mt-6 inline-block">
            <Button size="lg">{t("auth.sign_in")}</Button>
          </Link>
        </div>
      </div>
    </PageContainer>
  );
}
