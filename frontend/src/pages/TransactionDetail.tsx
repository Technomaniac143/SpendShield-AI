import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { transactions } from '../mocks/transactions';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { ThreeWayMatch } from '../components/transaction/ThreeWayMatch';
import { ArrowLeft, ShieldAlert, ShieldCheck } from 'lucide-react';
import { formatCurrency } from '../utils/format';

export function TransactionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const transaction = transactions.find(t => t.id === id) || transactions[0];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => navigate('/transactions')}>
          Back to Transactions
        </Button>
      </div>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900">{transaction.id}</h1>
            <StatusBadge status={transaction.status} />
          </div>
          <p className="mt-1 text-sm text-slate-500">Supplier: <span className="font-medium text-info cursor-pointer hover:underline" onClick={() => navigate(`/suppliers/${transaction.supplierId}`)}>{transaction.supplierName}</span> &middot; Date: {transaction.date}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" icon={ShieldAlert} onClick={() => navigate(`/investigations/new?target=${transaction.id}`)}>
            Investigate
          </Button>
        </div>
      </div>

      {transaction.exposure > 0 && (
        <div className="bg-risk-light border border-risk/20 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-risk text-white rounded-full">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-risk-dark text-lg">Financial Exposure Detected</h3>
              <p className="text-sm text-risk-dark/80">A quantity mismatch between the Goods Receipt Note and Invoice has created exposure.</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-risk-dark/80 uppercase font-bold tracking-wider">Exposure Amount</p>
            <p className="text-2xl font-bold text-risk-dark">{formatCurrency(transaction.exposure)}</p>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Three-Way Match Reconciliation</CardTitle>
        </CardHeader>
        <CardContent>
          <ThreeWayMatch transaction={transaction} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Blockchain Evidence Verification</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
              <div className="p-3 bg-safe-light text-safe rounded-full">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-slate-900 flex items-center gap-2">
                  Document Integrity
                  <StatusBadge status="VERIFIED" showIcon={false} />
                </h4>
                <p className="text-sm text-slate-500 mt-1">Invoice and GRN records matched against on-chain hash.</p>
              </div>
              <Button size="sm" variant="outline" onClick={() => navigate(`/evidence?record=${transaction.invoiceNumber}`)}>View Proof</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recommended Action</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-slate-700">Based on the calculated exposure and integrity verification:</p>
            <div className="p-4 bg-slate-900 rounded-lg border border-slate-800 text-white">
              <h4 className="font-bold text-lg text-risk-light">HOLD PAYMENT</h4>
              <p className="text-sm text-slate-400 mt-1">Block payment of {formatCurrency(transaction.invoiceQuantity * transaction.invoiceUnitPrice)} and request supplier investigation for {transaction.supplierName}.</p>
            </div>
            <div className="flex gap-3">
              <Button variant="danger" className="flex-1">Execute Hold</Button>
              <Button variant="outline" className="flex-1">Override</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
