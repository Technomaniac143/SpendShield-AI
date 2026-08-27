export interface Supplier {
  id: string;
  name: string;
  riskScore: number;
  confidence: number;
  totalSpend: number;
  trueCost: number;
  financialExposure: number;
  onTimeDelivery: number; // percentage
  defectRate: number; // percentage
  returnRate: number;
  disputeRate: number;
  priceVariance: number;
  status: 'ACTIVE' | 'WARNING' | 'CRITICAL';
  metrics: {
    pricingRisk: number;
    deliveryRisk: number;
    qualityRisk: number;
    relationshipRisk: number;
  };
}

export interface KPI {
  id: string;
  label: string;
  value: number;
  trend: number;
  trendLabel: string;
  status?: 'default' | 'risk' | 'warning' | 'safe';
}

export interface PriorityAction {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  action: string;
  entity: string;
  entityType: 'INVOICE' | 'SUPPLIER' | 'PO';
  exposure: number;
  reason: string;
  confidence: number;
  recommendedAction: string;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

export interface Investigation {
  id: string;
  targetId: string;
  targetName: string;
  targetType: 'SUPPLIER' | 'TRANSACTION' | 'INVOICE';
  status: 'COMPLETED' | 'RUNNING' | 'WAITING' | 'FAILED';
  riskScore: number;
  confidence: number;
  financialExposure: number;
  potentialSavings: number;
  primaryFinding: string;
  steps: InvestigationStep[];
  findings: Finding[];
}

export interface InvestigationStep {
  id: string;
  title: string;
  status: 'COMPLETED' | 'RUNNING' | 'WAITING' | 'FAILED';
  durationMs: number;
  details: string;
}

export interface Finding {
  id: string;
  type: 'DUPLICATE' | 'PRICE' | 'QUANTITY' | 'SUPPLIER' | 'QUALITY' | 'DELIVERY' | 'RELATIONSHIP' | 'INVENTORY' | 'PROVENANCE';
  title: string;
  description: string;
  exposure: number;
  confidence: number;
  evidenceId: string;
}

export interface Evidence {
  id: string;
  source: string;
  recordId: string;
  finding: string;
  calculation: string;
  confidence: number;
}

export interface Recommendation {
  id: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  issue: string;
  entity: string;
  exposure: number;
  recommendedAction: string;
  confidence: number;
  status: 'NEW' | 'PENDING REVIEW' | 'ACCEPTED' | 'REJECTED' | 'EXECUTED' | 'VERIFIED';
}
