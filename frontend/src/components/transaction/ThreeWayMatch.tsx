import React from 'react';
import { Card, CardContent } from '../common/Card';
import { StatusBadge } from '../common/StatusBadge';
import { FileText, Truck, Receipt, ArrowRight, AlertTriangle } from 'lucide-react';
import { formatCurrency } from '../../utils/format';

interface ThreeWayMatchProps {
  transaction: any;
}

export function ThreeWayMatch({ transaction }: ThreeWayMatchProps) {
  const isMatch = transaction.poQuantity === transaction.grnQuantity && transaction.grnQuantity === transaction.invoiceQuantity;

  return (
    <div className="space-y-6">
      {/* Visual Flow */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-6 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex flex-col items-center flex-1">
          <div className="h-12 w-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-3">
            <FileText className="h-6 w-6" />
          </div>
          <h4 className="font-semibold text-slate-900">Purchase Order</h4>
          <p className="text-sm text-slate-500">{transaction.poNumber}</p>
          <div className="mt-2 text-center bg-white border border-slate-200 rounded px-3 py-1.5 shadow-sm text-sm">
            <span className="font-medium">{transaction.poQuantity}</span> units<br/>
            <span className="text-slate-500">{formatCurrency(transaction.poUnitPrice)}/unit</span>
          </div>
        </div>

        <ArrowRight className="h-6 w-6 text-slate-300 hidden md:block flex-shrink-0" />

        <div className="flex flex-col items-center flex-1">
          <div className="h-12 w-12 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mb-3 relative">
            <Truck className="h-6 w-6" />
            {transaction.poQuantity !== transaction.grnQuantity && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-risk opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-risk items-center justify-center">
                  <AlertTriangle className="h-2.5 w-2.5 text-white" />
                </span>
              </span>
            )}
          </div>
          <h4 className="font-semibold text-slate-900">Goods Receipt</h4>
          <p className="text-sm text-slate-500">{transaction.grnNumber}</p>
          <div className="mt-2 text-center bg-white border border-risk rounded px-3 py-1.5 shadow-sm text-sm">
            <span className="font-medium text-risk">{transaction.grnQuantity}</span> units<br/>
            <span className="text-risk text-xs font-medium">80 unit shortage</span>
          </div>
        </div>

        <ArrowRight className="h-6 w-6 text-slate-300 hidden md:block flex-shrink-0" />

        <div className="flex flex-col items-center flex-1">
          <div className="h-12 w-12 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center mb-3 relative">
            <Receipt className="h-6 w-6" />
            {transaction.grnQuantity !== transaction.invoiceQuantity && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-risk opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-risk items-center justify-center">
                  <AlertTriangle className="h-2.5 w-2.5 text-white" />
                </span>
              </span>
            )}
          </div>
          <h4 className="font-semibold text-slate-900">Invoice</h4>
          <p className="text-sm text-slate-500">{transaction.invoiceNumber}</p>
          <div className="mt-2 text-center bg-white border border-risk rounded px-3 py-1.5 shadow-sm text-sm">
            <span className="font-medium">{transaction.invoiceQuantity}</span> units<br/>
            <span className="text-slate-500">{formatCurrency(transaction.invoiceUnitPrice)}/unit</span>
          </div>
        </div>
      </div>

      {/* Reconciliation Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 font-medium">Field</th>
                <th className="px-6 py-3 font-medium">PO</th>
                <th className="px-6 py-3 font-medium">GRN</th>
                <th className="px-6 py-3 font-medium">Invoice</th>
                <th className="px-6 py-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              <tr>
                <td className="px-6 py-3 font-medium text-slate-900">Quantity</td>
                <td className="px-6 py-3">{transaction.poQuantity}</td>
                <td className="px-6 py-3 font-medium text-risk">{transaction.grnQuantity}</td>
                <td className="px-6 py-3">{transaction.invoiceQuantity}</td>
                <td className="px-6 py-3 text-right"><StatusBadge status="FAILED" /></td>
              </tr>
              <tr>
                <td className="px-6 py-3 font-medium text-slate-900">Unit Price</td>
                <td className="px-6 py-3">{formatCurrency(transaction.poUnitPrice)}</td>
                <td className="px-6 py-3 text-slate-400">-</td>
                <td className="px-6 py-3">{formatCurrency(transaction.invoiceUnitPrice)}</td>
                <td className="px-6 py-3 text-right"><StatusBadge status="PASS" /></td>
              </tr>
              <tr>
                <td className="px-6 py-3 font-medium text-slate-900">Total Amount</td>
                <td className="px-6 py-3">{formatCurrency(transaction.poQuantity * transaction.poUnitPrice)}</td>
                <td className="px-6 py-3 text-slate-400">-</td>
                <td className="px-6 py-3">{formatCurrency(transaction.invoiceQuantity * transaction.invoiceUnitPrice)}</td>
                <td className="px-6 py-3 text-right"><StatusBadge status="PASS" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
