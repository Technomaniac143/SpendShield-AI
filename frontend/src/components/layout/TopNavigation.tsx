import React from 'react';
import { Bell, HelpCircle, Search } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const routeNames: Record<string, string> = {
  '/dashboard': 'Command Center',
  '/investigations': 'Investigations',
  '/suppliers': 'Suppliers',
  '/transactions': 'Transactions',
  '/graph': 'Procurement Graph',
  '/inventory': 'Inventory',
  '/recommendations': 'Recommendations',
  '/evidence': 'Evidence',
  '/outcomes': 'Outcomes',
  '/settings': 'Settings',
};

export function TopNavigation() {
  const location = useLocation();
  
  // Basic route name resolution - can be expanded for dynamic routes like /investigations/:id
  const getPageTitle = () => {
    const path = location.pathname;
    if (routeNames[path]) return routeNames[path];
    
    // Check for dynamic routes
    if (path.startsWith('/investigations/')) return 'Investigation Workspace';
    if (path.startsWith('/suppliers/')) return 'Supplier Profile';
    if (path.startsWith('/transactions/')) return 'Transaction Detail';
    if (path.startsWith('/recommendations/')) return 'Recommendation Detail';
    if (path.startsWith('/evidence/')) return 'Evidence Detail';
    
    return 'SpendShield AI';
  };

  return (
    <div className="sticky top-0 z-10 flex h-16 flex-shrink-0 bg-white border-b border-slate-200 shadow-sm">
      <div className="flex flex-1 justify-between px-6">
        <div className="flex flex-1 items-center">
          <h1 className="text-xl font-semibold text-slate-900 tracking-tight">
            {getPageTitle()}
          </h1>
        </div>
        
        <div className="ml-4 flex items-center space-x-4 md:ml-6">
          <div className="relative rounded-md shadow-sm max-w-lg hidden sm:block">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <Search className="h-4 w-4 text-slate-400" aria-hidden="true" />
            </div>
            <input
              type="text"
              name="search"
              id="global-search"
              className="block w-full rounded-md border-0 py-1.5 pl-9 pr-3 text-slate-900 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-info sm:text-sm sm:leading-6 bg-slate-50 transition-all"
              placeholder="Search suppliers, invoices, POs..."
            />
          </div>
          
          <button
            type="button"
            className="rounded-full bg-white p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-info focus:ring-offset-2 transition-colors"
          >
            <span className="sr-only">View notifications</span>
            <Bell className="h-5 w-5" aria-hidden="true" />
          </button>
          
          <button
            type="button"
            className="rounded-full bg-white p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-info focus:ring-offset-2 transition-colors"
          >
            <span className="sr-only">Help</span>
            <HelpCircle className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
