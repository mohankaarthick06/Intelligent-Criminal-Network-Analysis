# Frontend — Intelligent Criminal Network Analysis

Responsive, dark-themed analytical dashboard built with **React**, **Vite**, **Tailwind CSS**, **Cytoscape.js**, and **Recharts**.

---

## Architecture & Pages

- **Page 1: Overview (`Overview.jsx`)**: System KPIs (Datasets, Graph Nodes, Behavioral Outliers, Model Status), quick navigation cards, and synthetic data disclaimers.
- **Page 2: Dataset Explorer (`DatasetExplorer.jsx`)**: Dataset switcher, schema column inspector with null/unique counts, automated Data Quality Report with integrity scores (0-100), and search/paginated data preview.
- **Page 3: Identity Resolution (`IdentityResolution.jsx`)**: Interactive candidate pair feature simulator (contact overlap, temporal similarity, location overlap, call patterns, shared cases), XGBoost/Random Forest/Logistic Regression selector, match probability progress bar, decision explanations, and batch scoring.
- **Page 4: Network Explorer (`NetworkExplorer.jsx`)**: Cytoscape.js interactive communication network canvas with Louvain community coloring, node degree sizing, zoom/pan controls, edge inspection, and pairwise Link Analysis (Common Neighbors, Jaccard similarity, Adamic-Adar, Shortest Path).
- **Page 5: Behavioral Anomalies (`AnomalyAnalysis.jsx`)**: Unsupervised Isolation Forest detection results, normal vs. anomalous subscriber comparison charts (Recharts), custom subscriber simulator, and ranked outliers leaderboard with risk badges.
- **Page 6: Model Evaluation (`ModelEvaluation.jsx`)**: Genuine held-out test set comparative benchmark of Logistic Regression, Random Forest, and XGBoost with PR-AUC, ROC-AUC, F1-Score, Brier score, and Confusion Matrices.

---

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The application runs locally at `http://localhost:5173`. API requests are proxied automatically to the backend running at `http://127.0.0.1:8000`.

### 3. Production Build
```bash
npm run build
```
Generates a verified, minified production bundle in `dist/`.
