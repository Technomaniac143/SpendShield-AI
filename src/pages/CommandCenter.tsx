import React from 'react';
import { 
  dashboardKPIs, 
  priorityActions, 
  spendRiskTrend,
  leakageByCategory
} from '../mocks/dashboard';
import { suppliers } from '../mocks/suppliers';
import { MetricCard } from '../components/common/MetricCard';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { RiskScore } from '../components/common/RiskScore';
import { formatCompactCurrency } from '../utils/format';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { AlertCircle, ArrowRight, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function CommandCenter() {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">SpendShield Command Center</h1>
          <p className="mt-1 text-sm text-slate-500">Procurement intelligence across spend, suppliers, inventory and evidence.</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="bg-white border border-slate-300 rounded-md text-sm px-3 py-2 shadow-sm focus:ring-info focus:border-info">
            <option>Last 30 Days</option>
            <option>Last 90 Days</option>
            <option>Year to Date</option>
          </select>
          <Button icon={ShieldAlert}>New Investigation</Button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {dashboardKPIs.map(kpi => (
          <MetricCard
            key={kpi.id}
            title={kpi.label}
            value={formatCompactCurrency(kpi.value)}
            status={kpi.status}
            trend={{
              value: `${Math.abs(kpi.trend)}%`,
              direction: kpi.trend >= 0 ? 'up' : 'down',
              label: kpi.trendLabel,
              // For exposure/at-risk, 'up' is bad. For savings, 'up' is good.
              isPositive: kpi.label.includes('Spend') || kpi.label.includes('Exposure') || kpi.label.includes('Trapped') ? kpi.trend < 0 : kpi.trend >= 0
            }}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Priority Actions */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-4">
              <CardTitle className="text-risk">Priority Actions</CardTitle>
              <Badge variant="risk">{priorityActions.length} Pending</Badge>
            </CardHeader>
            <CardContent className="p-0">
              <ul className="divide-y divide-slate-100">
                {priorityActions.map(action => (
                  <li key={action.id} className="p-4 hover:bg-slate-50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-risk flex-shrink-0" />
                        <span className="text-sm font-bold text-slate-900">{action.action}</span>
                      </div>
                      <Badge variant={action.severity === 'CRITICAL' ? 'risk' : 'warning'}>
                        {action.severity}
                      </Badge>
                    </div>
                    <div className="mt-2 text-sm text-slate-900 font-medium">
                      {action.entity} &middot; <span className="text-risk">{formatCompactCurrency(action.exposure)} exposure</span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500 line-clamp-2">
                      {action.reason}
                    </p>
                    <div className="mt-3 flex items-center justify-between">
                      <span className="text-xs text-slate-400">{Math.round(action.confidence * 100)}% AI Confidence</span>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => navigate(action.entityType === 'SUPPLIER' ? `/suppliers/${action.entity}` : `/transactions/${action.entity}`)}
                      >
                        Investigate
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="py-4">
              <CardTitle>Cash Trapped in Inventory</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold text-warning">₹31.4L</div>
              <div className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="text-slate-500">Slow-moving</span>
                  <span className="font-medium">₹12.2L</span>
                </div>
                <div className="flex justify-between border-b border-slate-100 pb-2">
                  <span className="text-slate-500">Excess</span>
                  <span className="font-medium">₹14.8L</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Expiring</span>
                  <span className="font-medium">₹4.4L</span>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4"
                onClick={() => navigate('/inventory')}
              >
                View Inventory
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Charts & Tables */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader className="py-4">
                <CardTitle>Spend Risk Trend</CardTitle>
              </CardHeader>
              <CardContent className="h-64 pt-0">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={spendRiskTrend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                    <YAxis 
                      yAxisId="left" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 12, fill: '#64748b' }}
                      tickFormatter={(val) => `₹${val/100000}L`}
                    />
                    <RechartsTooltip 
                      formatter={(value: any) => formatCompactCurrency(value)}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: 12, paddingTop: 20 }} />
                    <Line yAxisId="left" type="monotone" dataKey="totalSpend" name="Total Spend" stroke="#94a3b8" strokeWidth={2} dot={false} />
                    <Line yAxisId="left" type="monotone" dataKey="riskySpend" name="Risky Spend" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
                    <Line yAxisId="left" type="monotone" dataKey="exposure" name="Exposure" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="py-4">
                <CardTitle>Financial Exposure by Category</CardTitle>
              </CardHeader>
              <CardContent className="h-64 pt-0">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={leakageByCategory} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                    <XAxis type="number" hide />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fontSize: 11, fill: '#475569' }} 
                      width={100}
                    />
                    <RechartsTooltip 
                      formatter={(value: any) => formatCompactCurrency(value)}
                      cursor={{ fill: '#f8fafc' }}
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                    />
                    <Bar dataKey="value" name="Exposure" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between py-4">
              <CardTitle>Supplier Risk Watchlist</CardTitle>
              <Button variant="ghost" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/suppliers')}>
                View All
              </Button>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-6 py-3 font-medium">Supplier</th>
                    <th className="px-6 py-3 font-medium">Risk Score</th>
                    <th className="px-6 py-3 font-medium">True Cost</th>
                    <th className="px-6 py-3 font-medium">Exposure</th>
                    <th className="px-6 py-3 font-medium text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {suppliers.slice(0, 3).map((supplier) => (
                    <tr key={supplier.id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-900">{supplier.name}</td>
                      <td className="px-6 py-4">
                        <RiskScore score={supplier.riskScore} size="sm" />
                      </td>
                      <td className="px-6 py-4">{formatCompactCurrency(supplier.trueCost)}</td>
                      <td className="px-6 py-4 font-medium text-risk">{formatCompactCurrency(supplier.financialExposure)}</td>
                      <td className="px-6 py-4 text-right">
                        <Button size="sm" variant="outline" onClick={() => navigate(`/suppliers/${supplier.id}`)}>
                          Investigate
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
