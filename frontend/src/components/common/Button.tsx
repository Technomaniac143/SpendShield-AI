import React from 'react';
import { cn } from '../../utils/cn';
import { LucideIcon } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', icon: Icon, iconPosition = 'left', isLoading, children, disabled, ...props }, ref) => {
    const variants = {
      primary: 'bg-slate-900 text-white hover:bg-slate-800 focus-visible:outline-slate-900 shadow-sm',
      secondary: 'bg-info text-white hover:bg-info-dark focus-visible:outline-info shadow-sm',
      danger: 'bg-risk text-white hover:bg-risk-dark focus-visible:outline-risk shadow-sm',
      outline: 'bg-white text-slate-700 ring-1 ring-inset ring-slate-300 hover:bg-slate-50',
      ghost: 'text-slate-700 hover:bg-slate-100',
    };

    const sizes = {
      sm: 'px-2.5 py-1.5 text-xs',
      md: 'px-3 py-2 text-sm',
      lg: 'px-4 py-2.5 text-sm',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center font-semibold rounded-md transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {!isLoading && Icon && iconPosition === 'left' && (
          <Icon className={cn("mr-2 h-4 w-4", size === 'sm' ? 'h-3.5 w-3.5' : '')} aria-hidden="true" />
        )}
        {children}
        {!isLoading && Icon && iconPosition === 'right' && (
          <Icon className={cn("ml-2 h-4 w-4", size === 'sm' ? 'h-3.5 w-3.5' : '')} aria-hidden="true" />
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
