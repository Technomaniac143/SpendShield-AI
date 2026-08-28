import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  Users, 
  Receipt, 
  Network, 
  Package, 
  Lightbulb, 
  ShieldCheck, 
  TrendingUp, 
  Settings,
  ShieldAlert,
  LogOut,
  Globe
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { authApi } from '../../services/auth';

const navigation = [
  { name: 'Command Center', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Investigations', href: '/investigations', icon: Search },
  { name: 'Suppliers', href: '/suppliers', icon: Users },
  { name: 'Transactions', href: '/transactions', icon: Receipt },
  { name: 'Procurement Graph', href: '/graph', icon: Network },
  { name: 'Inventory', href: '/inventory', icon: Package },
  { name: 'Recommendations', href: '/recommendations', icon: Lightbulb },
  { name: 'Evidence', href: '/evidence', icon: ShieldCheck },
  { name: 'Outcomes', href: '/outcomes', icon: TrendingUp },
  { name: 'Market Intelligence', href: '/market', icon: Globe },
];

export function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 text-slate-300">
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-slate-800">
        <ShieldAlert className="h-8 w-8 text-info" />
        <span className="ml-3 text-lg font-bold text-white tracking-tight">SpendShield <span className="text-info">AI</span></span>
      </div>
      
      <div className="flex flex-1 flex-col overflow-y-auto">
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white',
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon
                    className={cn(
                      isActive ? 'text-info' : 'text-slate-400 group-hover:text-slate-300',
                      'mr-3 h-5 w-5 flex-shrink-0 transition-colors'
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </div>
      
      <div className="flex shrink-0 border-t border-slate-800 p-4 items-center justify-between">
        <div className="flex items-center">
          <div className="inline-block h-9 w-9 rounded-full bg-slate-700 flex items-center justify-center">
            <span className="text-sm font-medium text-white">AD</span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-white">Administrator</p>
            <p className="text-xs font-medium text-slate-400">Demo Tenant</p>
          </div>
        </div>
        <button 
          onClick={() => authApi.logout()} 
          className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          title="Sign Out"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
