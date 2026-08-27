import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { StatusBadge } from '../common/StatusBadge';
import { Bot, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { InvestigationStep } from '../../types';
import { cn } from '../../utils/cn';

interface InvestigationTraceProps {
  steps: InvestigationStep[];
}

export function InvestigationTrace({ steps }: InvestigationTraceProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-info-light text-info rounded-md">
          <Bot className="h-5 w-5" />
        </div>
        <div>
          <CardTitle>AuditAgent Investigation</CardTitle>
          <p className="text-sm text-slate-500">Autonomous execution trace</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative border-l-2 border-slate-200 ml-3 space-y-8 pb-4">
          {steps.map((step, idx) => (
            <div key={step.id} className="relative pl-6">
              {/* Timeline marker */}
              <div className={cn(
                "absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 bg-white flex items-center justify-center",
                step.status === 'COMPLETED' ? 'border-safe' : 
                step.status === 'RUNNING' ? 'border-info' : 
                step.status === 'FAILED' ? 'border-risk' : 'border-slate-300'
              )}>
                {step.status === 'COMPLETED' && <CheckCircle2 className="h-3 w-3 text-safe" />}
                {step.status === 'RUNNING' && <Clock className="h-3 w-3 text-info animate-spin-slow" />}
                {step.status === 'FAILED' && <AlertCircle className="h-3 w-3 text-risk" />}
              </div>

              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                <div>
                  <h4 className={cn(
                    "text-sm font-semibold",
                    step.status === 'COMPLETED' ? 'text-slate-900' :
                    step.status === 'RUNNING' ? 'text-info-dark' : 'text-slate-500'
                  )}>
                    {step.title}
                  </h4>
                  <p className="text-sm text-slate-500 mt-1">{step.details}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 font-mono bg-slate-50 px-2 py-1 rounded">
                    {step.durationMs}ms
                  </span>
                  <StatusBadge status={step.status} showIcon={false} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
