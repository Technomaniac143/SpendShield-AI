import React from 'react';
import { outcomesData } from '../mocks/outcomes';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import { formatCompactCurrency } from '../utils/format';
import { Brain, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export function Outcomes() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Outcomes & Learning</h1>
          <p className="mt-1 text-sm text-slate-500">Track realized savings and AI prediction accuracy.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Realized Savings" value={formatCompactCurrency(outcomesData.metrics.realizedSavings)} status="safe" />
        <MetricCard title="Potential Savings" value={formatCompactCurrency(outcomesData.metrics.potentialSavings)} status="info" />
        <MetricCard title="Leakage Prevented" value={formatCompactCurrency(outcomesData.metrics.leakagePrevented)} status="safe" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="col-span-2">
          <CardHeader className="flex flex-row items-center gap-2">
            <div className="p-2 bg-info-light text-info rounded-md">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <CardTitle>AI Learning Loop</CardTitle>
              <p className="text-sm text-slate-500">Prediction accuracy tracking</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3 font-medium">Recommendation</th>
                    <th className="px-4 py-3 font-medium">Decision</th>
                    <th className="px-4 py-3 font-medium">Predicted True Cost</th>
                    <th className="px-4 py-3 font-medium">Actual True Cost</th>
                    <th className="px-4 py-3 font-medium">Prediction Error</th>
                    <th className="px-4 py-3 font-medium text-right">Realized Savings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {outcomesData.learningLoop.map((loop) => (
                    <tr key={loop.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900">{loop.recommendation}</td>
                      <td className="px-4 py-3">
                        <Badge variant="safe">{loop.decision}</Badge>
                      </td>
                      <td className="px-4 py-3">{formatCompactCurrency(loop.predictedTrueCost)}</td>
                      <td className="px-4 py-3 font-medium">{formatCompactCurrency(loop.actualTrueCost)}</td>
                      <td className="px-4 py-3">
                        <span className="flex items-center gap-1 font-medium text-info">
                          {loop.predictionError > 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                          {Math.abs(loop.predictionError)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-safe text-right">
                        {formatCompactCurrency(loop.realizedSavings)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
