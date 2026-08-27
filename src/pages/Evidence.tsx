import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { blockchainEvents } from '../mocks/evidence';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { Search, ShieldCheck, ShieldAlert, FileText, Activity } from 'lucide-react';
import { cn } from '../utils/cn';

export function Evidence() {
  const [searchParams] = useSearchParams();
  const recordQuery = searchParams.get('record');
  
  const [isSimulated, setIsSimulated] = useState(false);

  const targetEvent = blockchainEvents.find(e => e.recordId === recordQuery) || blockchainEvents[0];

  const currentStatus = isSimulated ? 'INTEGRITY_FAILURE' : targetEvent.verificationStatus;
  const currentHash = isSimulated 
    ? 'f4a9b33108fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c991' 
    : targetEvent.currentHash;

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Evidence & Provenance</h1>
          <p className="mt-1 text-sm text-slate-500">Blockchain-backed document verification.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search document hash..." 
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Verifications</CardTitle>
            </CardHeader>
            <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
              {blockchainEvents.map((evt) => (
                <div key={evt.eventId} className={cn(
                  "p-4 cursor-pointer transition-colors", 
                  evt.eventId === targetEvent.eventId ? "bg-slate-50 border-l-4 border-info" : "hover:bg-slate-50 border-l-4 border-transparent"
                )}>
                  <div className="flex justify-between items-start mb-1">
                    <p className="font-semibold text-sm text-slate-900">{evt.recordId}</p>
                    <StatusBadge status={evt.verificationStatus} showIcon={false} className="text-[10px] px-1.5 py-0.5" />
                  </div>
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <FileText className="h-3 w-3" /> {evt.document}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          <Card className={cn(
            "border-t-4",
            currentStatus === 'VERIFIED' ? "border-t-safe" : "border-t-risk"
          )}>
            <CardHeader className="pb-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <StatusBadge status={currentStatus} />
                    <span className="text-xs text-slate-500 font-mono">ID: {targetEvent.eventId}</span>
                  </div>
                  <CardTitle className="text-xl">Document Verification for {targetEvent.recordId}</CardTitle>
                </div>
                {currentStatus === 'VERIFIED' ? (
                  <ShieldCheck className="h-10 w-10 text-safe opacity-20" />
                ) : (
                  <ShieldAlert className="h-10 w-10 text-risk opacity-20" />
                )}
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-slate-50 p-3 rounded">
                  <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Actor</p>
                  <p className="font-medium text-slate-900">{targetEvent.actor}</p>
                </div>
                <div className="bg-slate-50 p-3 rounded">
                  <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Timestamp</p>
                  <p className="font-medium text-slate-900">{new Date(targetEvent.timestamp).toLocaleString()}</p>
                </div>
                <div className="bg-slate-50 p-3 rounded">
                  <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Network</p>
                  <p className="font-medium text-slate-900">{targetEvent.blockchainNetwork}</p>
                </div>
                <div className="bg-slate-50 p-3 rounded">
                  <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Document</p>
                  <p className="font-medium text-slate-900 flex items-center gap-1">
                    <FileText className="h-4 w-4" /> {targetEvent.document}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Original Registered Hash (SHA-256)</p>
                  <div className="bg-slate-900 text-slate-300 font-mono text-xs p-3 rounded break-all">
                    {targetEvent.originalHash}
                  </div>
                </div>
                
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Current Document Hash (SHA-256)</p>
                  <div className={cn(
                    "font-mono text-xs p-3 rounded break-all border",
                    currentStatus === 'VERIFIED' 
                      ? "bg-safe-light/30 border-safe/30 text-safe-dark" 
                      : "bg-risk-light/30 border-risk/30 text-risk-dark"
                  )}>
                    {currentHash}
                  </div>
                </div>
                
                {currentStatus !== 'VERIFIED' && (
                  <div className="p-3 bg-risk/10 border border-risk/20 rounded-md text-sm text-risk-dark flex items-start gap-2">
                    <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <strong>Hash Mismatch Detected.</strong> The current document does not match the evidence registered on the blockchain. The document may have been tampered with or modified after registration.
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-slate-400" /> Demonstration Controls
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600 mb-4">
                This control allows you to simulate a document tampering event to observe how SpendShield detects integrity failures.
              </p>
              <Button 
                variant={isSimulated ? 'outline' : 'danger'} 
                onClick={() => setIsSimulated(!isSimulated)}
              >
                {isSimulated ? 'Restore Original Document' : 'Simulate Document Modification'}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function AlertCircle(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
  );
}
