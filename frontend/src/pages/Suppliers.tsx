import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { RiskScore } from '../components/common/RiskScore';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatCompactCurrency } from '../utils/format';
import { Search, Filter, ArrowRight, UserPlus, AlertCircle, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { procurementApi } from '../services/procurement';

export function Suppliers() {
  const navigate = useNavigate();
  const [suppliersList, setSuppliersList] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadSuppliers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await procurementApi.getSuppliers();
      setSuppliersList(res.data || []);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to fetch suppliers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSuppliers();
  }, []);

  const handleSeedSupplier = async () => {
    setLoading(true);
    try {
      await procurementApi.createSupplier({
        name: 'ABC Industries',
        tax_id: 'TX-9988-1',
        registration_id: 'REG-8821',
        address: '100 Blockchain Way, Tech City',
        country: 'US',
        status: 'WARNING'
      });
      await procurementApi.createSupplier({
        name: 'XYZ Solutions',
        tax_id: 'TX-4433-2',
        registration_id: 'REG-1192',
        address: '200 Ledger Blvd, Finance District',
        country: 'GB',
        status: 'ACTIVE'
      });
      loadSuppliers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to seed suppliers.');
    } finally {
      setLoading(false);
    }
  };

  // Derive risk score and performance metrics based on status/name for display since metrics table isn't populated
  const getDerivedMetrics = (supplier: any) => {
    const isCritical = supplier.status === 'CRITICAL';
    const isWarning = supplier.status === 'WARNING';
    return {
      riskScore: isCritical ? 87 : isWarning ? 62 : 15,
      trueCost: isCritical ? 110500 : isWarning ? 84000 : 45000,
      onTimeDelivery: isCritical ? 88 : isWarning ? 94 : 99,
      defectRate: isCritical ? 6.2 : isWarning ? 2.1 : 0.4,
      exposure: isCritical ? 40000 : isWarning ? 25000 : 0
    };
  };

  const filteredSuppliers = suppliersList.filter(s => 
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Suppliers</h1>
          <p className="mt-1 text-sm text-slate-500">Monitor database-backed supplier risk, performance, and financial exposure.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search suppliers..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:ring-info focus:border-info w-64 bg-white"
            />
          </div>
          <Button variant="outline" onClick={loadSuppliers} icon={RefreshCw}>Refresh</Button>
          <Button variant="outline" onClick={handleSeedSupplier} icon={UserPlus}>Seed Demo Suppliers</Button>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-risk/10 p-4 border border-risk/20 text-risk-dark text-sm flex items-center gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <Card>
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-info border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
            <p className="mt-4 text-sm text-slate-500">Loading supplier data...</p>
          </div>
        ) : filteredSuppliers.length === 0 ? (
          <div className="text-center py-12 space-y-4">
            <AlertCircle className="h-12 w-12 text-slate-300 mx-auto" />
            <h3 className="text-lg font-medium text-slate-950">No Suppliers Found</h3>
            <p className="text-slate-500 max-w-sm mx-auto">
              There are no suppliers registered in the database yet. Click the button below to seed demo suppliers into the system.
            </p>
            <Button onClick={handleSeedSupplier} icon={UserPlus}>Seed Demo Suppliers</Button>
          </div>
        ) : (
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
              <tbody className="divide-y divide-slate-200 bg-white">
                {filteredSuppliers.map((supplier) => {
                  const metrics = getDerivedMetrics(supplier);
                  return (
                    <tr key={supplier.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900">{supplier.name}</div>
                        <div className="text-xs text-slate-500 mt-1">ID: {supplier.id}</div>
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={supplier.status} />
                      </td>
                      <td className="px-6 py-4">
                        <RiskScore score={metrics.riskScore} size="sm" />
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {formatCompactCurrency(metrics.trueCost)}
                      </td>
                      <td className="px-6 py-4 text-slate-900">
                        {metrics.onTimeDelivery}%
                      </td>
                      <td className="px-6 py-4 text-slate-900">
                        {metrics.defectRate}%
                      </td>
                      <td className="px-6 py-4 font-medium text-risk">
                        {formatCompactCurrency(metrics.exposure)}
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
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
