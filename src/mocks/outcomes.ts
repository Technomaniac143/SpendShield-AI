export const outcomesData = {
  metrics: {
    potentialSavings: 8400000,
    actionableSavings: 4200000,
    realizedSavings: 2800000,
    cashReleased: 1500000,
    leakagePrevented: 3100000
  },
  learningLoop: [
    {
      id: 'LL-001',
      recommendation: 'Switch to Supplier B',
      decision: 'ACCEPTED',
      predictedTrueCost: 1060,
      actualTrueCost: 1048,
      predictionError: 1.13, // percentage
      realizedSavings: 145000
    },
    {
      id: 'LL-002',
      recommendation: 'Reduce inventory of Product X',
      decision: 'ACCEPTED',
      predictedTrueCost: 450,
      actualTrueCost: 470,
      predictionError: -4.44, // percentage
      realizedSavings: 210000
    }
  ]
};
