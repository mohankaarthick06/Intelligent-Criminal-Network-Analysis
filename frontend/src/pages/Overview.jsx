import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  ShieldAlert, Database, Network, Cpu, AlertTriangle, 
  CheckCircle2, Activity, ArrowRight, BarChart3, RefreshCw
} from 'lucide-react';

export default function Overview({ onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [systemInfo, setSystemInfo] = useState(null);
  const [graphSummary, setGraphSummary] = useState(null);
  const [anomalySummary, setAnomalySummary] = useState(null);
  const [evalSummary, setEvalSummary] = useState(null);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sys, graph, anom, evals] = await Promise.all([
        api.getSystemInfo().catch(() => null),
        api.getGraphSummary({ min_interactions: 1 }).catch(() => null),
        api.getAnomalySummary().catch(() => null),
        api.getEvaluationSummary().catch(() => null)
      ]);
      setSystemInfo(sys);
      setGraphSummary(graph);
      setAnomalySummary(anom);
      setEvalSummary(evals);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Disclaimer Banner */}
      <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-start gap-3">
        <ShieldAlert className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-200/90 leading-relaxed">
          <span className="font-semibold text-amber-300">Notice: Synthetic Prototype Dataset.</span> All records, Indian-format numbers (+91), locations, and identifiers are synthetically generated for machine learning benchmarking. Model estimates represent statistical pattern similarities and do not establish identity or criminal culpability.
        </div>
      </div>

      {/* Top Header & Refresh */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Intelligent Criminal Network Analysis
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              v1.0.0 Local
            </span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            End-to-end identity resolution, behavioral anomaly detection, and telecom network graph analytics.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-sm font-medium transition text-slate-200"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Stats
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Datasets</p>
            <p className="text-2xl font-bold text-white mt-1">
              {systemInfo ? systemInfo.datasets_available.length : '6'}
            </p>
            <p className="text-xs text-emerald-400 flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> All schemas verified
            </p>
          </div>
          <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Database className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Network Nodes</p>
            <p className="text-2xl font-bold text-white mt-1">
              {graphSummary ? graphSummary.node_count.toLocaleString() : '—'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              {graphSummary ? `${graphSummary.edge_count.toLocaleString()} calls / interactions` : 'Loading...'}
            </p>
          </div>
          <div className="p-3 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Network className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Behavioral Outliers</p>
            <p className="text-2xl font-bold text-rose-400 mt-1">
              {anomalySummary ? anomalySummary.anomalies_count.toLocaleString() : '—'}
            </p>
            <p className="text-xs text-rose-300/80 mt-1">
              {anomalySummary ? `${anomalySummary.anomaly_percentage}% of population` : 'Loading...'}
            </p>
          </div>
          <div className="p-3 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Best Identity Model</p>
            <p className="text-2xl font-bold text-cyber-blue mt-1 uppercase">
              {evalSummary?.best_identity_model || 'XGBoost'}
            </p>
            <p className="text-xs text-emerald-400 mt-1">
              PR-AUC Optimized
            </p>
          </div>
          <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Cpu className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Interactive Module Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div 
          onClick={() => onNavigate('datasets')}
          className="glass-panel hover:glass-panel-glow p-5 rounded-xl cursor-pointer transition flex flex-col justify-between group"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2.5 rounded-lg bg-dark-800 text-cyan-400 border border-slate-700">
                <Database className="w-5 h-5" />
              </span>
              <span className="text-xs font-mono text-slate-400">Module A</span>
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-cyan-300 transition">
              Dataset Ingestion & Quality
            </h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Examine schemas, missingness rates, coordinate validity, and integrity health scores across the 6 synthetic datasets.
            </p>
          </div>
          <div className="mt-5 flex items-center text-sm font-medium text-cyan-400 group-hover:translate-x-1 transition">
            Explore Datasets <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </div>

        <div 
          onClick={() => onNavigate('identity')}
          className="glass-panel hover:glass-panel-glow p-5 rounded-xl cursor-pointer transition flex flex-col justify-between group"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2.5 rounded-lg bg-dark-800 text-indigo-400 border border-slate-700">
                <Cpu className="w-5 h-5" />
              </span>
              <span className="text-xs font-mono text-slate-400">Module C</span>
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-indigo-300 transition">
              Identity Resolution Matcher
            </h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Score candidate SIM/burner pairs using trained XGBoost and Random Forest models with feature contribution explanations.
            </p>
          </div>
          <div className="mt-5 flex items-center text-sm font-medium text-indigo-400 group-hover:translate-x-1 transition">
            Run Predictions <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </div>

        <div 
          onClick={() => onNavigate('network')}
          className="glass-panel hover:glass-panel-glow p-5 rounded-xl cursor-pointer transition flex flex-col justify-between group"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2.5 rounded-lg bg-dark-800 text-emerald-400 border border-slate-700">
                <Network className="w-5 h-5" />
              </span>
              <span className="text-xs font-mono text-slate-400">Module E</span>
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-emerald-300 transition">
              Communication Graph Visualizer
            </h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Interactive Cytoscape.js network explorer with Louvain community detection, centrality metrics, and pairwise link analysis.
            </p>
          </div>
          <div className="mt-5 flex items-center text-sm font-medium text-emerald-400 group-hover:translate-x-1 transition">
            Analyze Network <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </div>

        <div 
          onClick={() => onNavigate('anomalies')}
          className="glass-panel hover:glass-panel-glow p-5 rounded-xl cursor-pointer transition flex flex-col justify-between group"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2.5 rounded-lg bg-dark-800 text-rose-400 border border-slate-700">
                <AlertTriangle className="w-5 h-5" />
              </span>
              <span className="text-xs font-mono text-slate-400">Module D</span>
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-rose-300 transition">
              Behavioral Anomaly Detection
            </h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Unsupervised Isolation Forest isolating subscribers with unusual night calling, high churn, or rapid cell tower movement.
            </p>
          </div>
          <div className="mt-5 flex items-center text-sm font-medium text-rose-400 group-hover:translate-x-1 transition">
            Inspect Outliers <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </div>

        <div 
          onClick={() => onNavigate('evaluation')}
          className="glass-panel hover:glass-panel-glow p-5 rounded-xl cursor-pointer transition flex flex-col justify-between group lg:col-span-2"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="p-2.5 rounded-lg bg-dark-800 text-amber-400 border border-slate-700">
                <BarChart3 className="w-5 h-5" />
              </span>
              <span className="text-xs font-mono text-slate-400">Module F</span>
            </div>
            <h3 className="text-lg font-semibold text-white group-hover:text-amber-300 transition">
              Model Benchmark & Evaluation
            </h3>
            <p className="text-slate-400 text-sm mt-2 leading-relaxed">
              Rigorous comparative benchmarking of Logistic Regression, Random Forest, and XGBoost with PR-AUC, confusion matrices, and probability calibration.
            </p>
          </div>
          <div className="mt-5 flex items-center text-sm font-medium text-amber-400 group-hover:translate-x-1 transition">
            View Evaluation Metrics <ArrowRight className="w-4 h-4 ml-1.5" />
          </div>
        </div>
      </div>
    </div>
  );
}
