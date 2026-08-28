export const graphData = {
  nodes: [
    { id: 'SUP-001', type: 'supplier', data: { label: 'ABC Industries', risk: 87, type: 'Supplier' }, position: { x: 250, y: 100 } },
    { id: 'INV-001', type: 'invoice', data: { label: 'Invoice INV-001', risk: 40, type: 'Invoice' }, position: { x: 100, y: 200 } },
    { id: 'PO-1001', type: 'po', data: { label: 'PO PO-1001', risk: 10, type: 'Purchase Order' }, position: { x: 100, y: 300 } },
    { id: 'SUP-002', type: 'supplier', data: { label: 'Supplier B', risk: 92, type: 'Supplier' }, position: { x: 400, y: 100 } },
    { id: 'SUP-003', type: 'supplier', data: { label: 'Supplier C', risk: 63, type: 'Supplier' }, position: { x: 550, y: 150 } },
    { id: 'PROD-X', type: 'product', data: { label: 'Product X', risk: 20, type: 'Product' }, position: { x: 250, y: 300 } }
  ],
  edges: [
    { id: 'e1', source: 'SUP-001', target: 'INV-001', type: 'INVOICED' },
    { id: 'e2', source: 'SUP-001', target: 'PO-1001', type: 'ORDERED' },
    { id: 'e3', source: 'SUP-001', target: 'SUP-002', type: 'SHARES_ADDRESS', data: { label: 'shared address' }, style: { stroke: '#ef4444' } },
    { id: 'e4', source: 'SUP-001', target: 'SUP-003', type: 'SHARES_BANK_SIGNAL', data: { label: 'shared bank signal' }, style: { stroke: '#f59e0b' } },
    { id: 'e5', source: 'SUP-001', target: 'PROD-X', type: 'SUPPLIES' }
  ]
};
