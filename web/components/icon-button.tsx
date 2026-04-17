"use client";

import { ComponentPropsWithoutRef, ReactNode } from "react";

type IconButtonProps = {
  ariaLabel: string;
  icon: ReactNode;
  label?: string;
  title?: string;
  active?: boolean;
  variant?: "toolbar" | "panel";
} & ComponentPropsWithoutRef<"button">;

export function IconButton({
  ariaLabel,
  icon,
  label,
  title,
  active = false,
  className = "",
  variant = "toolbar",
  type = "button",
  ...props
}: IconButtonProps) {
  return (
    <button
      type={type}
      aria-label={ariaLabel}
      title={title || ariaLabel}
      className={`icon-button icon-button--${variant} ${label ? "icon-button--with-label" : "icon-button--icon-only"} ${
        active ? "icon-button--active" : ""
      } ${className}`.trim()}
      {...props}
    >
      <span className="icon-button__glyph" aria-hidden="true">
        {icon}
      </span>
      {label ? <span className="icon-button__label">{label}</span> : null}
    </button>
  );
}

type IconButtonLabelProps = {
  ariaLabel: string;
  icon: ReactNode;
  label: string;
  title?: string;
  disabled?: boolean;
};

export function IconButtonLabel({ ariaLabel, icon, label, title, disabled = false }: IconButtonLabelProps) {
  return (
    <span
      role="button"
      aria-label={ariaLabel}
      title={title || ariaLabel}
      aria-disabled={disabled}
      className={`icon-button icon-button--toolbar icon-button--with-label icon-button-label ${disabled ? "icon-button-label--disabled" : ""}`}
    >
      <span className="icon-button__glyph" aria-hidden="true">
        {icon}
      </span>
      <span className="icon-button__label">{label}</span>
    </span>
  );
}

type SvgIconProps = {
  children: ReactNode;
};

function SvgIcon({ children }: SvgIconProps) {
  return (
    <svg viewBox="0 0 24 24" className="ui-icon" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  );
}

export function OpenIcon() {
  return (
    <SvgIcon>
      <path d="M4 19a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-5-5H6a2 2 0 0 0-2 2z" />
      <path d="M14 4v6h6" />
    </SvgIcon>
  );
}

export function DownloadIcon() {
  return (
    <SvgIcon>
      <path d="M12 3v12" />
      <path d="m7 10 5 5 5-5" />
      <path d="M5 21h14" />
    </SvgIcon>
  );
}

export function ZoomInIcon() {
  return (
    <SvgIcon>
      <circle cx="11" cy="11" r="6" />
      <path d="M21 21l-4.35-4.35" />
      <path d="M11 8v6" />
      <path d="M8 11h6" />
    </SvgIcon>
  );
}

export function ZoomOutIcon() {
  return (
    <SvgIcon>
      <circle cx="11" cy="11" r="6" />
      <path d="M21 21l-4.35-4.35" />
      <path d="M8 11h6" />
    </SvgIcon>
  );
}

export function ZoomResetIcon() {
  return (
    <SvgIcon>
      <circle cx="11" cy="11" r="6" />
      <path d="M21 21l-4.35-4.35" />
      <path d="M8.5 11a2.5 2.5 0 1 0 3.2-2.4" />
      <path d="M11.7 6.8V9.5h-2.7" />
    </SvgIcon>
  );
}

export function ChevronLeftIcon() {
  return (
    <SvgIcon>
      <path d="m15 18-6-6 6-6" />
    </SvgIcon>
  );
}

export function ChevronRightIcon() {
  return (
    <SvgIcon>
      <path d="m9 18 6-6-6-6" />
    </SvgIcon>
  );
}

export function SearchIcon() {
  return (
    <SvgIcon>
      <circle cx="11" cy="11" r="6" />
      <path d="M21 21l-4.35-4.35" />
    </SvgIcon>
  );
}

export function ClearIcon() {
  return (
    <SvgIcon>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </SvgIcon>
  );
}

export function RotateCwIcon() {
  return (
    <SvgIcon>
      <path d="M20 11a8 8 0 1 1-2.34-5.66" />
      <path d="M20 4v7h-7" />
    </SvgIcon>
  );
}

export function RotateCcwIcon() {
  return (
    <SvgIcon>
      <path d="M4 11a8 8 0 1 0 2.34-5.66" />
      <path d="M4 4v7h7" />
    </SvgIcon>
  );
}

export function TrashIcon() {
  return (
    <SvgIcon>
      <path d="M3 6h18" />
      <path d="M8 6V4h8v2" />
      <path d="m6 6 1 14h10l1-14" />
      <path d="M10 10v6" />
      <path d="M14 10v6" />
    </SvgIcon>
  );
}

export function ExtractIcon() {
  return (
    <SvgIcon>
      <path d="M12 3v12" />
      <path d="m7 10 5 5 5-5" />
      <path d="M5 21h14" />
      <path d="M4 4h16" />
    </SvgIcon>
  );
}

export function SplitIcon() {
  return (
    <SvgIcon>
      <path d="M6 4v16" />
      <path d="M18 4v16" />
      <path d="M10 8h4" />
      <path d="M10 12h4" />
      <path d="M10 16h4" />
    </SvgIcon>
  );
}

export function HighlightIcon() {
  return (
    <SvgIcon>
      <path d="m6 15 6-6 6 6" />
      <path d="M7 16h10" />
      <path d="M5 20h14" />
    </SvgIcon>
  );
}

export function UnderlineIcon() {
  return (
    <SvgIcon>
      <path d="M8 5v6a4 4 0 0 0 8 0V5" />
      <path d="M5 20h14" />
    </SvgIcon>
  );
}
