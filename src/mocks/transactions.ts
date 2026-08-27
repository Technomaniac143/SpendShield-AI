export const transactions = [
  {
    id: 'TXN-1001',
    poNumber: 'PO-1001',
    poQuantity: 1000,
    poUnitPrice: 500,
    grnNumber: 'GRN-1001',
    grnQuantity: 920,
    invoiceNumber: 'INV-10482',
    invoiceQuantity: 1000,
    invoiceUnitPrice: 500,
    supplierId: 'SUP-001',
    supplierName: 'ABC Industries',
    status: 'BLOCKED',
    exposure: 40000, // (1000 - 920) * 500
    blockchainStatus: 'VERIFIED',
    date: '2023-10-15',
  }
];
