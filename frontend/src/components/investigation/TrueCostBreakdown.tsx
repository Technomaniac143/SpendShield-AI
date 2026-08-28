import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { formatCurrency } from '../../utils/format';
import { ArrowDown, ArrowUp } from 'lucide-react';

interface TrueCostBreakdownProps {
  quotedPrice: number;
  components: {
    label: string;
    amount: number;
    type: 'ADD' | 'SUBTRACT';
  }[];
  trueCost: number;
}

export function TrueCostBreakdown({ quotedPrice, components, trueCost }: TrueCostBreakdownProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>True Procurement Cost</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Base Price */}
          <div className="flex justify-between items-center py-2 border-b border-slate-200">
            <span className="font-semibold text-slate-900">Quoted Price</span>
            <span className="font-semibold text-slate-900">{formatCurrency(quotedPrice)}</span>
          </div>

          {/* Additions & Subtractions */}
          {components.map((comp, idx) => (
            <div key={idx} className="flex justify-between items-center py-1.5 text-sm">
              <span className="text-slate-600 flex items-center gap-2">
                {comp.type === 'ADD' ? (
                  <ArrowUp className="h-3 w-3 text-risk" />
                ) : (
                  <ArrowDown className="h-3 w-3 text-safe" />
                )}
                {comp.label}
              </span>
              <span className={comp.type === 'ADD' ? 'text-risk' : 'text-safe'}>
                {comp.type === 'ADD' ? '+' : '-'}{formatCurrency(comp.amount)}
              </span>
            </div>
          ))}

          {/* Total */}
          <div className="flex justify-between items-center pt-4 mt-2 border-t-2 border-slate-900">
            <span className="text-lg font-bold text-slate-900">True Cost</span>
            <span className="text-xl font-bold text-slate-900">{formatCurrency(trueCost)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
