"use client";

import ru from "./ru-RU";
import en from "./en-US";

export type Locale = "ru-RU" | "en-US";
export type LocaleStrings = typeof ru;

const locales: Record<Locale, LocaleStrings> = {
  "ru-RU": ru,
  "en-US": en,
};

const DEFAULT_LOCALE: Locale = "ru-RU";

let currentLocale: Locale = DEFAULT_LOCALE;

export function setLocale(locale: Locale): void {
  currentLocale = locale;
  if (typeof window !== "undefined") {
    localStorage.setItem("preferred_locale", locale);
  }
}

export function getCurrentLocale(): Locale {
  return currentLocale;
}

export function loadSavedLocale(): Locale {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("preferred_locale");
    if (saved === "ru-RU" || saved === "en-US") {
      currentLocale = saved;
      return saved;
    }
  }
  return currentLocale;
}

export function t(key: string): string {
  const keys = key.split(".");
  let value: unknown = locales[currentLocale];
  for (const k of keys) {
    if (value && typeof value === "object" && k in value) {
      value = (value as Record<string, unknown>)[k];
    } else {
      return key;
    }
  }
  if (typeof value === "string") return value;
  return key;
}

// Simple interpolation: t("hello {name}", {name: "World"})
export function ti(key: string, params: Record<string, string | number>): string {
  let text = t(key);
  for (const [k, v] of Object.entries(params)) {
    text = text.replace(`{${k}}`, String(v));
  }
  return text;
}

export function localeOptions(): { value: Locale; label: string }[] {
  return [
    { value: "ru-RU", label: "Русский" },
    { value: "en-US", label: "English" },
  ];
}
