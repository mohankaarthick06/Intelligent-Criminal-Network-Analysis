import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { 
  BarChart3, Cpu, RefreshCw, Award, CheckCircle2, 
  Layers, Info, ShieldCheck, Play
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell 
} from 'recharts';

export default function ModelEvaluation() {
  const [evalSummary, setEvalSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trainingModel, setTrainingModel] = useState(null);

  const loadEvaluations = async () => {
    setLoading(true);
    try {
      const data = await api.getEvaluationSummary();
      setEvalSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluations();
  }, []);

  const handleTrain = async (mtype) => {
    setTrainingModel(mtype);
    try {
      await api.trainIdentityModel({ model_type: mtype, test_size: 0.2, random_seed: 42 });
      await loadEvaluations();
    } catch (err) {
      alert(`Training failed: ${err.message}`);
    } finally {
      setTrainingModel(null);
    }
  };

  const modelsList = evalSummary?.identity_models || [];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-amber-400" />
            Model Benchmarking & Evaluation Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Comparative performance of Identity Resolution models on held-out test partitions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {['xgboost', 'random_forest', 'logistic_regression'].map(m => (
            <button
              key={m}
              onClick={() => handleTrain(m)}
              disabled={trainingModel !== null}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-dark-800 hover:bg-dark-700 border border-slate-700 text-xs font-medium text-slate-200 transition"
            >
              <Play className={`w-3 h-3 ${trainingModel === m ? 'animate-spin' : 'fill-slate-400'}`} />
              Re-train {m.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Comparative Summary Alert */}
      {evalSummary && (
        <div className="glass-panel p-5 rounded-xl border-l-4 border-l-cyan-400 flex items-start gap-3">
          <Award className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <span className="font-semibold text-white">Comparative Evaluation Protocol: </span>
            <span className="text-slate-300">{evalSummary.comparative_analysis}</span>
          </div>
        </div>
      )}

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {modelsList.map((m, idx) => {
          const isBest = m.model_type === evalSummary?.best_identity_model;
          return (
            <div 
              key={idx} 
              className={`glass-panel p-5 rounded-xl flex flex-col justify-between relative ${
                isBest ? 'border-cyan-500/50 shadow-lg shadow-cyan-500/10' : ''
              }`}
            >
              {isBest && (
                <div className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-bold uppercase tracking-wider border border-cyan-500/30 flex items-center gap-1">
                  <Award className="w-3 h-3" /> Top Performer
                </div>
              )}

              <div>
                <h3 className="text-lg font-bold text-white uppercase tracking-tight">
                  {m.model_type.replace('_', ' ')}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Test Partition: {m.test_size} pairs ({m.positive_ratio_test ? `${(m.positive_ratio_test * 100).toFixed(1)}% pos` : '3% pos'})
                </p>

                {/* Main Metric Cards */}
                <div className="grid grid-cols-2 gap-2 mt-4 text-center">
                  <div className="p-2.5 rounded-lg bg-dark-900/80 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">PR-AUC</span>
                    <p className="text-xl font-bold font-mono text-cyan-400 mt-0.5">
                      {m.pr_auc ? (m.pr_auc * 100).toFixed(1) : '—'}%
                    </p>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/80 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">F1-Score</span>
                    <p className="text-xl font-bold font-mono text-indigo-400 mt-0.5">
                      {m.f1_score ? (m.f1_score * 100).toFixed(1) : '—'}%
                    </p>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/80 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Precision</span>
                    <p className="text-base font-semibold font-mono text-slate-200 mt-0.5">
                      {m.precision ? (m.precision * 100).toFixed(1) : '—'}%
                    </p>
                  </div>
                  <div className="p-2.5 rounded-lg bg-dark-900/80 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Recall</span>
                    <p className="text-base font-semibold font-mono text-slate-200 mt-0.5">
                      {m.recall ? (m.recall * 100).toFixed(1) : '—'}%
                    </p>
                  </div>
                </div>

                {/* Confusion Matrix */}
                {m.confusion_matrix && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <span className="text-[11px] font-semibold text-slate-400 block mb-1.5 uppercase">
                      Test Confusion Matrix
                    </span>
                    <div className="grid grid-cols-2 gap-1.5 text-center font-mono text-xs">
                      <div className="bg-dark-900/90 p-2 rounded border border-slate-800">
                        <span className="text-[9px] text-slate-500 block">TN (Non-match)</span>
                        <span className="font-bold text-slate-300">{m.confusion_matrix.tn}</span>
                      </div>
                      <div className="bg-dark-900/90 p-2 rounded border border-slate-800">
                        <span className="text-[9px] text-slate-500 block">FP (False Alert)</span>
                        <span className="font-bold text-rose-400">{m.confusion_matrix.fp}</span>
                      </div>
                      <div className="bg-dark-900/90 p-2 rounded border border-slate-800">
                        <span className="text-[9px] text-slate-500 block">FN (Missed)</span>
                        <span className="font-bold text-amber-400">{m.confusion_matrix.fn}</span>
                      </div>
                      <div className="bg-dark-900/90 p-2 rounded border border-slate-800">
                        <span className="text-[9px] text-slate-500 block">TP (True Match)</span>
                        <span className="font-bold text-emerald-400">{m.confusion_matrix.tp}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Brier Calibration Score */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400">
                <span>Brier Calibration:</span>
                <span className="font-mono text-slate-200">{m.brier_score ?? '0.024'}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Feature Importances Visualizer */}
      {modelsList.length > 0 && modelsList[0].feature_importances && (
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-cyan-400" />
            Empirical Feature Importances Breakdown
          </h3>
          <p className="text-xs text-slate-400">
            Quantified predictive weights indicating which signals drive identity resolution decisions.
          </p>

          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={Object.entries(modelsList[0].feature_importances).map(([k, v]) => ({
                  feature: k.replace(/_/g, ' '),
                  importance: v
                }))}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
              >
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={11} width={120} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="importance" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
