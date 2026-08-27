export const inventoryData = {
  metrics: {
    totalValue: 31400000,
    excessValue: 1480000,
    slowMovingValue: 1220000,
    expiringValue: 440000,
    cashTrapped: 3140000
  },
  items: [
    {
      id: 'INV-ITM-01',
      product: 'Component Y',
      warehouse: 'Warehouse A',
      quantity: 15000,
      value: 1220000,
      daysIdle: 145,
      expiry: null,
      recommendedAction: 'REDUCE NEXT ORDER'
    },
    {
      id: 'INV-ITM-02',
      product: 'Material Z',
      warehouse: 'Warehouse B',
      quantity: 8500,
      value: 1480000,
      daysIdle: 42,
      expiry: '2024-12-01',
      recommendedAction: 'TRANSFER INVENTORY'
    },
    {
      id: 'INV-ITM-03',
      product: 'Chemical Q',
      warehouse: 'Warehouse A',
      quantity: 400,
      value: 440000,
      daysIdle: 85,
      expiry: '2023-11-15',
      recommendedAction: 'DISCOUNT'
    }
  ]
};
