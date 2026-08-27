import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { CommandCenter } from './pages/CommandCenter';
import { Suppliers } from './pages/Suppliers';
import { SupplierDetail } from './pages/SupplierDetail';
import { Transactions } from './pages/Transactions';
import { TransactionDetail } from './pages/TransactionDetail';
import { Investigations } from './pages/Investigations';
import { InvestigationDetail } from './pages/InvestigationDetail';
import { ProcurementGraph } from './pages/ProcurementGraph';
import { Recommendations } from './pages/Recommendations';
import { RecommendationDetail } from './pages/RecommendationDetail';
import { Evidence } from './pages/Evidence';
import { Inventory } from './pages/Inventory';
import { Outcomes } from './pages/Outcomes';

// Placeholder Pages
const Settings = () => <div className="p-6"><h1 className="text-2xl font-bold">Settings</h1><p className="mt-4 text-slate-500">Platform configuration.</p></div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<CommandCenter />} />
          
          <Route path="investigations">
            <Route index element={<Investigations />} />
            <Route path=":id" element={<InvestigationDetail />} />
          </Route>
          
          <Route path="suppliers">
            <Route index element={<Suppliers />} />
            <Route path=":id" element={<SupplierDetail />} />
          </Route>
          
          <Route path="transactions">
            <Route index element={<Transactions />} />
            <Route path=":id" element={<TransactionDetail />} />
          </Route>
          
          <Route path="graph" element={<ProcurementGraph />} />
          <Route path="inventory" element={<Inventory />} />
          
          <Route path="recommendations">
            <Route index element={<Recommendations />} />
            <Route path=":id" element={<RecommendationDetail />} />
          </Route>
          
          <Route path="evidence" element={<Evidence />} />
          
          <Route path="outcomes" element={<Outcomes />} />
          <Route path="settings" element={<Settings />} />
          
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
