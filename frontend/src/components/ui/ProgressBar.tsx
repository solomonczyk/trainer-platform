"use client";

import clsx from "clsx";

interface ProgressBarProps {
  value: number;
  max?: number;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
  labelClassName?: string;
}

const sizeStyles = {
  sm: "h-1.5",
  md: "h-2.5",
  lg: "h-4",
};

function getColorClass(value: number, max: number): string {
  const pct = max > 0 ? (value / max) * 100 : 0;
  if (pct < 33) return "bg-red-500";
  if (pct < 66) return "bg-amber-500";
  return "bg-green-500";
}

export default function ProgressBar({
  value,
  max = 100,
  showLabel = false,
  size = "md",
  className,
  labelClassName,
}: ProgressBarProps) {
  const clampedValue = Math.max(0, Math.min(value, max));
  const percentage = max > 0 ? Math.round((clampedValue / max) * 100) : 0;
  const colorClass = getColorClass(clampedValue, max);

  return (
    <div className={clsx("w-full", className)}>
      {showLabel && (
        <div
          className={clsx(
            "flex items-center justify-between mb-1",
            labelClassName
          )}
        >
          <span className="text-sm font-medium text-gray-700">
            {clampedValue}/{max}
          </span>
          <span className="text-sm font-medium text-gray-700">
            {percentage}%
          </span>
        </div>
      )}

      <div
        className={clsx(
          "w-full bg-gray-200 rounded-full overflow-hidden",
          sizeStyles[size]
        )}
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={`Progress: ${percentage}%`}
      >
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-300 ease-in-out",
            colorClass
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
