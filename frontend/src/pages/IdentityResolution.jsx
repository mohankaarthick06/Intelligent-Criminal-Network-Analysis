import React, { useState } from 'react';
import { api } from '../api/client';
import { 
  Cpu, ShieldAlert, Sparkles, CheckCircle2, XCircle, 
  Layers, ArrowRight, Play, Info
} from 'lucide-react';

export default function IdentityResolution() {
  const [modelType, setModelType] = useState('xgboost');
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [features, setFeatures] = useState({
    same_device_observed: 1,
    contact_overlap_jaccard: 0.82,
    temporal_pattern_similarity: 0.75,
    location_overlap_similarity: 0.68,
    call_pattern_similarity: 0.85,
    shared_case_count: 2,
    days_between_observations: 14.0
  });

  const handleSliderChange = (key, val) => {
    setFeatures(prev => ({ ...prev, [key]: parseFloat(val) }));
  };

  const applyPreset = (preset) => {
    if (preset === 'burner') {
      setFeatures({
        same_device_observed: 1,
        contact_overlap_jaccard: 0.92,
        temporal_pattern_similarity: 0.84,
        location_overlap_similarity: 0.78,
        call_pattern_similarity: 0.89,
        shared_case_count: 3,
        days_between_observations: 7.0
      });
    } else if (preset === 'unrelated') {
      setFeatures({
        same_device_observed: 0,
        contact_overlap_jaccard: 0.05,
        temporal_pattern_similarity: 0.12,
        location_overlap_similarity: 0.08,
        call_pattern_similarity: 0.15,
        shared_case_count: 0,
        days_between_observations: 180.0
      });
    } else if (preset === 'ambiguous') {
      setFeatures({
        same_device_observed: 0,
        contact_overlap_jaccard: 0.45,
        temporal_pattern_similarity: 0.50,
        location_overlap_similarity: 0.40,
        call_pattern_similarity: 0.48,
        shared_case_count: 1,
        days_between_observations: 45.0
      });
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.predictIdentity({
        model_type: modelType,
        pair_id: `SIM-PAIR-${Math.floor(Math.random() * 9000 + 1000)}`,
        features: features
      });
      setPrediction(res);
    } catch (err) {
      alert(`Prediction failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Cpu className="w-6 h-6 text-indigo-400" />
          Identity Resolution Matcher (Burner SIM Detection)
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Predict whether two disparate SIM numbers share the same physical individual identity based on behavioral footprint similarity.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Form Column (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-xl space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-base font-semibold text-white">Candidate Pair Features</h3>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Presets:</span>
              <button 
                type="button" 
                onClick={() => applyPreset('burner')}
                className="px-2 py-1 rounded bg-indigo-500/20 text-indigo-300 text-xs hover:bg-indigo-500/30 font-medium"
              >
                Burner Swap
              </button>
              <button 
                type="button" 
                onClick={() => applyPreset('ambiguous')}
                className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 text-xs hover:bg-amber-500/30 font-medium"
              >
                Borderline
              </button>
              <button 
                type="button" 
                onClick={() => applyPreset('unrelated')}
                className="px-2 py-1 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700 font-medium"
              >
                Unrelated
              </button>
            </div>
          </div>

          <form onSubmit={handlePredict} className="space-y-4">
            {/* Algorithm Selector */}
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-slate-300">Model Classifier</label>
              <div className="flex gap-2">
                {['xgboost', 'random_forest', 'logistic_regression'].map(m => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setModelType(m)}
                    className={`px-3 py-1 rounded text-xs font-medium uppercase ${
                      modelType === m
                        ? 'bg-indigo-600 text-white'
                        : 'bg-dark-800 text-slate-400 hover:bg-dark-700'
                    }`}
                  >
                    {m.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Same Device Observed */}
            <div className="pt-2">
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Same Device Observed (IMEI Link)</span>
                <span className="font-mono text-cyan-400">{features.same_device_observed === 1 ? 'YES (1)' : 'NO (0)'}</span>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => handleSliderChange('same_device_observed', 1)}
                  className={`flex-1 py-1.5 rounded text-xs font-medium border ${
                    features.same_device_observed === 1
                      ? 'bg-indigo-600/30 border-indigo-500 text-indigo-200'
                      : 'bg-dark-800 border-slate-700 text-slate-400'
                  }`}
                >
                  Yes (Same IMEI Tracked)
                </button>
                <button
                  type="button"
                  onClick={() => handleSliderChange('same_device_observed', 0)}
                  className={`flex-1 py-1.5 rounded text-xs font-medium border ${
                    features.same_device_observed === 0
                      ? 'bg-indigo-600/30 border-indigo-500 text-indigo-200'
                      : 'bg-dark-800 border-slate-700 text-slate-400'
                  }`}
                >
                  No (Different Hardware)
                </button>
              </div>
            </div>

            {/* Contact Overlap Jaccard */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Contact Overlap (Jaccard Index)</span>
                <span className="font-mono text-cyan-400">{(features.contact_overlap_jaccard * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={features.contact_overlap_jaccard}
                onChange={e => handleSliderChange('contact_overlap_jaccard', e.target.value)}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Temporal Pattern Similarity */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Temporal Pattern Similarity</span>
                <span className="font-mono text-cyan-400">{(features.temporal_pattern_similarity * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={features.temporal_pattern_similarity}
                onChange={e => handleSliderChange('temporal_pattern_similarity', e.target.value)}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Location Overlap Similarity */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Location Overlap Similarity</span>
                <span className="font-mono text-cyan-400">{(features.location_overlap_similarity * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={features.location_overlap_similarity}
                onChange={e => handleSliderChange('location_overlap_similarity', e.target.value)}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Call Pattern Similarity */}
            <div>
              <div className="flex justify-between text-xs text-slate-300 mb-1">
                <span>Call Duration & Pattern Similarity</span>
                <span className="font-mono text-cyan-400">{(features.call_pattern_similarity * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={features.call_pattern_similarity}
                onChange={e => handleSliderChange('call_pattern_similarity', e.target.value)}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Shared Case Count & Days Between Observations */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-300 mb-1 block">Shared Case Count</label>
                <input
                  type="number"
                  min="0"
                  max="20"
                  value={features.shared_case_count}
                  onChange={e => handleSliderChange('shared_case_count', e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-dark-900 border border-slate-700 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-xs text-slate-300 mb-1 block">Days Between Observations</label>
                <input
                  type="number"
                  min="0"
                  max="365"
                  value={features.days_between_observations}
                  onChange={e => handleSliderChange('days_between_observations', e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg bg-dark-900 border border-slate-700 text-xs text-white"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 font-semibold text-sm text-white shadow-lg shadow-indigo-600/20 transition flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4 fill-white" />
              {loading ? 'Evaluating Model...' : 'Calculate Identity Resolution Probability'}
            </button>
          </form>
        </div>

        {/* Prediction Results Column (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel p-6 rounded-xl space-y-5">
            <h3 className="text-base font-semibold text-white flex items-center justify-between">
              Resolution Output
              {prediction && (
                <span className="text-xs font-mono text-slate-400 uppercase">
                  {prediction.model_type} ({prediction.model_version})
                </span>
              )}
            </h3>

            {prediction ? (
              <div className="space-y-5">
                {/* Probability Card */}
                <div className={`p-4 rounded-xl border text-center ${
                  prediction.prediction_label === 1
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                }`}>
                  <p className="text-xs uppercase font-medium tracking-wider">Estimated Identity Match Probability</p>
                  <p className="text-4xl font-extrabold mt-2 font-mono">
                    {(prediction.probability_same_identity * 100).toFixed(1)}%
                  </p>
                  <div className="mt-3 flex items-center justify-center gap-2 text-sm font-semibold">
                    {prediction.prediction_label === 1 ? (
                      <span className="flex items-center gap-1.5 text-emerald-400">
                        <CheckCircle2 className="w-4 h-4" /> Probable Same Individual (Match)
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-rose-400">
                        <XCircle className="w-4 h-4" /> Distinct Individuals (Non-Match)
                      </span>
                    )}
                  </div>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="h-2 w-full bg-dark-900 rounded-full overflow-hidden border border-slate-700">
                    <div 
                      className={`h-full transition-all duration-500 ${
                        prediction.probability_same_identity >= 0.5 ? 'bg-gradient-to-r from-cyan-400 to-emerald-400' : 'bg-rose-500'
                      }`}
                      style={{ width: `${Math.min(100, prediction.probability_same_identity * 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>0% (Disjoint)</span>
                    <span>Threshold: 50%</span>
                    <span>100% (Identical)</span>
                  </div>
                </div>

                {/* Interpretation */}
                <div className="p-3 rounded-lg bg-dark-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                  <span className="font-semibold text-slate-200">Analytical Rationale: </span>
                  {prediction.interpretation}
                </div>

                {/* Feature Contributions */}
                {prediction.feature_contributions && (
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                      Key Contributing Factors
                    </h4>
                    <div className="space-y-1.5">
                      {Object.entries(prediction.feature_contributions).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between text-xs">
                          <span className="text-slate-400 truncate max-w-[200px]">{k.replace(/_/g, ' ')}</span>
                          <span className="font-mono text-cyan-300 font-medium">{v}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 space-y-2">
                <Cpu className="w-10 h-10 mx-auto text-slate-600 stroke-1" />
                <p className="text-sm">Configure candidate parameters and click "Calculate" to generate resolution scores.</p>
              </div>
            )}

            {/* Disclaimer */}
            <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 leading-tight flex items-start gap-2">
              <Info className="w-4 h-4 flex-shrink-0 text-slate-400 mt-0.5" />
              <span>Statistical pattern estimation from synthetic training data. Must not be used as definitive judicial proof of identity.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
