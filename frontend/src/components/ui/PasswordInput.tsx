"use client";

import { useState, type InputHTMLAttributes } from "react";
import { Eye, EyeOff } from "lucide-react";
import clsx from "clsx";
import { t } from "@/lib/i18n";

interface PasswordInputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  error?: string;
  showToggle?: boolean;
}

export default function PasswordInput({
  label,
  error,
  className,
  showToggle = true,
  id,
  ...inputProps
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  const inputId = id || inputProps.name || "password-field";

  const toggleLabel = visible
    ? t("auth.hidePassword") || "Hide password"
    : t("auth.showPassword") || "Show password";

  return (
    <div className={clsx("w-full", className)}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}

      <div className="relative">
        <input
          id={inputId}
          type={visible ? "text" : "password"}
          className={clsx(
            "block w-full rounded-lg border px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 transition-colors",
            "focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500",
            error
              ? "border-red-400 focus:border-red-500 focus:ring-red-500"
              : "border-gray-300",
            showToggle && "pr-10"
          )}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...inputProps}
        />

        {showToggle && (
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            className={clsx(
              "absolute inset-y-0 right-0 flex items-center pr-3",
              "text-gray-400 hover:text-gray-600 transition-colors",
              "focus:outline-none focus:text-primary-600"
            )}
            aria-label={toggleLabel}
            tabIndex={0}
          >
            {visible ? (
              <EyeOff className="h-4 w-4" aria-hidden="true" />
            ) : (
              <Eye className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
        )}
      </div>

      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-xs text-red-500" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
