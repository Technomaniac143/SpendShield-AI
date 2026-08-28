import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { recommendations } from '../mocks/recommendations';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatCurrency } from '../utils/format';
import { ArrowLeft, Check, X, ShieldAlert, History } from 'lucide-react';

export function RecommendationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const rec = recommendations.find(r => r.id === id) || recommendations[0];
  const [overrideMode, setOverrideMode] = useState(false);

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="sm" icon={ArrowLeft} onClick={() => navigate('/recommendations')}>
          Back to Recommendations
        </Button>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-slate-900">Decision Workflow</h1>
            <Badge variant={rec.priority === 'CRITICAL' ? 'risk' : 'warning'}>{rec.priority}</Badge>
          </div>
          <p className="mt-1 text-sm text-slate-500">ID: {rec.id} &middot; Entity: {rec.entity}</p>
        </div>
        <StatusBadge status={rec.status} />
      </div>

      <Card>
        <CardContent className="p-0 flex flex-col md:flex-row divide-y md:divide-y-0 md:divide-x divide-slate-200">
          <div className="p-6 flex-1 space-y-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 font-bold mb-1">Identified Problem</p>
              <p className="font-medium text-slate-900">{rec.issue}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 font-bold mb-1">Financial Impact</p>
              <p className="font-bold text-risk text-xl">{formatCurrency(rec.exposure)} Exposure</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500 font-bold mb-1">Confidence</p>
              <p className="font-medium text-slate-900">{Math.round(rec.confidence * 100)}% Evidence-Backed</p>
            </div>
          </div>
          <div className="p-6 flex-1 bg-info-light/30">
            <div>
              <p className="text-xs uppercase tracking-wide text-info font-bold mb-2 flex items-center gap-1">
                <ShieldAlert className="h-4 w-4" /> AI Recommended Action
              </p>
              <h3 className="text-2xl font-bold text-slate-900">{rec.recommendedAction}</h3>
              <p className="mt-4 text-sm text-slate-600">This action mitigates immediate risk and initiates a formal dispute process.</p>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex flex-wrap items-center gap-4 py-4 px-6 bg-slate-50 border-t border-slate-200">
          {!overrideMode ? (
            <>
              <Button icon={Check} variant="primary">Accept & Execute</Button>
              <Button icon={X} variant="outline" onClick={() => setOverrideMode(true)}>Override AI</Button>
            </>
          ) : (
            <div className="w-full flex items-start gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-slate-700 mb-1">Reason for override (Required for audit)</label>
                <textarea className="w-full rounded-md border-slate-300 shadow-sm focus:border-info focus:ring-info sm:text-sm p-2" rows={3} placeholder="Explain why the AI recommendation is being rejected..." />
              </div>
              <div className="flex flex-col gap-2">
                <Button variant="danger">Submit Reject</Button>
                <Button variant="ghost" onClick={() => setOverrideMode(false)}>Cancel</Button>
              </div>
            </div>
          )}
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-slate-400" /> Decision History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative border-l-2 border-slate-200 ml-3 space-y-6">
            <div className="relative pl-6">
              <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 bg-white border-slate-300"></div>
              <p className="text-sm font-medium text-slate-900">Recommendation Generated</p>
              <p className="text-xs text-slate-500 mt-1">By SpendShield AuditAgent &middot; Oct 15, 2023</p>
            </div>
            <div className="relative pl-6">
              <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 bg-white border-slate-300"></div>
              <p className="text-sm font-medium text-slate-900">Pending Review</p>
              <p className="text-xs text-slate-500 mt-1">Awaiting human decision</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
