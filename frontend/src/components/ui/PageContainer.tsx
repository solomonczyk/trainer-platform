"use client";

import type { ReactNode } from "react";
import clsx from "clsx";

interface PageContainerProps {
  children: ReactNode;
  width?: "page" | "narrow" | "wide";
  padding?: "default" | "compact";
  className?: string;
}

const widthStyles = {
  page: "max-w-page",
  narrow: "max-w-page-narrow",
  wide: "max-w-page-wide",
};

const paddingStyles = {
  default: "px-4 py-12 sm:px-6 lg:px-8",
  compact: "px-4 py-8 sm:px-6 lg:px-8",
};

export default function PageContainer({
  children,
  width = "page",
  padding = "default",
  className,
}: PageContainerProps) {
  return (
    <div
      className={clsx(
        "mx-auto",
        widthStyles[width],
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}

export function SectionHeader({
  title,
  description,
  className,
}: {
  title: string;
  description?: string;
  className?: string;
}) {
  return (
    <div className={clsx("mb-10", className)}>
      <h1 className="text-h1 text-foreground tracking-tight">{title}</h1>
      {description && (
        <p className="mt-3 text-body-lg text-text-secondary leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
}
