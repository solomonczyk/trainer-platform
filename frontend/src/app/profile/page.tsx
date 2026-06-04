"use client";

import { useState, useEffect, type FormEvent } from "react";
import { getCurrentUser, updateProfile, type UserResponse, ApiClientError } from "@/lib/api/client";
import { t, setLocale, getCurrentLocale, localeOptions, type Locale } from "@/lib/i18n";
import Button from "@/components/ui/Button";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { AlertCircle, CheckCircle, User, Mail, Globe } from "lucide-react";

export default function ProfilePage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [selectedLocale, setSelectedLocale] = useState<Locale>("ru-RU");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    getCurrentUser()
      .then((u) => {
        setUser(u);
        setDisplayName(u.display_name || "");
        setEmail(u.email);
        const savedLocale = getCurrentLocale();
        setSelectedLocale(savedLocale);
      })
      .catch(() => {
        setError(t("common.error"));
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsSaving(true);

    try {
      const updated = await updateProfile({
        display_name: displayName.trim() || undefined,
        preferred_locale: selectedLocale,
      });
      setUser(updated);

      // Update i18n locale immediately
      setLocale(selectedLocale);
      window.dispatchEvent(new CustomEvent("locale-changed"));

      setSuccess(t("profile.saved"));
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message || t("common.error"));
      } else {
        setError(t("common.error"));
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <p className="text-lg font-medium text-gray-900">{t("common.unauthorized")}</p>
        <Button onClick={() => (window.location.href = "/login")}>
          {t("nav.login")}
        </Button>
      </div>
    );
  }

  const locales = localeOptions();

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-900">{t("profile.title")}</h1>

      <Card padding="lg">
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700">
            <CheckCircle className="h-4 w-4" />
            {success}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Display Name */}
          <div>
            <label
              htmlFor="displayName"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-400" />
                {t("profile.name")}
              </div>
            </label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder={t("auth.displayName")}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {/* Email (read-only) */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-400" />
                {t("profile.email")}
              </div>
            </label>
            <input
              id="email"
              type="email"
              value={email}
              readOnly
              className="block w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500 cursor-not-allowed"
            />
            <p className="mt-1 text-xs text-gray-400">Email cannot be changed</p>
          </div>

          {/* Locale Switcher */}
          <div>
            <label
              htmlFor="locale"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-gray-400" />
                {t("profile.preferredLocale")}
              </div>
            </label>
            <select
              id="locale"
              value={selectedLocale}
              onChange={(e) => setSelectedLocale(e.target.value as Locale)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {locales.map((loc) => (
                <option key={loc.value} value={loc.value}>
                  {loc.label}
                </option>
              ))}
            </select>
          </div>

          <div className="pt-2">
            <Button type="submit" variant="primary" size="lg" isLoading={isSaving}>
              {t("profile.save")}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
