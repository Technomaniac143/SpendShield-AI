import React from 'react';
import { cn } from '../../utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'risk' | 'warning' | 'safe' | 'info' | 'outline';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-slate-100 text-slate-700',
    risk: 'bg-risk-light text-risk-dark',
    warning: 'bg-warning-light text-warning-dark',
    safe: 'bg-safe-light text-safe-dark',
    info: 'bg-info-light text-info-dark',
    outline: 'border border-slate-200 text-slate-700',
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-slate-500/10",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
