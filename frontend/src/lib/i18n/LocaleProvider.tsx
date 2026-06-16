"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { getCurrentLocale, setLocale as setGlobalLocale } from "@/lib/i18n";
import type { Locale } from "@/lib/i18n";

interface LocaleContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

const LocaleContext = createContext<LocaleContextValue>({
  locale: "ru-RU",
  setLocale: () => {},
});

/**
 * Reactive locale provider.
 *
 * Wraps the app so that every component that calls t() re-renders
 * when the user switches language — no manual refresh needed.
 *
 * The actual translation lookup still goes through the module-level
 * setLocale()/currentLocale (which t() reads). This provider only
 * triggers React re-renders by holding locale in state.
 */
export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("ru-RU");

  // Initialise from saved locale
  useEffect(() => {
    setLocaleState(getCurrentLocale());
  }, []);

  // Listen for locale-changed events dispatched by LocaleSwitcher
  useEffect(() => {
    const handler = () => {
      setLocaleState(getCurrentLocale());
    };
    window.addEventListener("locale-changed", handler);
    return () => window.removeEventListener("locale-changed", handler);
  }, []);

  const setLocale = useCallback((newLocale: Locale) => {
    // Update module-level variable + localStorage
    setGlobalLocale(newLocale);
    // Trigger React re-render
    setLocaleState(newLocale);
    // Notify other listeners (e.g. LocaleSwitcher itself)
    window.dispatchEvent(new CustomEvent("locale-changed"));
  }, []);

  return (
    <LocaleContext.Provider value={{ locale, setLocale }}>
      {children}
    </LocaleContext.Provider>
  );
}

/**
 * Hook to read current locale.
 *
 * Components that do NOT call t() but still need to react to locale
 * changes can call this hook. Components that DO call t() will also
 * re-render correctly as long as this provider is mounted, because
 * the context state change propagates through React's tree.
 */
export function useLocale(): LocaleContextValue {
  return useContext(LocaleContext);
}
