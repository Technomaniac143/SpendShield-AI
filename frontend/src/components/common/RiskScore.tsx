import React from 'react';
import { cn } from '../../utils/cn';

interface RiskScoreProps {
  score: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function RiskScore({ score, max = 100, size = 'md', className }: RiskScoreProps) {
  // Determine risk level based on standard thresholds
  const getRiskLevel = (val: number) => {
    if (val >= 80) return 'critical';
    if (val >= 50) return 'warning';
    return 'safe';
  };

  const level = getRiskLevel(score);

  const colors = {
    critical: 'text-risk bg-risk-light ring-risk/20',
    warning: 'text-warning bg-warning-light ring-warning/20',
    safe: 'text-safe bg-safe-light ring-safe/20',
  };

  const sizes = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-xl',
  };

  return (
    <div
      className={cn(
        "inline-flex items-center justify-center font-bold rounded-full ring-1 ring-inset",
        colors[level],
        sizes[size],
        className
      )}
      title={`Risk Score: ${score}/${max}`}
    >
      {score}
    </div>
  );
}
