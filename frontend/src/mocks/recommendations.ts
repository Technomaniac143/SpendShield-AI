import { Recommendation } from '../types';

export const recommendations: Recommendation[] = [
  {
    id: 'REC-001',
    priority: 'CRITICAL',
    issue: 'GRN quantity mismatch on Invoice INV-10482',
    entity: 'ABC Industries',
    exposure: 40000,
    recommendedAction: 'HOLD PAYMENT and investigate supplier',
    confidence: 0.98,
    status: 'NEW'
  },
  {
    id: 'REC-002',
    priority: 'HIGH',
    issue: 'Excess inventory of Product X',
    entity: 'Warehouse A',
    exposure: 600000,
    recommendedAction: 'REDUCE NEXT ORDER by 50%',
    confidence: 0.89,
    status: 'PENDING REVIEW'
  },
  {
    id: 'REC-003',
    priority: 'MEDIUM',
    issue: 'Price variance detected',
    entity: 'Supplier C',
    exposure: 150000,
    recommendedAction: 'RENEGOTIATE contract terms',
    confidence: 0.85,
    status: 'ACCEPTED'
  }
];
