import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { Badge } from '../components/common/Badge';
import { formatCompactCurrency } from '../utils/format';
import { Search, Globe, RefreshCw, Layers, TrendingUp, AlertTriangle } from 'lucide-react';
import { apiClient } from '../services/api';

interface MarketProduct {
  id: string;
  name: string;
  sku: string | null;
  manufacturer: string | null;
  category: string | null;
}

interface BenchmarkData {
  product_name: string;
  market_median: number;
  lowest_price: number;
  highest_price: number;
  average_price: number;
  sample_count: number;
  internal_price: number;
  price_variance_percentage: number;
  potential_savings: number;
  internal_quantity: number;
}

interface SupplierResult {
  id: string;
  name: string;
  product_name: string;
  product_id: string;
  price: number;
  currency: string;
  availability: string;
  source: string;
  confidence: number;
}

export function MarketIntelligence() {
  const [products, setProducts] = useState<MarketProduct[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [benchmark, setBenchmark] = useState<BenchmarkData | null>(null);
  const [suppliers, setSuppliers] = useState<SupplierResult[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [collectionQuery, setCollectionQuery] = useState<string>('');
  const [collecting, setCollecting] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial market products list
  const fetchProducts = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<{ products: MarketProduct[] }>('/market/products');
      setProducts(res.data.products);
      if (res.data.products.length > 0 && !selectedProductId) {
        setSelectedProductId(res.data.products[0].id);
      }
    } catch (err) {
      console.error(err);
      setError('Failed to fetch market products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Fetch benchmark data when selected product changes
  useEffect(() => {
    if (selectedProductId) {
      const fetchBenchmark = async () => {
        try {
          const res = await apiClient.get<BenchmarkData>(`/market/benchmark/${selectedProductId}`);
          setBenchmark(res.data);
        } catch (err) {
          console.error(err);
        }
      };
      fetchBenchmark();
    }
  }, [selectedProductId]);

  // Fetch alternative suppliers search
  const handleSearchSuppliers = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await apiClient.get<{ suppliers: SupplierResult[] }>(`/market/suppliers/search?product=${searchQuery}`);
      setSuppliers(res.data.suppliers);
    } catch (err) {
      console.error(err);
      setError('Supplier search failed');
    } finally {
      setLoading(false);
    }
  };

  // Trigger web collection job
  const handleCollect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!collectionQuery) return;
    try {
      setCollecting(true);
      setError(null);
      await apiClient.post('/market/collect', { query: collectionQuery });
      alert('Collection job scheduled! Data will be loaded shortly in the background.');
      setCollectionQuery('');
      // Delay fetch to let the background task work
      setTimeout(() => {
        fetchProducts();
      }, 2000);
    } catch (err) {
      console.error(err);
      setError('Collection request failed');
    } finally {
      setCollecting(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Market & Supplier Intelligence</h1>
          <p className="mt-1 text-sm text-slate-500">Benchmark your procurement prices against global supplier catalog data.</p>
        </div>
      </div>

      {error && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200 text-red-700 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Grid: Search & Collection Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-info" />
              <span>Trigger Market Data Collection</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCollect} className="space-y-4">
              <p className="text-sm text-slate-500">
                Trigger our pluggable collection pipeline to scan public source directories and supplier catalogs for pricing updates.
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. A4 Paper, LaserJet Printer"
                  value={collectionQuery}
                  onChange={(e) => setCollectionQuery(e.target.value)}
                  className="flex-1 min-w-0 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-info focus:ring-1 focus:ring-info outline-none"
                  required
                />
                <button
                  type="submit"
                  disabled={collecting}
                  className="inline-flex items-center justify-center rounded-md bg-info text-slate-900 px-4 py-2 text-sm font-bold hover:bg-info-hover transition-colors disabled:opacity-50"
                >
                  {collecting ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Scanning...
                    </>
                  ) : (
                    'Collect Data'
                  )}
                </button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5 text-info" />
              <span>Find Alternative Suppliers</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearchSuppliers} className="space-y-4">
              <p className="text-sm text-slate-500">
                Query local resolved market suppliers and catalogs to discover competitive alternative sources.
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Search product name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 min-w-0 rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-info focus:ring-1 focus:ring-info outline-none"
                />
                <button
                  type="submit"
                  className="inline-flex items-center justify-center rounded-md bg-slate-900 text-white px-4 py-2 text-sm font-bold hover:bg-slate-800 transition-colors"
                >
                  Search
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Select Product for Benchmarking */}
      <div className="card-base p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Price Benchmarking Tool</h2>
          <p className="text-sm text-slate-500">Select a resolved product to compare internal invoices against collected market data.</p>
        </div>
        <div className="min-w-[250px]">
          <select
            value={selectedProductId}
            onChange={(e) => setSelectedProductId(e.target.value)}
            className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-info"
          >
            <option value="">-- Select Product --</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} {p.sku ? `(SKU: ${p.sku})` : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Benchmarking Metrics */}
      {benchmark && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <MetricCard title="Market Median Price" value={formatCompactCurrency(benchmark.market_median)} status="info" />
            <MetricCard title="Lowest Observed" value={formatCompactCurrency(benchmark.lowest_price)} status="safe" />
            <MetricCard title="Your Invoice Price" value={formatCompactCurrency(benchmark.internal_price)} status="warning" />
            <MetricCard
              title="Potential Savings"
              value={formatCompactCurrency(benchmark.potential_savings)}
              status={benchmark.potential_savings > 0 ? "risk" : "default"}
              trend={{
                value: `${benchmark.price_variance_percentage.toFixed(1)}%`,
                direction: benchmark.price_variance_percentage > 0 ? 'up' : 'down',
                label: 'vs market median',
                isPositive: benchmark.price_variance_percentage <= 0
              }}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Alternative Suppliers list */}
            <Card className="col-span-3">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Discovered Alternative Suppliers</CardTitle>
                  <p className="text-sm text-slate-500">List of verified suppliers carrying this product in our database.</p>
                </div>
                <Badge variant="info">AI Recommendation</Badge>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-600">
                    <thead className="bg-slate-50 text-xs uppercase text-slate-500 border-b border-slate-200">
                      <tr>
                        <th className="px-4 py-3 font-medium">Supplier</th>
                        <th className="px-4 py-3 font-medium">Product Offered</th>
                        <th className="px-4 py-3 font-medium">Listed Price</th>
                        <th className="px-4 py-3 font-medium">Availability</th>
                        <th className="px-4 py-3 font-medium">Source</th>
                        <th className="px-4 py-3 font-medium text-right">Match Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {suppliers.length > 0 ? (
                        suppliers.map((s) => (
                          <tr key={s.id} className="hover:bg-slate-50">
                            <td className="px-4 py-3 font-medium text-slate-900">{s.name}</td>
                            <td className="px-4 py-3 text-slate-500">{s.product_name}</td>
                            <td className="px-4 py-3 font-bold text-slate-800">
                              {s.price} {s.currency}
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant={s.availability === 'IN_STOCK' ? 'safe' : 'warning'}>
                                {s.availability}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-slate-500">{s.source}</td>
                            <td className="px-4 py-3 text-right font-medium text-info">
                              {Math.round(s.confidence * 100)}%
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                            Use the search bar above to look up verified suppliers of this product.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
