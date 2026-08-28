import React from 'react';
import { recommendations } from '../mocks/recommendations';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatCompactCurrency } from '../utils/format';
import { Search, Filter, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Recommendations() {
  const navigate = useNavigate();

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Recommendations Queue</h1>
          <p className="mt-1 text-sm text-slate-500">AI-generated actionable insights to mitigate risk and capture savings.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search recommendations..." 
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
                <th className="px-6 py-4 font-medium">Priority</th>
                <th className="px-6 py-4 font-medium">Issue</th>
                <th className="px-6 py-4 font-medium">Entity</th>
                <th className="px-6 py-4 font-medium text-risk">Exposure</th>
                <th className="px-6 py-4 font-medium">Recommended Action</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {recommendations.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4">
                    <Badge variant={rec.priority === 'CRITICAL' ? 'risk' : rec.priority === 'HIGH' ? 'warning' : 'default'}>
                      {rec.priority}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-900 max-w-xs truncate">{rec.issue}</td>
                  <td className="px-6 py-4">{rec.entity}</td>
                  <td className="px-6 py-4 font-medium text-risk">{formatCompactCurrency(rec.exposure)}</td>
                  <td className="px-6 py-4 max-w-xs truncate">{rec.recommendedAction}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={rec.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      icon={ArrowRight} 
                      iconPosition="right"
                      onClick={() => navigate(`/recommendations/${rec.id}`)}
                    >
                      Review
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
