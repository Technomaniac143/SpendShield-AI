import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { Search, ShieldCheck, ShieldAlert, FileText, Paperclip, Upload, CheckCircle2, History } from 'lucide-react';
import { cn } from '../utils/cn';
import { evidenceApi } from '../services/evidence';

interface EvidenceDetail {
  eventId: string;
  recordId: string;
  eventType: string;
  timestamp: string;
  sourceType: string;
  sourceId: string | null;
  metadataHash: string | null;
  documentHash: string;
  previousHash: string | null;
  recordHash: string;
  verificationStatus: string;
  status: string;
}

export function Evidence() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryEventId = searchParams.get('eventId');

  // List of active/recent verifications (we keep a local list, populated dynamically)
  const [eventsList, setEventsList] = useState<string[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>(queryEventId || '');
  const [searchQuery, setSearchQuery] = useState('');

  // Evidence state
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [historyList, setHistoryList] = useState<any[]>([]);
  const [blockchainInfo, setBlockchainInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Simulation state
  const [isSimulated, setIsSimulated] = useState(false);
  const [simulatedHash, setSimulatedHash] = useState<string | null>(null);

  // Form registration state
  const [regEventId, setRegEventId] = useState('');
  const [regRecordId, setRegRecordId] = useState('');
  const [regEventType, setRegEventType] = useState('INVOICE_REGISTERED');
  const [regFile, setRegFile] = useState<File | null>(null);
  const [regSuccess, setRegSuccess] = useState(false);
  const [regError, setRegError] = useState<string | null>(null);
  const [regLoading, setRegLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load selected evidence data
  const loadEvidenceData = async (eventId: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await evidenceApi.getEvidence(eventId);
      if (data.status === 'NOT_REGISTERED') {
        setEvidence(null);
        setError(`Evidence event ID "${eventId}" is not registered in the database ledger.`);
      } else {
        setEvidence(data);
        // Add to recent list if not already present
        if (!eventsList.includes(eventId)) {
          setEventsList(prev => [eventId, ...prev]);
        }
        // Load history and blockchain
        try {
          const hist = await evidenceApi.getHistory(eventId);
          setHistoryList(hist.history || []);
          const chain = await evidenceApi.getBlockchain(eventId);
          setBlockchainInfo(chain.fabric);
        } catch (e) {
          console.warn('Failed to load history or blockchain details:', e);
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to fetch evidence.');
      setEvidence(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedEventId && selectedEventId.trim()) {
      loadEvidenceData(selectedEventId);
    }
  }, [selectedEventId]);

  // Handle verify request
  const handleVerify = async () => {
    if (!evidence) return;
    setLoading(true);
    try {
      const res = await evidenceApi.verify(evidence.eventId);
      if (res.status) {
        setEvidence(prev => prev ? { ...prev, verificationStatus: res.status } : null);
      }
      setIsSimulated(false);
      setSimulatedHash(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification request failed.');
    } finally {
      setLoading(false);
    }
  };

  // Handle simulate tampering
  const handleSimulateTamper = async () => {
    if (!evidence) return;
    setLoading(true);
    try {
      const res = await evidenceApi.simulateModification(evidence.eventId);
      if (res.status === 'INTEGRITY_FAILURE') {
        setIsSimulated(true);
        setSimulatedHash(res.simulated_current_hash);
        setEvidence(prev => prev ? { ...prev, verificationStatus: 'INTEGRITY_FAILURE' } : null);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to simulate tampering.');
    } finally {
      setLoading(false);
    }
  };

  // Handle registration submission
  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!regEventId || !regRecordId || !regFile) {
      setRegError('Please fill in all fields and select a PDF file.');
      return;
    }
    setRegLoading(true);
    setRegError(null);
    setRegSuccess(false);

    const formData = new FormData();
    formData.append('record_id', regRecordId);
    formData.append('event_type', regEventType);
    formData.append('timestamp', new Date().toISOString());
    formData.append('document', regFile);

    try {
      const res = await evidenceApi.register(regEventId, formData);
      if (res.status === 'REGISTERED') {
        setRegSuccess(true);
        setSelectedEventId(regEventId);
        setSearchParams({ eventId: regEventId });
        // Clear form
        setRegEventId('');
        setRegRecordId('');
        setRegFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setRegError(detail.map((d: any) => d.msg || JSON.stringify(d)).join('; '));
      } else {
        setRegError(typeof detail === 'string' ? detail : 'Failed to register evidence. Ensure file is a valid PDF.');
      }
    } finally {
      setRegLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setSelectedEventId(searchQuery.trim());
      setSearchParams({ eventId: searchQuery.trim() });
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Evidence & Provenance</h1>
          <p className="mt-1 text-sm text-slate-500">Database-backed cryptographic hash chain verification.</p>
        </div>
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search Event ID..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64 bg-white"
            />
          </div>
          <Button type="submit">Search</Button>
        </form>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent and Register form */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Verifications</CardTitle>
            </CardHeader>
            <div className="divide-y divide-slate-100 max-h-60 overflow-y-auto">
              {eventsList.map((id) => (
                <div 
                  key={id} 
                  onClick={() => {
                    setSelectedEventId(id);
                    setSearchParams({ eventId: id });
                  }}
                  className={cn(
                    "p-4 cursor-pointer transition-colors border-l-4", 
                    id === selectedEventId ? "bg-slate-50 border-l-info text-info font-medium" : "hover:bg-slate-50 border-l-transparent text-slate-700"
                  )}
                >
                  <div className="flex justify-between items-center">
                    <p className="text-sm">{id}</p>
                    <span className="text-xs text-slate-400">Click to load</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5 text-slate-500" /> Register New Evidence
              </CardTitle>
            </CardHeader>
            <CardContent>
              {regSuccess && (
                <div className="mb-4 rounded-md bg-safe/10 p-3 border border-safe/20 text-safe-dark text-sm flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 flex-shrink-0" />
                  <span>Evidence registered successfully!</span>
                </div>
              )}
              {regError && (
                <div className="mb-4 rounded-md bg-risk/10 p-3 border border-risk/20 text-risk-dark text-sm flex items-start gap-2">
                  <ShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5" />
                  <span>{regError}</span>
                </div>
              )}
              <form onSubmit={handleRegisterSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Event ID</label>
                  <input 
                    type="text" 
                    placeholder="e.g. EVT-9999"
                    required
                    value={regEventId}
                    onChange={(e) => setRegEventId(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Record ID</label>
                  <input 
                    type="text" 
                    placeholder="e.g. INV-1002"
                    required
                    value={regRecordId}
                    onChange={(e) => setRegRecordId(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm bg-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Event Type</label>
                  <select 
                    value={regEventType}
                    onChange={(e) => setRegEventType(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded text-sm bg-white"
                  >
                    <option value="INVOICE_REGISTERED">Invoice Registered</option>
                    <option value="GOODS_RECEIVED">Goods Received</option>
                    <option value="PAYMENT_COMPLETED">Payment Completed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">PDF Document</label>
                  {/* Hidden native file input — triggered programmatically */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    style={{ display: 'none' }}
                    onChange={(e) => setRegFile(e.target.files?.[0] || null)}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2 px-4 py-2 rounded-md border border-slate-300 bg-white text-sm font-semibold text-slate-600 hover:bg-slate-50 hover:border-slate-400 transition-colors cursor-pointer"
                  >
                    <Paperclip className="h-4 w-4 text-slate-500" />
                    {regFile ? regFile.name : 'Choose PDF file…'}
                  </button>
                  {regFile && (
                    <p className="mt-1 text-xs text-slate-400">
                      {(regFile.size / 1024).toFixed(1)} KB selected
                    </p>
                  )}
                </div>
                <Button type="submit" disabled={regLoading} className="w-full">
                  {regLoading ? 'Registering...' : 'Register Evidence'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Detailed panel */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="rounded-md bg-risk/10 p-4 border border-risk/20 text-risk-dark text-sm flex items-start gap-3">
              <ShieldAlert className="h-6 w-6 mt-0.5 flex-shrink-0" />
              <div>
                <strong className="block font-bold">Ledger Query Message</strong>
                <span>{error}</span>
              </div>
            </div>
          )}

          {evidence ? (
            <>
              <Card className={cn(
                "border-t-4",
                evidence.verificationStatus === 'VERIFIED' ? "border-t-safe" : "border-t-risk"
              )}>
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <StatusBadge status={evidence.verificationStatus} />
                        <span className="text-xs text-slate-500 font-mono">Event ID: {evidence.eventId}</span>
                      </div>
                      <CardTitle className="text-xl">Cryptographic Provenance Verification</CardTitle>
                    </div>
                    {evidence.verificationStatus === 'VERIFIED' ? (
                      <ShieldCheck className="h-10 w-10 text-safe opacity-50" />
                    ) : (
                      <ShieldAlert className="h-10 w-10 text-risk opacity-50" />
                    )}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Record ID</p>
                      <p className="font-medium text-slate-900">{evidence.recordId}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Event Type</p>
                      <p className="font-medium text-slate-900">{evidence.eventType}</p>
                    </div>
                    <div className="bg-slate-50 p-3 rounded">
                      <p className="text-slate-500 text-xs uppercase font-semibold mb-1">Timestamp</p>
                      <p className="font-medium text-slate-900">{new Date(evidence.timestamp).toLocaleString()}</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Document SHA-256 Hash</p>
                      <div className="bg-slate-900 text-slate-300 font-mono text-xs p-3 rounded break-all border border-slate-800">
                        {isSimulated && simulatedHash ? simulatedHash : evidence.documentHash}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Previous Chain Record Hash</p>
                      <div className="bg-slate-900 text-slate-400 font-mono text-xs p-3 rounded break-all border border-slate-800">
                        {evidence.previousHash || 'Genesis Block (None)'}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Current Chain Record Hash</p>
                      <div className={cn(
                        "font-mono text-xs p-3 rounded break-all border",
                        evidence.verificationStatus === 'VERIFIED' 
                          ? "bg-safe/5 border-safe/20 text-safe-dark" 
                          : "bg-risk/5 border-risk/20 text-risk-dark"
                      )}>
                        {evidence.recordHash}
                      </div>
                    </div>

                    {evidence.verificationStatus === 'INTEGRITY_FAILURE' && (
                      <div className="p-4 bg-risk/10 border border-risk/20 rounded-md text-sm text-risk-dark flex items-start gap-2">
                        <ShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5" />
                        <div>
                          <strong>Ledger Integrity Failure!</strong> The current document hash or record properties do not match the cryptographic signature chained in the database ledger. Tampering or parameter alteration detected.
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3 pt-2">
                    <Button onClick={handleVerify}>Verify Integrity</Button>
                    <Button variant="outline" onClick={handleSimulateTamper}>Simulate Tampering</Button>
                  </div>
                </CardContent>
              </Card>

              {/* History Timeline */}
              {historyList.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <History className="h-5 w-5 text-slate-400" /> Cryptographic Ledger History
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flow-root">
                      <ul className="-mb-8">
                        {historyList.map((item, itemIdx) => (
                          <li key={itemIdx}>
                            <div className="relative pb-8">
                              {itemIdx !== historyList.length - 1 ? (
                                <span className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true" />
                              ) : null}
                              <div className="relative flex space-x-3">
                                <div>
                                  <span className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center ring-8 ring-white">
                                    <FileText className="h-4 w-4 text-slate-500" />
                                  </span>
                                </div>
                                <div className="flex-1 min-w-0 pt-1.5">
                                  <p className="text-sm text-slate-800">
                                    Event: <strong className="text-slate-900">{item.eventType}</strong> by{' '}
                                    <span className="font-semibold text-slate-900">{item.actor || 'System'}</span>
                                  </p>
                                  <div className="text-xs text-slate-400 mt-0.5">
                                    {new Date(item.timestamp).toLocaleString()}
                                  </div>
                                  <div className="mt-2 text-xs font-mono bg-slate-50 text-slate-600 p-2 rounded break-all border border-slate-100">
                                    Record Hash: {item.recordHash}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg border border-slate-200 shadow-sm">
              <ShieldAlert className="h-12 w-12 text-slate-300 mx-auto mb-3" />
              <p className="text-slate-500">No active evidence record loaded. Select a recent one or search above.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
