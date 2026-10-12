import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  Database, CheckCircle, AlertTriangle, XCircle, Search, 
  FileText, ShieldCheck, RefreshCw, ChevronLeft, ChevronRight, Table
} from 'lucide-react';

export default function DatasetExplorer() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('cdr');
  const [summary, setSummary] = useState(null);
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('quality'); // 'quality', 'schema', 'preview'
  const [searchQuery, setSearchQuery] = useState('');
  const [previewPage, setPreviewPage] = useState(1);
  const rowsPerPage = 5;

  useEffect(() => {
    api.getDatasets().then(data => {
      setDatasets(data);
      if (data.length > 0 && !data.includes(selectedDataset)) {
        setSelectedDataset(data[0]);
      }
    }).catch(console.error);
  }, []);

  const loadDatasetDetails = async (dsName) => {
    setLoading(true);
    try {
      const [sumData, qualData] = await Promise.all([
        api.getDatasetSummary(dsName),
        api.getQualityReport(dsName)
      ]);
      setSummary(sumData);
      setQuality(qualData);
      setPreviewPage(1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedDataset) {
      loadDatasetDetails(selectedDataset);
    }
  }, [selectedDataset]);

  const filteredPreview = summary?.preview?.filter(row => {
    if (!searchQuery) return true;
    return Object.values(row).some(val => 
      String(val).toLowerCase().includes(searchQuery.toLowerCase())
    );
  }) || [];

  const totalPages = Math.ceil(filteredPreview.length / rowsPerPage) || 1;
  const paginatedRows = filteredPreview.slice((previewPage - 1) * rowsPerPage, previewPage * rowsPerPage);

  return (
    <div className="space-y-6">
      {/* Header & Dataset Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Database className="w-6 h-6 text-cyan-400" />
            Dataset Explorer & Schema Inspector
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Validate synthetic datasets, inspect schema columns, and audit data quality scores.
          </p>
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {datasets.map(ds => (
            <button
              key={ds}
              onClick={() => setSelectedDataset(ds)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap ${
                selectedDataset === ds
                  ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
                  : 'bg-dark-800 text-slate-300 hover:bg-dark-700 border border-slate-700'
              }`}
            >
              {ds}.csv
            </button>
          ))}
        </div>
      </div>

      {/* Dataset Header Stats */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <p className="text-xs text-slate-400 uppercase font-medium">Row Count</p>
            <p className="text-xl font-bold text-white mt-1">{summary.row_count.toLocaleString()}</p>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <p className="text-xs text-slate-400 uppercase font-medium">Column Count</p>
            <p className="text-xl font-bold text-white mt-1">{summary.column_count}</p>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <p className="text-xs text-slate-400 uppercase font-medium">Quality Health</p>
            <p className="text-xl font-bold text-emerald-400 mt-1">
              {quality ? `${quality.integrity_score}%` : '—'}
            </p>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <p className="text-xs text-slate-400 uppercase font-medium">File Size</p>
            <p className="text-xl font-bold text-slate-300 mt-1">
              {(summary.file_size_bytes / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => setActiveTab('quality')}
          className={`pb-3 text-sm font-medium transition flex items-center gap-2 border-b-2 ${
            activeTab === 'quality'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldCheck className="w-4 h-4" /> Data Quality Report
        </button>
        <button
          onClick={() => setActiveTab('schema')}
          className={`pb-3 text-sm font-medium transition flex items-center gap-2 border-b-2 ${
            activeTab === 'schema'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" /> Schema & Data Types
        </button>
        <button
          onClick={() => setActiveTab('preview')}
          className={`pb-3 text-sm font-medium transition flex items-center gap-2 border-b-2 ${
            activeTab === 'preview'
              ? 'border-cyan-400 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Table className="w-4 h-4" /> Data Preview
        </button>
      </div>

      {/* Tab 1: Quality Report */}
      {activeTab === 'quality' && quality && (
        <div className="space-y-6">
          <div className="glass-panel p-5 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Integrity & Quality Health Assessment</h3>
              <p className="text-slate-400 text-sm mt-1">
                Automated checks on coordinate bounds, missing values, duplicates, and expected schemas.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-xs text-slate-400">Integrity Score</span>
                <p className="text-2xl font-bold text-emerald-400">{quality.integrity_score} / 100</p>
              </div>
            </div>
          </div>

          {/* Validation Checks Table */}
          <div className="glass-panel rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-800">
              <h4 className="text-sm font-semibold text-white">Automated Validation Checks</h4>
            </div>
            <div className="divide-y divide-slate-800/60">
              {quality.checks.map((chk, i) => (
                <div key={i} className="px-5 py-3.5 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    {chk.status === 'PASS' && <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
                    {chk.status === 'WARN' && <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />}
                    {chk.status === 'FAIL' && <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />}
                    <div>
                      <span className="text-sm font-medium text-slate-200">{chk.check_name}</span>
                      <p className="text-xs text-slate-400 mt-0.5">{chk.message}</p>
                    </div>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded font-semibold ${
                    chk.status === 'PASS' ? 'bg-emerald-500/20 text-emerald-300' :
                    chk.status === 'WARN' ? 'bg-amber-500/20 text-amber-300' :
                    'bg-rose-500/20 text-rose-300'
                  }`}>
                    {chk.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="glass-panel p-5 rounded-xl">
            <h4 className="text-sm font-semibold text-slate-200 mb-2">Quality Recommendations</h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              {quality.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Tab 2: Schema */}
      {activeTab === 'schema' && summary && (
        <div className="glass-panel rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-dark-900/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Column</th>
                  <th className="px-5 py-3.5">Data Type</th>
                  <th className="px-5 py-3.5">Missing</th>
                  <th className="px-5 py-3.5">Unique Count</th>
                  <th className="px-5 py-3.5">Sample Values</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {summary.column_details.map((col, idx) => (
                  <tr key={idx} className="hover:bg-dark-800/40 transition">
                    <td className="px-5 py-3 font-mono text-cyan-300 font-medium">{col.name}</td>
                    <td className="px-5 py-3 text-xs text-slate-400">{col.dtype}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        col.missing_count === 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {col.missing_count} ({col.missing_percentage}%)
                      </span>
                    </td>
                    <td className="px-5 py-3 text-slate-300">{col.unique_count.toLocaleString()}</td>
                    <td className="px-5 py-3 font-mono text-xs text-slate-400">
                      {col.sample_values.join(', ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 3: Data Preview */}
      {activeTab === 'preview' && summary && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search preview rows..."
                value={searchQuery}
                onChange={e => { setSearchQuery(e.target.value); setPreviewPage(1); }}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-dark-900 border border-slate-700 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span>Page {previewPage} of {totalPages}</span>
              <button
                disabled={previewPage <= 1}
                onClick={() => setPreviewPage(p => Math.max(1, p - 1))}
                className="p-1.5 rounded bg-dark-800 hover:bg-dark-700 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={previewPage >= totalPages}
                onClick={() => setPreviewPage(p => Math.min(totalPages, p + 1))}
                className="p-1.5 rounded bg-dark-800 hover:bg-dark-700 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="glass-panel rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="uppercase bg-dark-900/80 text-slate-400 border-b border-slate-800">
                  <tr>
                    {summary.columns.map((col, i) => (
                      <th key={i} className="px-4 py-3 whitespace-nowrap">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {paginatedRows.map((row, rowIdx) => (
                    <tr key={rowIdx} className="hover:bg-dark-800/40 transition">
                      {summary.columns.map((col, colIdx) => (
                        <td key={colIdx} className="px-4 py-2.5 whitespace-nowrap text-slate-300">
                          {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-600">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
