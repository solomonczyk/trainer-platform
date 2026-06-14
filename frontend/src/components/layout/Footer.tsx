"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import clsx from "clsx";
import { t, getCurrentLocale, setLocale, localeOptions } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";

interface FooterProps {
  className?: string;
}

export default function Footer({ className }: FooterProps) {
  const [currentLocale, setCurrentLocale] = useState<Locale>("ru-RU");

  const refreshLocale = useCallback(() => {
    setCurrentLocale(getCurrentLocale());
  }, []);

  useEffect(() => {
    refreshLocale();
    window.addEventListener("locale-changed", refreshLocale);
    return () => window.removeEventListener("locale-changed", refreshLocale);
  }, [refreshLocale]);

  const handleLocaleChange = (newLocale: Locale) => {
    setLocale(newLocale);
    setCurrentLocale(newLocale);
    window.dispatchEvent(new CustomEvent("locale-changed"));
  };

  const locales = localeOptions();
  const year = new Date().getFullYear();

  return (
    <footer className={clsx("border-t border-gray-200 bg-white", className)}>
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <Link href="/" className="text-lg font-bold text-gray-900 hover:text-primary-600 transition-colors">
              {t("app.name")}
            </Link>
            <p className="mt-2 text-sm text-gray-500">{t("app.tagline")}</p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">
              {t("nav.domains")}
            </h3>
            <ul className="mt-3 space-y-2">
              <li>
                <Link href="/domains" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">
                  {t("nav.domains")}
                </Link>
              </li>
              <li>
                <Link href="/me/dashboard" className="text-sm text-gray-500 hover:text-gray-700 transition-colors">
                  {t("nav.myProgress")}
                </Link>
              </li>
            </ul>
          </div>

          {/* Locale Switcher */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider">
              {t("profile.language")}
            </h3>
            <div className="mt-3 flex gap-2">
              {locales.map((loc) => (
                <button
                  key={loc.value}
                  type="button"
                  onClick={() => handleLocaleChange(loc.value)}
                  className={clsx(
                    "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
                    loc.value === currentLocale
                      ? "bg-primary-100 text-primary-700"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  )}
                  aria-label={`Switch language to ${loc.label}`}
                >
                  {loc.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-8 pt-6 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-sm text-gray-400">
            &copy; {year} {t("app.name")}. All rights reserved.
          </p>
          {/* Locale labels — shown in locale switcher above */}
        </div>
      </div>
    </footer>
  );
}
