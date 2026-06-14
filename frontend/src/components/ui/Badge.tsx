"use client";

import type { ReactNode } from "react";
import clsx from "clsx";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info" | "primary" | "outline" | "secondary";
type BadgeSize = "sm" | "md";

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-muted text-muted-foreground border-default",
  primary: "bg-primary-50 text-primary-700 border-primary-200 dark:bg-primary-900/30 dark:text-primary-200 dark:border-primary-700",
  success: "bg-success-50 text-success-700 border-success-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700",
  warning: "bg-warning-50 text-warning-700 border-warning-200 dark:bg-amber-900/30 dark:text-amber-200 dark:border-amber-700",
  danger: "bg-danger-50 text-danger-700 border-danger-200 dark:bg-red-900/30 dark:text-red-200 dark:border-red-700",
  info: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700",
  outline: "bg-transparent text-primary border-primary-300",
  secondary: "bg-secondary text-secondary-foreground border-default",
};

const sizeStyles: Record<BadgeSize, string> = {
  sm: "px-2 py-0.5 text-caption",
  md: "px-2.5 py-1 text-label",
};

export default function Badge({
  children,
  variant = "default",
  size = "md",
  className,
}: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center font-medium rounded-full border",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
    >
      {children}
    </span>
  );
}
