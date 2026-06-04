"use client";

import "./globals.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { loadSavedLocale } from "@/lib/i18n";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    loadSavedLocale();
    setMounted(true);
  }, []);

  return (
    <html lang="ru">
      <body className="min-h-screen flex flex-col bg-gray-50">
        <QueryClientProvider client={queryClient}>
          <Header />
          <main className="flex-1">{mounted ? children : <div className="p-8 text-center text-gray-400">Loading...</div>}</main>
          <Footer />
        </QueryClientProvider>
      </body>
    </html>
  );
}
