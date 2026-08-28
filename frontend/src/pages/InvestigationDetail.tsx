import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { investigations } from '../mocks/investigations';
import { evidenceData } from '../mocks/evidence';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { InvestigationTrace } from '../components/investigation/InvestigationTrace';
import { FindingCard } from '../components/investigation/FindingCard';
import { TrueCostBreakdown } from '../components/investigation/TrueCostBreakdown';
import { formatCompactCurrency } from '../utils/format';
import { ArrowLeft, Network, ArrowRight } from 'lucide-react';
import { investigationApi } from '../services/investigationApi';
import { Investigation } from '../types';

export function InvestigationDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const targetId = searchParams.get('target') || 'SUP-001';
  const navigate = useNavigate();
  
  const [investigation, setInvestigation] = useState<Partial<Investigation> | null>(null);

  useEffect(() => {
    if (id === 'new') {
      const cleanup = investigationApi.simulateRealtimeInvestigation(targetId, (newState) => {
        setInvestigation(newState);
      });
      return cleanup;
    } else {
      setInvestigation(investigations.find(i => i.id === id) || investigations[0]);
    }
  }, [id, targetId]);

  if (!investigation) return <div className="p-6">Loading investigation...</div>;

  const trueCostComponents = [
    { label: 'Logistics Penalty', amount: 45, type: 'ADD' as const },
    { label: 'Quality Dispute Cost', amount: 65, type: 'ADD' as const },
    { label: 'Delayed Delivery Cost', amount: 20, type: 'ADD' as const },
    { label: 'Volume Discount', amount: 25, type: 'SUBTRACT' as const },
  ];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => navigate('/investigations')}>
          Back to Investigations
        </Button>
      </div>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900">Investigate {investigation.targetName || 'Entity'}</h1>
            <StatusBadge status={investigation.status || 'WAITING'} />
          </div>
          <p className="mt-1 text-sm text-slate-500">ID: {investigation.id} &middot; Type: {investigation.targetType}</p>
        </div>
      </div>

      {/* Investigation Summary */}
      <Card className="bg-slate-900 text-white border-slate-800">
        <CardContent className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
            <div>
              <p className="text-sm font-medium text-slate-400">Risk Score</p>
              <p className="text-3xl font-bold text-risk-light mt-1">{investigation.riskScore || 0} <span className="text-sm font-normal text-slate-500">/ 100</span></p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">AI Confidence</p>
              <p className="text-3xl font-bold text-info-light mt-1">{Math.round((investigation.confidence || 0) * 100)}%</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Financial Exposure</p>
              <p className="text-3xl font-bold text-risk mt-1">{formatCompactCurrency(investigation.financialExposure || 0)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-400">Potential Savings</p>
              <p className="text-3xl font-bold text-safe mt-1">{formatCompactCurrency(investigation.potentialSavings || 0)}</p>
            </div>
          </div>
          <div className="pt-4 border-t border-slate-800">
            <p className="font-semibold text-lg flex items-center gap-2">
              <span className="px-2 py-1 bg-info/20 text-info-light text-xs rounded uppercase tracking-wider">AI Conclusion</span>
              {investigation.primaryFinding || 'Analyzing patterns...'}
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Trace & Cost */}
        <div className="lg:col-span-1 space-y-6">
          <InvestigationTrace steps={investigation.steps || []} />
          <TrueCostBreakdown 
            quotedPrice={1000} 
            components={trueCostComponents} 
            trueCost={1105} 
          />
        </div>

        {/* Right Column: Findings & Evidence */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-slate-900">Findings & Evidence</h3>
            <Button size="sm" variant="outline" icon={Network} onClick={() => navigate('/graph')}>
              Open Procurement Graph
            </Button>
          </div>
          
          <div className="space-y-4">
            {(investigation.findings || []).map(finding => (
              <FindingCard 
                key={finding.id} 
                finding={finding} 
                evidence={evidenceData.find(e => e.id === finding.evidenceId)} 
              />
            ))}
          </div>

          <Card className="mt-8">
            <CardHeader className="bg-slate-50 border-b border-slate-200">
              <CardTitle>Recommended Action</CardTitle>
            </CardHeader>
            <CardContent className="py-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-lg text-slate-900">Hold affected invoice and investigate supplier.</h4>
                  <p className="text-sm text-slate-500 mt-1">This action mitigates immediate financial exposure while allowing for dispute resolution.</p>
                </div>
                <Button icon={ArrowRight} iconPosition="right" onClick={() => navigate('/recommendations')}>
                  Review Recommendation
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
