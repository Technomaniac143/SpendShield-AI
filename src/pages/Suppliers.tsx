import React from 'react';
import { suppliers } from '../mocks/suppliers';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { RiskScore } from '../components/common/RiskScore';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatCompactCurrency, formatPercentage } from '../utils/format';
import { Search, Filter, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Suppliers() {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Suppliers</h1>
          <p className="mt-1 text-sm text-slate-500">Monitor supplier risk, performance, and financial exposure.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search suppliers..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64"
            />
          </div>
          <Button variant="outline" icon={Filter}>Filter</Button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium">Supplier</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Risk Score</th>
                <th className="px-6 py-4 font-medium">True Cost</th>
                <th className="px-6 py-4 font-medium">On-Time Del.</th>
                <th className="px-6 py-4 font-medium">Defect Rate</th>
                <th className="px-6 py-4 font-medium text-risk">Exposure</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {suppliers.map((supplier) => (
                <tr key={supplier.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-900">{supplier.name}</div>
                    <div className="text-xs text-slate-500 mt-1">ID: {supplier.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={supplier.status} />
                  </td>
                  <td className="px-6 py-4">
                    <RiskScore score={supplier.riskScore} size="sm" />
                  </td>
                  <td className="px-6 py-4 font-medium">
                    {formatCompactCurrency(supplier.trueCost)}
                  </td>
                  <td className="px-6 py-4">
                    {supplier.onTimeDelivery}%
                  </td>
                  <td className="px-6 py-4">
                    {supplier.defectRate}%
                  </td>
                  <td className="px-6 py-4 font-medium text-risk">
                    {formatCompactCurrency(supplier.financialExposure)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      icon={ArrowRight} 
                      iconPosition="right"
                      onClick={() => navigate(`/suppliers/${supplier.id}`)}
                    >
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
  );
}
