import { KPI, PriorityAction, ChartDataPoint } from '../types';

export const dashboardKPIs: KPI[] = [
  {
    id: 'kpi-1',
    label: 'Total Spend',
    value: 12000000,
    trend: 4.2,
    trendLabel: 'vs previous period',
    status: 'default'
  },
  {
    id: 'kpi-2',
    label: 'At-Risk Spend',
    value: 4260000,
    trend: 8.4,
    trendLabel: 'vs previous period',
    status: 'risk'
  },
  {
    id: 'kpi-3',
    label: 'Financial Exposure',
    value: 1450000,
    trend: -2.1,
    trendLabel: 'vs previous period',
    status: 'warning'
  },
  {
    id: 'kpi-4',
    label: 'Cash Trapped',
    value: 3140000,
    trend: 1.5,
    trendLabel: 'vs previous period',
    status: 'warning'
  },
  {
    id: 'kpi-5',
    label: 'Verified Savings',
    value: 850000,
    trend: 12.4,
    trendLabel: 'vs previous period',
    status: 'safe'
  }
];

export const priorityActions: PriorityAction[] = [
  {
    id: 'pa-1',
    severity: 'CRITICAL',
    action: 'HOLD PAYMENT',
    entity: 'INV-10482',
    entityType: 'INVOICE',
    exposure: 40000,
    reason: 'GRN quantity mismatch (PO: 1,000, GRN: 920, Invoice: 1,000)',
    confidence: 0.98,
    recommendedAction: 'Hold payment and verify physical receipt'
  },
  {
    id: 'pa-2',
    severity: 'HIGH',
    action: 'INVESTIGATE',
    entity: 'ABC Industries',
    entityType: 'SUPPLIER',
    exposure: 840000,
    reason: 'New hidden relationship detected with Supplier B',
    confidence: 0.93,
    recommendedAction: 'Trigger comprehensive supplier audit'
  },
  {
    id: 'pa-3',
    severity: 'HIGH',
    action: 'REVIEW',
    entity: 'INV-10091',
    entityType: 'INVOICE',
    exposure: 125000,
    reason: 'Price anomaly: Unit price 15% above contract',
    confidence: 0.96,
    recommendedAction: 'Dispute invoice pricing'
  }
];

export const leakageByCategory: ChartDataPoint[] = [
  { name: 'Duplicate Invoices', value: 250000 },
  { name: 'Price Anomalies', value: 480000 },
  { name: 'Quantity Mismatch', value: 120000 },
  { name: 'Contract Leakage', value: 340000 },
  { name: 'Inventory Excess', value: 260000 }
];

export const spendRiskTrend = [
  { date: 'Jan', totalSpend: 1000000, riskySpend: 150000, exposure: 50000 },
  { date: 'Feb', totalSpend: 1100000, riskySpend: 180000, exposure: 60000 },
  { date: 'Mar', totalSpend: 950000,  riskySpend: 120000, exposure: 40000 },
  { date: 'Apr', totalSpend: 1200000, riskySpend: 250000, exposure: 90000 },
  { date: 'May', totalSpend: 1150000, riskySpend: 300000, exposure: 110000 },
  { date: 'Jun', totalSpend: 1300000, riskySpend: 426000, exposure: 145000 }
];
