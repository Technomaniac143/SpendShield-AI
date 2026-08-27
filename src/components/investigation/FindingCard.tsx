import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Finding, Evidence } from '../../types';
import { formatCompactCurrency } from '../../utils/format';
import { FileText, ShieldCheck, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface FindingCardProps {
  finding: Finding;
  evidence?: Evidence;
}

export function FindingCard({ finding, evidence }: FindingCardProps) {
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();

  return (
    <Card className="border-l-4 border-l-warning">
      <CardHeader className="py-4 cursor-pointer hover:bg-slate-50 transition-colors" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="warning">{finding.type}</Badge>
              <span className="text-xs font-semibold text-slate-500">{Math.round(finding.confidence * 100)}% Confidence</span>
            </div>
            <CardTitle>{finding.title}</CardTitle>
          </div>
          {finding.exposure > 0 && (
            <div className="text-right flex-shrink-0">
              <p className="text-xs text-slate-500 uppercase tracking-wide font-bold">Exposure</p>
              <p className="text-lg font-bold text-risk">{formatCompactCurrency(finding.exposure)}</p>
            </div>
          )}
        </div>
      </CardHeader>
      
      {expanded && (
        <CardContent className="pt-0 pb-4 bg-slate-50/50">
          <div className="pt-4 border-t border-slate-100">
            <p className="text-sm text-slate-700 leading-relaxed mb-4">{finding.description}</p>
            
            {evidence && (
              <div className="bg-white p-4 rounded-lg border border-slate-200">
                <div className="flex items-center gap-2 mb-3">
                  <ShieldCheck className="h-4 w-4 text-safe" />
                  <h5 className="text-sm font-semibold text-slate-900">Verified Evidence</h5>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-slate-500">Source</p>
                    <p className="text-sm font-medium text-slate-900 flex items-center gap-1">
                      <FileText className="h-3 w-3" />
                      {evidence.source}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Evidence Confidence</p>
                    <p className="text-sm font-medium text-slate-900">{Math.round(evidence.confidence * 100)}%</p>
                  </div>
                  <div className="md:col-span-2 bg-slate-50 p-2 rounded text-xs font-mono text-slate-600">
                    <span className="text-slate-400 block mb-1">Calculation:</span>
                    {evidence.calculation}
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <Button size="sm" variant="ghost" icon={ExternalLink} iconPosition="right" onClick={(e) => { e.stopPropagation(); navigate(`/evidence?record=${evidence.recordId}`); }}>
                    View Original Record
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}
