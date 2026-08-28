import { Supplier } from '../types';

export const suppliers: Supplier[] = [
  {
    id: 'SUP-001',
    name: 'ABC Industries',
    riskScore: 87,
    confidence: 0.93,
    totalSpend: 5400000,
    trueCost: 1105,
    financialExposure: 840000,
    onTimeDelivery: 81,
    defectRate: 6.2,
    returnRate: 4.1,
    disputeRate: 8.5,
    priceVariance: 11.6,
    status: 'CRITICAL',
    metrics: {
      pricingRisk: 78,
      deliveryRisk: 65,
      qualityRisk: 72,
      relationshipRisk: 88
    }
  },
  {
    id: 'SUP-002',
    name: 'Supplier B',
    riskScore: 54,
    confidence: 0.94,
    totalSpend: 3200000,
    trueCost: 1060,
    financialExposure: 120000,
    onTimeDelivery: 94,
    defectRate: 2.1,
    returnRate: 1.5,
    disputeRate: 2.0,
    priceVariance: 1.2,
    status: 'ACTIVE',
    metrics: {
      pricingRisk: 30,
      deliveryRisk: 25,
      qualityRisk: 20,
      relationshipRisk: 40
    }
  },
  {
    id: 'SUP-003',
    name: 'Supplier C',
    riskScore: 63,
    confidence: 0.88,
    totalSpend: 2800000,
    trueCost: 1130,
    financialExposure: 210000,
    onTimeDelivery: 88,
    defectRate: 3.4,
    returnRate: 2.5,
    disputeRate: 4.2,
    priceVariance: 4.5,
    status: 'WARNING',
    metrics: {
      pricingRisk: 55,
      deliveryRisk: 45,
      qualityRisk: 40,
      relationshipRisk: 60
    }
  }
];
