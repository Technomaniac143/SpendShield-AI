import { Investigation, InvestigationStep, Finding, Evidence } from '../types';

export const demoInvestigationSteps: InvestigationStep[] = [
  { id: 's1', title: 'Supplier profile loaded', status: 'COMPLETED', durationMs: 42, details: 'Fetched ABC Industries profile and historical metrics.' },
  { id: 's2', title: 'Transaction history analyzed', status: 'COMPLETED', durationMs: 1250, details: 'Analyzed 143 transactions over the past 12 months.' },
  { id: 's3', title: 'Duplicate analysis', status: 'COMPLETED', durationMs: 3400, details: 'Found 3 potential duplicates matching amount and date.' },
  { id: 's4', title: 'Price benchmarking', status: 'COMPLETED', durationMs: 890, details: 'Compared unit prices against contract and market rates.' },
  { id: 's5', title: 'Delivery performance check', status: 'COMPLETED', durationMs: 520, details: 'Calculated 81% on-time delivery rate (12% delay rate).' },
  { id: 's6', title: 'Relationship graph traversal', status: 'COMPLETED', durationMs: 4100, details: 'Traversed 4 degrees of separation. Found 2 risk signals.' },
  { id: 's7', title: 'True cost calculation', status: 'COMPLETED', durationMs: 150, details: 'Computed true cost at ₹1,105.' },
  { id: 's8', title: 'Financial exposure calculation', status: 'COMPLETED', durationMs: 80, details: 'Total exposure aggregated to ₹8.4L.' },
  { id: 's9', title: 'Generating recommendation', status: 'COMPLETED', durationMs: 2200, details: 'Synthesized findings into actionable recommendations.' }
];

export const demoFindings: Finding[] = [
  {
    id: 'f1',
    type: 'QUANTITY',
    title: 'GRN Quantity Mismatch',
    description: 'Invoice INV-10482 billed for 1,000 units, but GRN shows only 920 units received.',
    exposure: 40000,
    confidence: 0.98,
    evidenceId: 'EV-1021'
  },
  {
    id: 'f2',
    type: 'PRICE',
    title: 'Price Anomaly Detected',
    description: 'Current price of ₹575 is 15% above the contracted rate of ₹500.',
    exposure: 75000,
    confidence: 0.96,
    evidenceId: 'EV-1022'
  },
  {
    id: 'f3',
    type: 'RELATIONSHIP',
    title: 'Hidden Relationship Risk',
    description: 'Supplier shares a registered address and bank signal with Supplier B, which was recently flagged for quality issues.',
    exposure: 0,
    confidence: 0.91,
    evidenceId: 'EV-1023'
  }
];

export const investigations: Investigation[] = [
  {
    id: 'INVEST-001',
    targetId: 'SUP-001',
    targetName: 'ABC Industries',
    targetType: 'SUPPLIER',
    status: 'COMPLETED',
    riskScore: 87,
    confidence: 0.93,
    financialExposure: 840000,
    potentialSavings: 310000,
    primaryFinding: 'Multiple procurement anomalies indicate elevated financial and supplier risk.',
    steps: demoInvestigationSteps,
    findings: demoFindings
  }
];
