"use client";

import "./globals.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { loadSavedLocale } from "@/lib/i18n";
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
          <AuthProvider>
            <Favicon />
            <Header />
            <main className="flex-1">{mounted ? children : <div className="p-8 text-center text-gray-400">Loading...</div>}</main>
            <Footer />
          </AuthProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
