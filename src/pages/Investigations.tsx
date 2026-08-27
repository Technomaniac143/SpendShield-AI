import React from 'react';
import { investigations } from '../mocks/investigations';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { RiskScore } from '../components/common/RiskScore';
import { formatCompactCurrency } from '../utils/format';
import { Search, Filter, ArrowRight, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Investigations() {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Investigations</h1>
          <p className="mt-1 text-sm text-slate-500">History and status of AI procurement investigations.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative flex-1 md:w-96">
            <Search className="absolute left-3 top-2.5 h-5 w-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="Ask SpendShield to investigate a supplier, transaction or issue..." 
              className="w-full pl-10 pr-12 py-2 border border-slate-300 rounded-full text-sm focus:ring-2 focus:ring-info focus:border-info shadow-sm"
              onKeyDown={(e) => {
                if (e.key === 'Enter') navigate('/investigations/INVEST-001');
              }}
            />
            <button 
              className="absolute right-1 top-1 p-1.5 bg-info text-white rounded-full hover:bg-info-dark transition-colors"
              onClick={() => navigate('/investigations/INVEST-001')}
            >
              <Play className="h-4 w-4 ml-0.5" />
            </button>
          </div>
          <Button variant="outline" icon={Filter} className="hidden md:flex">Filter</Button>
        </div>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-medium">Investigation ID</th>
                <th className="px-6 py-4 font-medium">Target</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Risk Score</th>
                <th className="px-6 py-4 font-medium text-risk">Exposure</th>
                <th className="px-6 py-4 font-medium text-safe">Potential Savings</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {investigations.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900">{inv.id}</td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-900">{inv.targetName}</div>
                    <div className="text-xs text-slate-500 mt-1">{inv.targetType}</div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={inv.status} />
                  </td>
                  <td className="px-6 py-4">
                    <RiskScore score={inv.riskScore} size="sm" />
                  </td>
                  <td className="px-6 py-4 font-medium text-risk">
                    {formatCompactCurrency(inv.financialExposure)}
                  </td>
                  <td className="px-6 py-4 font-medium text-safe">
                    {formatCompactCurrency(inv.potentialSavings)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      icon={ArrowRight} 
                      iconPosition="right"
                      onClick={() => navigate(`/investigations/${inv.id}`)}
                    >
                      Workspace
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
