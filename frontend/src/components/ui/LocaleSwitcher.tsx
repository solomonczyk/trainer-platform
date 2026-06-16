"use client";

import { useState, useEffect, useCallback } from "react";
import { ChevronDown } from "lucide-react";
import clsx from "clsx";
import { getCurrentLocale, setLocale, localeOptions } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";

interface LocaleSwitcherProps {
  className?: string;
  variant?: "dropdown" | "buttons";
}

export default function LocaleSwitcher({
  className,
  variant = "dropdown",
}: LocaleSwitcherProps) {
  const [open, setOpen] = useState(false);
  const [currentLocale, setCurrentLocale] = useState<Locale>("ru-RU");

  const refreshLocale = useCallback(() => {
    setCurrentLocale(getCurrentLocale());
  }, []);

  useEffect(() => {
    refreshLocale();
    window.addEventListener("locale-changed", refreshLocale);
    return () => window.removeEventListener("locale-changed", refreshLocale);
  }, [refreshLocale]);

  const handleChange = (newLocale: Locale) => {
    setLocale(newLocale);
    setCurrentLocale(newLocale);
    setOpen(false);
    window.dispatchEvent(new CustomEvent("locale-changed"));
  };

  const locales = localeOptions();
  const currentLocaleLabel = locales.find((l) => l.value === currentLocale)?.label ?? currentLocale;

  if (variant === "buttons") {
    return (
      <div className={clsx("flex gap-1", className)}>
        {locales.map((loc) => (
          <button
            key={loc.value}
            type="button"
            onClick={() => handleChange(loc.value)}
            className={clsx(
              "px-2.5 py-1 rounded text-xs font-medium transition-colors",
              loc.value === currentLocale
                ? "bg-primary-100 text-primary-700"
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            )}
            aria-label={`Switch language to ${loc.label}`}
          >
            {loc.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={clsx("relative", className)}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-1 px-2 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
        aria-haspopup="true"
        aria-expanded={open ? "true" : "false"}
        aria-label="Switch language"
      >
        {currentLocaleLabel}
        <ChevronDown className="h-3.5 w-3.5" />
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-lg border border-gray-200 z-20 py-1">
            {locales.map((loc) => (
              <button
                key={loc.value}
                type="button"
                onClick={() => handleChange(loc.value)}
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
  );
}
