import { Evidence } from '../types';

export const evidenceData: Evidence[] = [
  {
    id: 'EV-1021',
    source: 'Invoice INV-10482',
    recordId: 'INV-10482',
    finding: 'Invoice quantity exceeds GRN quantity by 80 units.',
    calculation: '(1000 - 920) * 500 = 40,000',
    confidence: 0.98
  },
  {
    id: 'EV-1022',
    source: 'Contract PO-1001',
    recordId: 'PO-1001',
    finding: 'Unit price is 15% above contract.',
    calculation: '(575 - 500) / 500 * 100 = 15%',
    confidence: 0.96
  },
  {
    id: 'EV-1023',
    source: 'Corporate Registry',
    recordId: 'REG-8821',
    finding: 'Shared address with Supplier B.',
    calculation: 'Address hash match: 100%',
    confidence: 0.91
  }
];

export const blockchainEvents = [
  {
    eventId: 'EVT-001',
    recordId: 'INV-10482',
    originalHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    currentHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    verificationStatus: 'VERIFIED',
    actor: 'Warehouse',
    timestamp: '2023-10-15T14:32:00Z',
    blockchainNetwork: 'Hyperledger Fabric',
    document: 'invoice.pdf'
  }
];
