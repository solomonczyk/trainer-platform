"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Menu, X, ChevronDown } from "lucide-react";
import clsx from "clsx";
import { logout } from "@/lib/api/client";
import { useAuth } from "@/lib/auth/AuthContext";
import { t, getCurrentLocale, setLocale, localeOptions } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";
import Button from "@/components/ui/Button";

interface HeaderProps {
  className?: string;
}

export default function Header({ className }: HeaderProps) {
  const router = useRouter();
  const { user, clearSession } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [localeSwitcherOpen, setLocaleSwitcherOpen] = useState(false);
  const [currentLocale, setCurrentLocale] = useState<Locale>("ru-RU");

  const refreshLocale = useCallback(() => {
    setCurrentLocale(getCurrentLocale());
  }, []);

  useEffect(() => {
    setMounted(true);
    refreshLocale();

    window.addEventListener("locale-changed", refreshLocale);
    return () => {
      window.removeEventListener("locale-changed", refreshLocale);
    };
  }, [refreshLocale]);

  const handleLogout = () => {
    logout();
    clearSession();
    router.push("/login");
  };

  const handleLocaleChange = (newLocale: Locale) => {
    setLocale(newLocale);
    setCurrentLocale(newLocale);
    setLocaleSwitcherOpen(false);
    window.dispatchEvent(new CustomEvent("locale-changed"));
  };

  const closeMobile = () => setMobileOpen(false);

  const locales = localeOptions();
  const currentLocaleLabel = locales.find((l) => l.value === currentLocale)?.label ?? currentLocale;

  if (!mounted) {
    return (
      <header className={clsx("border-b border-gray-200 bg-white", className)}>
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <span className="text-lg font-bold text-gray-900">{t("app.name")}</span>
        </div>
      </header>
    );
  }

  return (
    <header className={clsx("sticky top-0 z-50 border-b border-gray-200 bg-white/95 backdrop-blur", className)}>
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left section: Logo + Desktop Nav */}
        <div className="flex items-center gap-8">
          <Link href="/" className="text-lg font-bold text-gray-900 hover:text-primary-600 transition-colors" aria-label={t("app.name")}>
            {t("app.name")}
          </Link>
          <nav className="hidden md:flex items-center gap-6" aria-label="Main navigation">
            <Link
              href="/domains"
              className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            >
              {t("nav.domains")}
            </Link>
            {user && (
              <Link
                href="/me/dashboard"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                {t("nav.myProgress")}
              </Link>
            )}
            {user?.role === "admin" && (
              <Link
                href="/admin"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                {t("nav.admin")}
              </Link>
            )}
          </nav>
        </div>

        {/* Right section: Locale switcher + Profile + Auth */}
        <div className="hidden md:flex items-center gap-3">
          {/* Locale Switcher */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setLocaleSwitcherOpen((prev) => !prev)}
              className="flex items-center gap-1 px-2 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
              aria-haspopup="true"
              aria-expanded={localeSwitcherOpen ? "true" : "false"}
              aria-label={t("profile.language")}
            >
              {currentLocale}
              <ChevronDown className="h-3.5 w-3.5" />
            </button>

            {localeSwitcherOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setLocaleSwitcherOpen(false)}
                  aria-hidden="true"
                />
                <div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-lg border border-gray-200 z-20 py-1">
                  {locales.map((loc) => (
                    <button
                      key={loc.value}
                      type="button"
                      onClick={() => handleLocaleChange(loc.value)}
                      className={clsx(
                        "w-full text-left px-4 py-2 text-sm transition-colors",
                        loc.value === currentLocale
                          ? "bg-primary-50 text-primary-700 font-medium"
                          : "text-gray-700 hover:bg-gray-50"
                      )}
                    >
                      {loc.label}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {user ? (
            <>
              <Link
                href="/profile"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                {user.display_name || user.email}
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                {t("nav.logout")}
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  {t("nav.login")}
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">{t("nav.register")}</Button>
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          type="button"
          className="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen ? "true" : "false"}
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="px-4 py-3 space-y-1">
            <Link
              href="/domains"
              onClick={closeMobile}
              className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 transition-colors"
            >
              {t("nav.domains")}
            </Link>

            {user && (
              <Link
                href="/me/dashboard"
                onClick={closeMobile}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 transition-colors"
              >
                {t("nav.myProgress")}
              </Link>
            )}

            {user?.role === "admin" && (
              <Link
                href="/admin"
                onClick={closeMobile}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 transition-colors"
              >
                {t("nav.admin")}
              </Link>
            )}

            <hr className="my-2 border-gray-200" />

            {user ? (
              <>
                <Link
                  href="/profile"
                  onClick={closeMobile}
                  className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50 transition-colors"
                >
                  {t("nav.profile")}
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    closeMobile();
                    handleLogout();
                  }}
                  className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  {t("nav.logout")}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={closeMobile}
                  className="block px-3 py-2 rounded-md text-base font-medium text-primary-600 hover:bg-primary-50 transition-colors"
                >
                  {t("nav.login")}
                </Link>
                <Link
                  href="/register"
                  onClick={closeMobile}
                  className="block px-3 py-2 rounded-md text-base font-medium text-primary-600 hover:bg-primary-50 transition-colors"
                >
                  {t("nav.register")}
                </Link>
              </>
            )}

            {/* Mobile locale switcher */}
            <hr className="my-2 border-gray-200" />
            <div className="px-3 py-2">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                {t("profile.language")}
              </p>
              <div className="flex gap-2">
                {locales.map((loc) => (
                  <button
                    key={loc.value}
                    type="button"
                    onClick={() => {
                      handleLocaleChange(loc.value);
                      closeMobile();
                    }}
                    className={clsx(
                      "flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                      loc.value === currentLocale
                        ? "bg-primary-100 text-primary-700"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    )}
                  >
                    {loc.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
