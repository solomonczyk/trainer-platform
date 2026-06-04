"use client";

import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";
import clsx from "clsx";

type InputVariants = "default" | "error";

interface BaseProps {
  label?: string;
  helperText?: string;
  error?: string;
  className?: string;
  inputClassName?: string;
}

interface InputAsInputProps
  extends BaseProps,
    Omit<InputHTMLAttributes<HTMLInputElement>, "size"> {
  as?: "input";
}

interface InputAsTextareaProps
  extends BaseProps,
    Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "size"> {
  as: "textarea";
}

type InputProps = InputAsInputProps | InputAsTextareaProps;

const baseInputStyles =
  "block w-full rounded-lg border bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500";

const variantStyles: Record<InputVariants, string> = {
  default:
    "border-gray-300 focus:border-primary-500 focus:ring-primary-500/30",
  error:
    "border-red-400 focus:border-red-500 focus:ring-red-500/30",
};

function resolveInputVariant(error?: string): InputVariants {
  return error ? "error" : "default";
}

const Input = forwardRef<HTMLInputElement | HTMLTextAreaElement, InputProps>(
  (props, ref) => {
    const {
      label,
      helperText,
      error,
      className,
      inputClassName,
      ...rest
    } = props;

    const variant = resolveInputVariant(error);
    const id = (rest as Record<string, unknown>).id;

    return (
      <div className={clsx("w-full", className)}>
        {label && (
          <label
            htmlFor={id as string | undefined}
            className="block mb-1.5 text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}

        {props.as === "textarea" ? (
          <textarea
            ref={ref as React.Ref<HTMLTextAreaElement>}
            id={id as string | undefined}
            className={clsx(
              baseInputStyles,
              variantStyles[variant],
              "min-h-[80px] resize-y",
              inputClassName
            )}
            {...(rest as TextareaHTMLAttributes<HTMLTextAreaElement>)}
          />
        ) : (
          <input
            ref={ref as React.Ref<HTMLInputElement>}
            id={id as string | undefined}
            className={clsx(
              baseInputStyles,
              variantStyles[variant],
              inputClassName
            )}
            {...(rest as InputHTMLAttributes<HTMLInputElement>)}
          />
        )}

        {error && (
          <p className="mt-1.5 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}

        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
