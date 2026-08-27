import React from 'react';
import { inventoryData } from '../mocks/inventory';
import { Card } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { Button } from '../components/common/Button';
import { formatCompactCurrency } from '../utils/format';
import { Search, Filter, AlertTriangle } from 'lucide-react';

export function Inventory() {
  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Inventory Intelligence</h1>
          <p className="mt-1 text-sm text-slate-500">Monitor cash trapped in excess and slow-moving inventory.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search inventory..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64"
            />
          </div>
          <Button variant="outline" icon={Filter}>Filter</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard title="Total Value" value={formatCompactCurrency(inventoryData.metrics.totalValue)} />
        <MetricCard title="Cash Trapped" value={formatCompactCurrency(inventoryData.metrics.cashTrapped)} status="risk" icon={<AlertTriangle className="h-4 w-4" />} />
        <MetricCard title="Excess Value" value={formatCompactCurrency(inventoryData.metrics.excessValue)} status="warning" />
        <MetricCard title="Slow-Moving" value={formatCompactCurrency(inventoryData.metrics.slowMovingValue)} status="warning" />
        <MetricCard title="Expiring Value" value={formatCompactCurrency(inventoryData.metrics.expiringValue)} status="risk" />
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium">Product ID</th>
                <th className="px-6 py-4 font-medium">Product Name</th>
                <th className="px-6 py-4 font-medium">Warehouse</th>
                <th className="px-6 py-4 font-medium">Quantity</th>
                <th className="px-6 py-4 font-medium text-warning">Value Trapped</th>
                <th className="px-6 py-4 font-medium">Days Idle</th>
                <th className="px-6 py-4 font-medium text-right">Recommended Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {inventoryData.items.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900">{item.id}</td>
                  <td className="px-6 py-4">{item.product}</td>
                  <td className="px-6 py-4">{item.warehouse}</td>
                  <td className="px-6 py-4">{item.quantity.toLocaleString()}</td>
                  <td className="px-6 py-4 font-medium text-warning">
                    {formatCompactCurrency(item.value)}
                  </td>
                  <td className="px-6 py-4">
                    <span className={item.daysIdle > 90 ? 'text-risk font-medium' : ''}>{item.daysIdle} days</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button size="sm" variant="outline">
                      {item.recommendedAction}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
