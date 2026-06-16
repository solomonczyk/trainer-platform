"use client";

import "./globals.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { loadSavedLocale } from "@/lib/i18n";
import { LocaleProvider, useLocale } from "@/lib/i18n/LocaleProvider";
import { AuthProvider } from "@/lib/auth/AuthContext";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

function Favicon() {
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "icon";
    link.href = "/favicon.svg";
    link.type = "image/svg+xml";
    document.head.appendChild(link);
  }, []);
  return null;
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
});

/**
 * Inner wrapper that re-creates page content when locale changes.
 *
 * Next.js App Router passes `children` as a static ReactNode — it
 * does NOT re-execute the page component when the layout re-renders.
 * By keying the children wrapper to the current locale, React is
 * forced to unmount the old page content and remount it, which
 * re-executes all t() calls with the fresh locale.
 */
function LocaleAwareContent({ children }: { children: React.ReactNode }) {
  const { locale } = useLocale();
  return <div key={locale}>{children}</div>;
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    loadSavedLocale();
    setMounted(true);
  }, []);

  return (
    <html lang="ru">
      <body className="min-h-screen flex flex-col bg-app">
        <QueryClientProvider client={queryClient}>
          <LocaleProvider>
          <AuthProvider>
            <Favicon />
            <Header />
            <main className="flex-1">
              {mounted ? <LocaleAwareContent>{children}</LocaleAwareContent> : <div className="p-8 text-center text-gray-400">Loading...</div>}
            </main>
            <Footer />
          </AuthProvider>
          </LocaleProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
