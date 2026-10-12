const API_BASE = '/api/v1';

async function request(endpoint, options = {}) {
  try {
    const res = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    if (!res.ok) {
      let errDetail = 'Request failed';
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
      } catch (e) {
        errDetail = `HTTP ${res.status}: ${res.statusText}`;
      }
      throw new Error(errDetail);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on [${options.method || 'GET'}] ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Health & System
  getHealth: () => request('/health'),
  getReady: () => request('/ready'),
  getSystemInfo: () => request(`${API_BASE}/system/info`),

  // Datasets
  getDatasets: () => request(`${API_BASE}/datasets`),
  getDatasetSummary: (name) => request(`${API_BASE}/datasets/${name}/summary`),
  validateDataset: (name) => request(`${API_BASE}/datasets/${name}/validate`, { method: 'POST' }),
  getQualityReport: (name) => request(`${API_BASE}/datasets/${name}/quality`),

  // Identity Resolution
  getIdentityModels: () => request(`${API_BASE}/identity/models`),
  trainIdentityModel: (params) => request(`${API_BASE}/identity/train`, {
    method: 'POST',
    body: JSON.stringify(params)
  }),
  predictIdentity: (payload) => request(`${API_BASE}/identity/predict`, {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  batchPredictIdentity: (payload) => request(`${API_BASE}/identity/predict/batch`, {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getIdentityEvaluation: (modelType = 'xgboost') => request(`${API_BASE}/identity/evaluation?model_type=${modelType}`),

  // Anomaly Detection
  trainAnomalyModel: (params) => request(`${API_BASE}/anomalies/train`, {
    method: 'POST',
    body: JSON.stringify(params)
  }),
  detectAnomalies: (items) => request(`${API_BASE}/anomalies/detect`, {
    method: 'POST',
    body: JSON.stringify({ items })
  }),
  getAnomalySummary: () => request(`${API_BASE}/anomalies/summary`),
  getAnomalyEvaluation: () => request(`${API_BASE}/anomalies/evaluation`),

  // Graph Analytics
  buildGraph: (params) => request(`${API_BASE}/graph/build`, {
    method: 'POST',
    body: JSON.stringify(params)
  }),
  getGraphSummary: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`${API_BASE}/graph/summary?${qs}`);
  },
  getGraphNodes: (limit = 100, offset = 0) => request(`${API_BASE}/graph/nodes?limit=${limit}&offset=${offset}`),
  getGraphEdges: (limit = 100, offset = 0) => request(`${API_BASE}/graph/edges?limit=${limit}&offset=${offset}`),
  getGraphCommunities: () => request(`${API_BASE}/graph/communities`),
  getGraphCentrality: (alg = 'degree', topK = 10) => request(`${API_BASE}/graph/centrality?algorithm=${alg}&top_k=${topK}`),
  analyzeLink: (source_node, target_node) => request(`${API_BASE}/graph/link-analysis`, {
    method: 'POST',
    body: JSON.stringify({ source_node, target_node })
  }),

  // Evaluation & Artifacts
  getEvaluationSummary: () => request(`${API_BASE}/evaluation/summary`),
  getArtifactStatus: () => request(`${API_BASE}/artifacts/status`)
};
