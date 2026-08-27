import React from 'react';
import { Card } from './Card';
import { cn } from '../../utils/cn';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
    label: string;
    isPositive?: boolean; // Sometimes up is bad (e.g., exposure)
  };
  icon?: React.ReactNode;
  status?: 'default' | 'risk' | 'warning' | 'safe' | 'info';
  className?: string;
}

export function MetricCard({ title, value, trend, icon, status = 'default', className }: MetricCardProps) {
  const statusColors = {
    default: 'text-slate-900',
    risk: 'text-risk',
    warning: 'text-warning',
    safe: 'text-safe',
    info: 'text-info',
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.direction === 'up') return <TrendingUp className="h-4 w-4" />;
    if (trend.direction === 'down') return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const getTrendColor = () => {
    if (!trend) return '';
    // If explicitly defined, use it
    if (trend.isPositive !== undefined) {
      return trend.isPositive ? 'text-safe-dark' : 'text-risk-dark';
    }
    // Default assumption: up is good, down is bad
    if (trend.direction === 'up') return 'text-safe-dark';
    if (trend.direction === 'down') return 'text-risk-dark';
    return 'text-slate-500';
  };

  return (
    <Card className={cn("relative overflow-hidden", className)}>
      {/* Optional top border indicator for status */}
      {status !== 'default' && (
        <div className={cn("absolute top-0 left-0 w-full h-1", {
          'bg-risk': status === 'risk',
          'bg-warning': status === 'warning',
          'bg-safe': status === 'safe',
          'bg-info': status === 'info',
        })} />
      )}
      
      <div className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-500 truncate">{title}</p>
          {icon && (
            <div className="p-2 bg-slate-50 rounded-md text-slate-400">
              {icon}
            </div>
          )}
        </div>
        
        <div className="mt-2 flex items-baseline gap-x-2">
          <span className={cn("text-3xl font-semibold tracking-tight", statusColors[status])}>
            {value}
          </span>
        </div>
        
        {trend && (
          <div className="mt-4 flex items-center text-sm">
            <span className={cn("flex items-center font-medium", getTrendColor())}>
              {getTrendIcon()}
              <span className="ml-1">{trend.value}</span>
            </span>
            <span className="ml-2 text-slate-500 truncate">{trend.label}</span>
          </div>
        )}
      </div>
    </Card>
  );
}
