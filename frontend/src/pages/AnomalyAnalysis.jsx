import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  AlertTriangle, ShieldCheck, Activity, BarChart2, 
  Search, Play, AlertCircle, CheckCircle, Info
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';

export default function AnomalyAnalysis() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Custom detection test form state
  const [customEntity, setCustomEntity] = useState({
    entity_id: 'TEST-SUB-99',
    calls_per_day: 75.0,
    unique_contacts_per_day: 45.0,
    night_call_ratio: 0.85,
    avg_call_duration_seconds: 240.0,
    daily_contact_change_ratio: 0.78,
    new_cell_count: 8
  });
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const loadSummary = async () => {
    setLoading(true);
    try {
      const data = await api.getAnomalySummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handleRunDetection = async (e) => {
    e.preventDefault();
    setTesting(true);
    try {
      const res = await api.detectAnomalies([customEntity]);
      if (res && res.results.length > 0) {
        setTestResult(res.results[0]);
      }
    } catch (err) {
      alert(`Detection failed: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  // Prepare chart comparison data
  const comparisonData = summary ? [
    {
      feature: 'Calls/Day',
      Normal: summary.feature_averages_normal.calls_per_day || 0,
      Anomalous: summary.feature_averages_anomalous.calls_per_day || 0
    },
    {
      feature: 'Unique Contacts',
      Normal: summary.feature_averages_normal.unique_contacts_per_day || 0,
      Anomalous: summary.feature_averages_anomalous.unique_contacts_per_day || 0
    },
    {
      feature: 'Night Ratio (x100)',
      Normal: (summary.feature_averages_normal.night_call_ratio * 100) || 0,
      Anomalous: (summary.feature_averages_anomalous.night_call_ratio * 100) || 0
    },
    {
      feature: 'New Cells',
      Normal: summary.feature_averages_normal.new_cell_count || 0,
      Anomalous: summary.feature_averages_anomalous.new_cell_count || 0
    }
  ] : [];

  const filteredEntities = summary?.top_anomalies.filter(e => 
    e.entity_id.toLowerCase().includes(search.toLowerCase()) ||
    (e.city && e.city.toLowerCase().includes(search.toLowerCase()))
  ) || [];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 text-rose-400" />
          Behavioral Anomaly Detection (Unsupervised Isolation Forest)
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Identifies extreme outliers across telecommunication patterns without using supervision labels during model fitting.
        </p>
      </div>

      {/* KPI Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="glass-panel p-5 rounded-xl">
            <span className="text-xs text-slate-400 uppercase font-medium">Population Size</span>
            <p className="text-2xl font-bold text-white mt-1">{summary.total_entities.toLocaleString()}</p>
            <p className="text-xs text-slate-400 mt-1">Subscribers evaluated</p>
          </div>
          <div className="glass-panel p-5 rounded-xl">
            <span className="text-xs text-slate-400 uppercase font-medium">Statistical Outliers</span>
            <p className="text-2xl font-bold text-rose-400 mt-1">{summary.anomalies_count.toLocaleString()}</p>
            <p className="text-xs text-rose-300/80 mt-1">{summary.anomaly_percentage}% isolation rate</p>
          </div>
          <div className="glass-panel p-5 rounded-xl">
            <span className="text-xs text-slate-400 uppercase font-medium">Model Contamination Prior</span>
            <p className="text-2xl font-bold text-cyan-400 mt-1">9.0%</p>
            <p className="text-xs text-emerald-400 mt-1">Unsupervised tree ensemble</p>
          </div>
        </div>
      )}

      {/* Visual Comparison & Custom Tester Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Recharts Comparison (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            Normal vs Anomalous Behavioral Baselines
          </h3>
          <p className="text-xs text-slate-400">
            Comparing statistical means of typical subscribers against identified high-risk clusters.
          </p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="feature" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="Normal" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Anomalous" fill="#f43f5e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Custom Subscriber Tester (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-rose-400" />
            Subscriber Anomaly Simulator
          </h3>

          <form onSubmit={handleRunDetection} className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Calls/Day</label>
                <input
                  type="number"
                  value={customEntity.calls_per_day}
                  onChange={e => setCustomEntity({ ...customEntity, calls_per_day: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-dark-900 border border-slate-700 rounded px-2.5 py-1.5 text-white"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Night Call Ratio (0-1)</label>
                <input
                  type="number"
                  step="0.05"
                  max="1"
                  min="0"
                  value={customEntity.night_call_ratio}
                  onChange={e => setCustomEntity({ ...customEntity, night_call_ratio: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-dark-900 border border-slate-700 rounded px-2.5 py-1.5 text-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Contacts/Day</label>
                <input
                  type="number"
                  value={customEntity.unique_contacts_per_day}
                  onChange={e => setCustomEntity({ ...customEntity, unique_contacts_per_day: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-dark-900 border border-slate-700 rounded px-2.5 py-1.5 text-white"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">New Cell Count</label>
                <input
                  type="number"
                  value={customEntity.new_cell_count}
                  onChange={e => setCustomEntity({ ...customEntity, new_cell_count: parseInt(e.target.value) || 0 })}
                  className="w-full bg-dark-900 border border-slate-700 rounded px-2.5 py-1.5 text-white"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={testing}
              className="w-full mt-2 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium transition flex items-center justify-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              {testing ? 'Scoring...' : 'Score Subscriber Behavior'}
            </button>
          </form>

          {/* Test Result Display */}
          {testResult && (
            <div className={`p-3 rounded-lg border text-xs space-y-1.5 ${
              testResult.is_anomaly 
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' 
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            }`}>
              <div className="flex items-center justify-between font-semibold">
                <span>Anomaly Status:</span>
                <span className={`px-2 py-0.5 rounded text-[10px] ${
                  testResult.risk_level === 'HIGH' ? 'bg-rose-500 text-white' :
                  testResult.risk_level === 'MEDIUM' ? 'bg-amber-500 text-black' :
                  'bg-emerald-500 text-white'
                }`}>
                  {testResult.risk_level} RISK
                </span>
              </div>
              <p className="text-slate-300">
                Decision Function Score: <strong className="font-mono">{testResult.anomaly_score}</strong>
              </p>
              <ul className="list-disc list-inside space-y-0.5 text-slate-400 text-[11px] pt-1 border-t border-slate-800">
                {testResult.explanation.map((exp, i) => <li key={i}>{exp}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Top Anomalies Table */}
      <div className="glass-panel rounded-xl overflow-hidden space-y-3">
        <div className="p-5 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Flagged Statistical Anomalies Leaderboard</h3>
            <p className="text-xs text-slate-400 mt-0.5">Ranked by lowest decision score (highest severity deviation)</p>
          </div>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search entity or city..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 rounded-lg bg-dark-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="uppercase bg-dark-900/80 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-5 py-3">Entity ID</th>
                <th className="px-5 py-3">City</th>
                <th className="px-5 py-3">Calls/Day</th>
                <th className="px-5 py-3">Night Ratio</th>
                <th className="px-5 py-3">New Cells</th>
                <th className="px-5 py-3">Anomaly Score</th>
                <th className="px-5 py-3">Risk Assessment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredEntities.slice(0, 15).map((row, i) => (
                <tr key={i} className="hover:bg-dark-800/40 transition">
                  <td className="px-5 py-3 font-semibold text-rose-300">{row.entity_id}</td>
                  <td className="px-5 py-3 text-slate-400 font-sans">{row.city}</td>
                  <td className="px-5 py-3">{row.calls_per_day}</td>
                  <td className="px-5 py-3 font-bold text-amber-400">{(row.night_call_ratio * 100).toFixed(0)}%</td>
                  <td className="px-5 py-3">{row.new_cell_count}</td>
                  <td className="px-5 py-3 text-rose-400">{row.anomaly_score}</td>
                  <td className="px-5 py-3 font-sans">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      row.risk_level === 'HIGH' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                      row.risk_level === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                      'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}>
                      {row.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
