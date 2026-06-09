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
  // Skip empty/falsy keys
  if (!key) return key;

  // Support dotted keys at any level — try the full key as-is first
  const root = locales[currentLocale] as Record<string, unknown>;
  if (key in root) {
    const direct = root[key];
    if (typeof direct === "string") return direct;
  }

  // Dotted-path traversal with dotted-key fallback at each level
  const parts = key.split(".");
  let value: unknown = root;
  let i = 0;
  while (i < parts.length) {
    const seg = parts[i];
    if (value && typeof value === "object" && seg in (value as Record<string, unknown>)) {
      value = (value as Record<string, unknown>)[seg];
      i++;
    } else {
      // Try combining remaining segments as a single dotted key at this level
      let found = false;
      for (let j = parts.length - 1; j > i; j--) {
        const dotted = parts.slice(i, j + 1).join(".");
        if (value && typeof value === "object" && dotted in (value as Record<string, unknown>)) {
          value = (value as Record<string, unknown>)[dotted];
          i = j + 1;
          found = true;
          break;
        }
      }
      // Also try at root level using progressive prefix
      if (!found) {
        // Try full key at root, back to partial prefix
        for (let j = parts.length - 1; j >= i; j--) {
          // Try from start of key to j — this handles cases like
          // "quest.qa.payment_defect" being a root key while
          // traversal already consumed "quest" as first segment
          const dotted = parts.slice(0, j + 1).join(".");
          if (dotted in root) {
            value = root[dotted];
            i = j + 1;
            found = true;
            break;
          }
        }
      }
      if (!found) return key;
    }
  }
  if (typeof value === "string") return value;
  return key;
}

/**
 * Safe translate: returns translated text for the given key, or
 * the key itself if not found. Use this when the key IS the fallback
 * display value and you don't want to show raw translation keys.
 *
 * For scenario title_key/goal_key usage:
 *   tl(scenario.title_key)  // translates if key exists, shows key as-is otherwise
 *
 * Unlike bare `t()`, this never shows raw `scenario.xxx.title` keys.
 */
export function tl(key: string): string {
  if (!key) return "";
  const result = t(key);
  // If translation returned the key unchanged, the key was not found
  if (result === key) {
    // For dot-separated keys like "scenario.qa_xxx.title", return a
    // cleaned-up fallback derived from the last segment
    const lastSegment = key.split(".").pop() || key;
    return lastSegment.replace(/_/g, " ");
  }
  return result;
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
