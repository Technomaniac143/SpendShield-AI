import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { suppliers } from '../mocks/suppliers';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { RiskScore } from '../components/common/RiskScore';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatCompactCurrency } from '../utils/format';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar
} from 'recharts';
import { Search, ShieldAlert, ArrowLeft } from 'lucide-react';

export function SupplierDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const supplier = suppliers.find(s => s.id === id) || suppliers[0];

  const deliveryData = [
    { month: 'Jan', onTime: 92, delayed: 8 },
    { month: 'Feb', onTime: 88, delayed: 12 },
    { month: 'Mar', onTime: 85, delayed: 15 },
    { month: 'Apr', onTime: 81, delayed: 19 },
    { month: 'May', onTime: 82, delayed: 18 },
    { month: 'Jun', onTime: 81, delayed: 19 },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => navigate('/suppliers')}>
          Back to Suppliers
        </Button>
      </div>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900">{supplier.name}</h1>
            <StatusBadge status={supplier.status} />
          </div>
          <p className="mt-1 text-sm text-slate-500">Supplier ID: {supplier.id}</p>
        </div>
        <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-lg border border-slate-200">
          <div className="text-right mr-2">
            <p className="text-sm font-medium text-slate-500">Overall Risk Score</p>
            <p className="text-xs text-slate-400 mt-0.5">{Math.round(supplier.confidence * 100)}% Confidence</p>
          </div>
          <RiskScore score={supplier.riskScore} size="lg" />
          <Button icon={ShieldAlert} className="ml-4" onClick={() => navigate(`/investigations/new?target=${supplier.id}`)}>
            Investigate
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard title="Total Spend" value={formatCompactCurrency(supplier.totalSpend)} />
        <MetricCard title="True Cost" value={formatCompactCurrency(supplier.trueCost)} />
        <MetricCard title="Financial Exposure" value={formatCompactCurrency(supplier.financialExposure)} status="risk" />
        <MetricCard title="On-Time Delivery" value={`${supplier.onTimeDelivery}%`} status={supplier.onTimeDelivery < 90 ? 'warning' : 'safe'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Delivery Performance Trend</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deliveryData} stackOffset="expand" margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                  <YAxis tickFormatter={(tick) => `${tick * 100}%`} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} />
                  <Bar dataKey="onTime" name="On Time" stackId="a" fill="#10b981" />
                  <Bar dataKey="delayed" name="Delayed" stackId="a" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Risk Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ul className="divide-y divide-slate-100">
                <li className="p-4 flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div>
                    <p className="font-medium text-slate-900">Pricing Risk</p>
                    <p className="text-xs text-slate-500 mt-1">{supplier.priceVariance}% above historical benchmark</p>
                  </div>
                  <RiskScore score={supplier.metrics.pricingRisk} size="sm" />
                </li>
                <li className="p-4 flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div>
                    <p className="font-medium text-slate-900">Delivery Risk</p>
                    <p className="text-xs text-slate-500 mt-1">Degrading on-time performance</p>
                  </div>
                  <RiskScore score={supplier.metrics.deliveryRisk} size="sm" />
                </li>
                <li className="p-4 flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div>
                    <p className="font-medium text-slate-900">Quality Risk</p>
                    <p className="text-xs text-slate-500 mt-1">{supplier.defectRate}% defect rate</p>
                  </div>
                  <RiskScore score={supplier.metrics.qualityRisk} size="sm" />
                </li>
                <li className="p-4 flex justify-between items-center hover:bg-slate-50 transition-colors">
                  <div>
                    <p className="font-medium text-slate-900">Relationship Risk</p>
                    <p className="text-xs text-slate-500 mt-1">Hidden flags detected in graph</p>
                  </div>
                  <RiskScore score={supplier.metrics.relationshipRisk} size="sm" />
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
