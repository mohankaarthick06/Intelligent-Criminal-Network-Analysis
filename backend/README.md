# Backend — Intelligent Criminal Network Analysis

Modular data science backend implemented with **FastAPI**, **Pydantic v2**, **scikit-learn**, **XGBoost**, and **NetworkX**.

---

## Architecture & Directory Structure

```text
backend/
├── app/
│   ├── main.py                  # FastAPI application factory & CORS configuration
│   ├── core/
│   │   ├── config.py            # Centralized settings & path resolution
│   │   ├── exceptions.py        # Domain exception hierarchy & HTTP handlers
│   │   └── logging_config.py    # Structured logging configuration
│   ├── schemas/
│   │   ├── common.py            # Health, readiness, and system schemas
│   │   ├── datasets.py          # Schema inspection and quality report schemas
│   │   ├── identity.py          # Identity resolution requests, metrics, predictions
│   │   ├── anomalies.py         # Isolation Forest schemas and risk scores
│   │   ├── graph.py             # NetworkX node, edge, centrality, link schemas
│   │   └── models.py            # Evaluation summary and artifact models
│   ├── routes/
│   │   ├── health.py            # /health, /ready, /api/v1/system/info
│   │   ├── datasets.py          # Ingestion, validation, and quality endpoints
│   │   ├── identity.py          # Model training, single/batch prediction
│   │   ├── anomalies.py         # Isolation forest training and outlier scoring
│   │   ├── graph.py             # Network graph building, centrality, link analysis
│   │   └── model_evaluation.py  # Model benchmarking and artifact status
│   ├── services/
│   │   ├── data_loader.py       # Safe tabular dataset discovery & previewing
│   │   ├── data_validation.py   # Schema integrity, bounds, duplicates, missingness
│   │   ├── preprocessing.py     # Leak-free scikit-learn transformers
│   │   ├── feature_engineering.py # Similarity vector builders
│   │   ├── identity_resolution.py # XGBoost, Random Forest, Logistic Regression
│   │   ├── anomaly_detection.py # Unsupervised Isolation Forest service
│   │   ├── graph_analytics.py   # NetworkX graph algorithms, Louvain, Jaccard
│   │   └── model_evaluation.py  # Evaluation reporter & model comparator
│   └── repositories/
│       ├── dataset_repository.py # Safe CSV access and caching
│       └── artifact_repository.py# Model serialization (.joblib) & JSON reports
└── tests/
    ├── conftest.py              # TestClient fixtures
    ├── test_unit/               # Isolated unit tests for algorithms & math
    ├── test_api/                # Integration tests for all REST endpoints
    └── test_e2e_workflow.py     # End-to-end full investigative simulation
```

---

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation is available interactively at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 3. Run the Automated Test Suite
```bash
python -m pytest backend/tests -v
```
All 38 unit, API integration, and end-to-end workflow tests execute with zero warnings.
