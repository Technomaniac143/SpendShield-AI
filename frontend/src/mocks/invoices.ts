export const invoices = [
  {
    id: 'INV-10482',
    supplierId: 'SUP-001',
    supplierName: 'ABC Industries',
    date: '2023-10-15',
    amount: 500000,
    poNumber: 'PO-1001',
    status: 'BLOCKED',
    lineItems: [
      { product: 'Widget X', quantity: 1000, unitPrice: 500, tax: 0, discount: 0, total: 500000 }
    ],
    duplicateProbability: 0.96,
    relatedInvoice: 'INV-10091'
  }
];
