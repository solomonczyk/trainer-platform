"use client";

import type { HTMLAttributes, ReactNode } from "react";
import clsx from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
  variant?: "default" | "elevated" | "immersive" | "outlined";
}

const paddingStyles = {
  none: "",
  sm: "p-3",
  md: "p-5",
  lg: "p-7",
};

const variantStyles = {
  default: "border border-default bg-surface shadow-card",
  elevated: "border border-default bg-elevated shadow-elevated",
  immersive: "border-0 bg-immersive text-text-inverse shadow-immersive",
  outlined: "border-2 border-selected bg-surface shadow-sm",
};

export default function Card({
  children,
  hover = false,
  padding = "md",
  variant = "default",
  className,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        "rounded transition-all duration-200",
        hover && "hover:-translate-y-0.5 hover:shadow-elevated cursor-pointer",
        variantStyles[variant],
        paddingStyles[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={clsx("mb-3 flex items-center gap-3", className)}>
      {children}
    </div>
  );
}

export function CardTitle({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h3 className={clsx("text-h4 font-semibold text-foreground", className)}>
      {children}
    </h3>
  );
}

export function CardDescription({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <p className={clsx("text-body-sm text-muted-foreground", className)}>{children}</p>
  );
}

export function CardContent({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={clsx("text-body-sm text-secondary-foreground leading-relaxed", className)}>{children}</div>;
}

export function CardFooter({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={clsx("mt-4 flex items-center gap-2 pt-3 border-t border-default", className)}>
      {children}
    </div>
  );
}
