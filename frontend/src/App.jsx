import React, { useState, useEffect } from 'react';
import Overview from './pages/Overview';
import DatasetExplorer from './pages/DatasetExplorer';
import IdentityResolution from './pages/IdentityResolution';
import NetworkExplorer from './pages/NetworkExplorer';
import AnomalyAnalysis from './pages/AnomalyAnalysis';
import ModelEvaluation from './pages/ModelEvaluation';
import { api } from './api/client';
import { 
  Activity, Database, Network, Cpu, AlertTriangle, 
  BarChart3, ShieldAlert, Circle
} from 'lucide-react';

export default function App() {
  const [currentPage, setCurrentPage] = useState('overview');
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.getHealth();
        setBackendOnline(res.status === 'ok');
      } catch (e) {
        setBackendOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'datasets', label: 'Dataset Explorer', icon: Database },
    { id: 'identity', label: 'Identity Resolution', icon: Cpu },
    { id: 'network', label: 'Network Graph', icon: Network },
    { id: 'anomalies', label: 'Behavioral Anomalies', icon: AlertTriangle },
    { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div 
              onClick={() => setCurrentPage('overview')} 
              className="flex items-center gap-3 cursor-pointer"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Network className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-bold text-base tracking-tight text-white block">
                  CRIME<span className="text-cyan-400">GRAPH</span> AI
                </span>
                <span className="text-[10px] text-slate-400 font-mono -mt-1 block">
                  Criminal Network Intelligence
                </span>
              </div>
            </div>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map(item => {
                const Icon = item.icon;
                const active = currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition ${
                      active
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-dark-800/60'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
            </nav>

            {/* Backend Health Badge */}
            <div className="flex items-center gap-2.5">
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-mono border ${
                backendOnline 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}>
                <Circle className={`w-2 h-2 fill-current ${backendOnline ? 'animate-pulse text-emerald-400' : 'text-rose-400'}`} />
                {backendOnline ? 'API Connected' : 'Connecting...'}
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Scrollbar */}
        <div className="md:hidden flex overflow-x-auto px-4 py-2 border-t border-slate-800/60 gap-1 text-xs">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap ${
                currentPage === item.id ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Page Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentPage === 'overview' && <Overview onNavigate={setCurrentPage} />}
        {currentPage === 'datasets' && <DatasetExplorer />}
        {currentPage === 'identity' && <IdentityResolution />}
        {currentPage === 'network' && <NetworkExplorer />}
        {currentPage === 'anomalies' && <AnomalyAnalysis />}
        {currentPage === 'evaluation' && <ModelEvaluation />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#060911] py-6 text-center text-xs text-slate-500">
        <p>Intelligent Criminal Network Analysis • Prototype Data Science Platform</p>
        <p className="mt-1 text-[11px] text-slate-600">
          All records & telemetry data are synthetic. Model estimations serve investigative hypothesis generation only.
        </p>
      </footer>
    </div>
  );
}
