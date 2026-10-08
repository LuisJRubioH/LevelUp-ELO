/**
 * components/ui/Button.tsx
 * ========================
 * Botón reutilizable con variantes: primary, secondary, danger, ghost.
 */

import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: ReactNode;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-violet-600 hover:bg-violet-500 text-white shadow-[0_10px_24px_-14px_rgba(109,40,217,0.9)]",
  secondary: "border border-slate-600 bg-slate-800 hover:bg-slate-700 text-slate-100",
  danger: "bg-red-600 hover:bg-red-500 text-white",
  ghost: "border border-transparent bg-transparent hover:border-slate-700 hover:bg-slate-800 text-slate-300",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
};

export function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  children,
  className = "",
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={[
        "inline-flex min-h-10 items-center justify-center gap-2 whitespace-nowrap rounded-xl font-semibold",
        "transition-[transform,background-color,border-color,box-shadow] duration-150 cursor-pointer",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400",
        "active:translate-y-px active:scale-[0.99]",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].join(" ")}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      )}
      {children}
    </button>
  );
}
