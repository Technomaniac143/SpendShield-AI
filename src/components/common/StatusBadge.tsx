import React from 'react';
import { cn } from '../../utils/cn';
import { CheckCircle2, AlertTriangle, XCircle, Clock, Info } from 'lucide-react';
import { Badge } from './Badge';

export type StatusType = 
  | 'VERIFIED' 
  | 'COMPLETED' 
  | 'WAITING' 
  | 'RUNNING' 
  | 'FAILED' 
  | 'HOLD' 
  | 'WARNING' 
  | 'INTEGRITY_FAILURE';

interface StatusBadgeProps {
  status: StatusType | string;
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const normalizedStatus = status.toUpperCase();
  
  let variant: 'safe' | 'risk' | 'warning' | 'info' | 'default' = 'default';
  let Icon = Info;

  switch (normalizedStatus) {
    case 'VERIFIED':
    case 'COMPLETED':
    case 'PASS':
    case 'ACCEPTED':
    case 'EXECUTED':
      variant = 'safe';
      Icon = CheckCircle2;
      break;
    case 'FAILED':
    case 'FAIL':
    case 'BLOCKED':
    case 'HOLD':
    case 'INTEGRITY_FAILURE':
    case 'INTEGRITY FAILURE':
    case 'REJECTED':
      variant = 'risk';
      Icon = XCircle;
      break;
    case 'WARNING':
    case 'PENDING REVIEW':
    case 'OPEN':
      variant = 'warning';
      Icon = AlertTriangle;
      break;
    case 'WAITING':
    case 'RUNNING':
    case 'PENDING':
    case 'NEW':
      variant = 'info';
      Icon = Clock;
      break;
    default:
      variant = 'default';
      Icon = Info;
  }

  return (
    <Badge variant={variant} className={cn("px-2.5 py-1", className)}>
      {showIcon && <Icon className="mr-1.5 h-3.5 w-3.5" />}
      {status}
    </Badge>
  );
}
