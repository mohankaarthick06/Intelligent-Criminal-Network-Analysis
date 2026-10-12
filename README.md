# Intelligent Criminal Network Analysis

An end-to-end, modular, locally executable data science application for analyzing synthetic Call Detail Records (CDRs), device histories, communication topologies, and behavioral patterns.

---

## Key Capabilities

1. **Identity Resolution**: Binary classification using **XGBoost**, **Random Forest**, and **Logistic Regression** to detect shared identities (burner phone handoffs) from behavioral footprints with probability calibration and feature contribution explanations.
2. **Behavioral Anomaly Detection**: Unsupervised **Isolation Forest** isolating atypical subscriber communication volumes, high night-time activity, contact churn, and cell tower movements.
3. **Graph Analytics & Network Mapping**: **NetworkX** telecom graph construction with **Louvain community detection**, degree/betweenness centrality, and topological link prediction (Common Neighbors, Jaccard, Adamic-Adar).
4. **Interactive Analytical Dashboard**: Dark cyber-themed React application with **Cytoscape.js** for interactive network exploration and **Recharts** for metric visualization.
5. **Quality Assurance & Verification**: 38 automated unit, API integration, and end-to-end workflow tests achieving 100% pass rate.

---

## Technology Stack

- **Backend**: Python 3.13 / 3.11, FastAPI, Pydantic v2, Pandas, NumPy, scikit-learn, XGBoost, NetworkX, Uvicorn, Pytest, HTTPX.
- **Frontend**: React 18, Vite 5, Tailwind CSS, Cytoscape.js, Recharts, Lucide React.
- **Storage**: Clean file-based architecture (`data/raw`, `data/processed`, `models`, `reports`).

---

## Quick Start Guide

### 1. Backend Setup & Startup

From the project root:
```bash
# Install backend dependencies
pip install -r requirements.txt

# Run all automated tests
python -m pytest backend/tests -v

# Launch the FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API and interactive documentation will be live at:
- **API Docs (Swagger)**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

### 2. Frontend Setup & Startup

Open a second terminal window in the project root:
```bash
# Navigate to frontend and install packages
cd frontend
npm install

# Start the Vite development server
npm run dev
```
Open your browser at:
- **Interactive Dashboard**: `http://localhost:5173`

---

## Data Dictionary & Synthetic Disclaimers

> [!IMPORTANT]
> **Synthetic Demonstration Data**: All records, mobile numbers (+91), IMEIs, case IDs, and coordinate assignments are synthetic. Model estimations serve as statistical hypothesis generators for prototyping and do not establish legal proof of identity or criminal culpability.

### Primary Datasets (`data/raw/`):
- **`cdr.csv`** (5,000 events): Caller/receiver person IDs, phone numbers, timestamps, call durations, call types (voice/sms), caller IMEIs, and cell tower city locations.
- **`phone_device_history.csv`** (348 records): Person ID to IMEI mappings, validity timeframes, and hardware replacement reasons.
- **`imei_summary.csv`** (204 devices): Device-level aggregations (total events, distinct phone numbers, distinct cells).
- **`identity_resolution_pairs.csv`** (1,530 pairs): Contact overlap Jaccard, temporal similarity, location similarity, call pattern similarity, and `same_identity_label` (Class 0: 96.86%, Class 1: 3.14%).
- **`behavior_anomaly_features.csv`** (2,000 entities): Calls per day, unique contacts, night call ratio, average duration, contact change ratio, and new cell counts.
- **`synthetic_location_reference.csv`** (10 cities): Central latitude and longitude coordinates for reference cities.

---

## Test Verification Summary

- **Total Test Cases**: 38
- **Passed**: 38 (100%)
- **Failed**: 0
- **Warnings**: 0
- **Execution Time**: ~6.1 seconds
- **Test Command**: `python -m pytest backend/tests -v`
