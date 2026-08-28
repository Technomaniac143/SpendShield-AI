import { apiClient } from './api';

export interface Supplier {
  id: string;
  name: string;
  supplier_code: string;
  risk_score: number;
  confidence: number;
  total_spend: number;
  true_cost: number;
  financial_exposure: number;
  on_time_delivery_rate: number;
  defect_rate: number;
  price_variance: number;
  status: 'ACTIVE' | 'WARNING' | 'CRITICAL';
}

export interface Invoice {
  id: string;
  invoice_number: string;
  supplier_id: string;
  total_amount: number;
  currency: string;
  status: string;
  created_at: string;
}

export const procurementApi = {
  getSuppliers: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/suppliers', { params: { page, page_size: pageSize } });
    return response.data;
  },

  getSupplier: async (id: string) => {
    const response = await apiClient.get(`/suppliers/${id}`);
    return response.data;
  },

  createSupplier: async (data: any) => {
    const response = await apiClient.post('/suppliers', data);
    return response.data;
  },

  getInvoices: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/invoices', { params: { page, page_size: pageSize } });
    return response.data;
  },

  getInvoice: async (id: string) => {
    const response = await apiClient.get(`/invoices/${id}`);
    return response.data;
  },

  createInvoice: async (data: any) => {
    const response = await apiClient.post('/invoices', data);
    return response.data;
  },

  getPurchaseOrders: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/purchase-orders', { params: { page, page_size: pageSize } });
    return response.data;
  },

  getGoodsReceipts: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/goods-receipts', { params: { page, page_size: pageSize } });
    return response.data;
  },

  getPayments: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/payments', { params: { page, page_size: pageSize } });
    return response.data;
  },

  getInventory: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get('/inventory', { params: { page, page_size: pageSize } });
    return response.data;
  },

  calculateThreeWayMatch: async (data: { po_id: string; grn_id: string; invoice_id: string }) => {
    const response = await apiClient.post('/procurement/reconciliation/three-way', data);
    return response.data;
  },

  calculateTrueCost: async (data: { supplier_id: string; base_price: number; shipping_cost: number; quality_defect_cost: number; delay_penalty: number }) => {
    const response = await apiClient.post('/procurement/true-cost/calculate', data);
    return response.data;
  },

  calculateQuantityExposure: async (data: { invoice_id: string }) => {
    const response = await apiClient.post('/procurement/exposure/quantity-mismatch', data);
    return response.data;
  }
};
