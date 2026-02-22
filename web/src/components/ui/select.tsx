// BOUND: TARLAANALIZ_SSOT_v1_0_0.txt – canonical rules are referenced, not duplicated.
'use client';

import { forwardRef } from 'react';

export interface SelectOption {
  readonly value: string;
  readonly label: string;
  readonly disabled?: boolean;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options: readonly SelectOption[];
  placeholder?: string;
  hasError?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className = '', options, placeholder, hasError = false, ...props },
  ref
) {
  return (
    <select
      ref={ref}
      className={`h-10 w-full rounded-md border px-3 text-sm shadow-sm outline-none transition focus-visible:ring-2 ${
        hasError
          ? 'border-rose-500 focus-visible:ring-rose-400'
          : 'border-slate-300 focus-visible:ring-emerald-500'
      } disabled:cursor-not-allowed disabled:opacity-50 ${className}`.trim()}
      {...props}
    >
      {placeholder ? (
        <option value="" disabled>
          {placeholder}
        </option>
      ) : null}
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} disabled={opt.disabled}>
          {opt.label}
        </option>
      ))}
    </select>
  );
});
