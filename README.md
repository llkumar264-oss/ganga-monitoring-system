# Ganga Guardian - Smart River Monitoring Platform

A production-quality smart-city environmental monitoring system for river pollution detection and citizen reporting.

## Project Structure

```
ganga monitoring system/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # SQLAlchemy config & session
│   ├── routers/          # API routes
│   │   ├── sensors.py    # Sensor data & hotspots
│   │   ├── complaints.py # Citizen complaints
│   │   └── analytics.py  # Government analytics
│   ├── services/         # Business logic
│   │   ├── pollution_service.py
│   │   └── ai_pollution_service.py
│   ├── models/           # SQLAlchemy models
│   └── schemas/          # Pydantic schemas
├── dashboard/            # Web dashboard
│   ├── index.html
│   ├── app.js
│   └── style.css
├── sensor_simulator/
│   └── simulator.py
└── uploads/              # Complaint media storage
```

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

### 2. Sensor Simulator

```bash
cd sensor_simulator
pip install requests
python simulator.py
```

### 3. Dashboard

Open `dashboard/index.html` in a browser (or serve via any HTTP server).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/sensor-data` | Ingest sensor data (JSON or query params) |
| GET | `/pollution-hotspots` | All sensor readings for map |
| GET | `/heatmap-data` | Heatmap coordinates |
| POST | `/complaint` | Submit complaint with photo |
| GET | `/complaint/list` | List complaints |
| GET | `/complaint/map` | Complaints for map markers |
| GET | `/analytics` | Full analytics for gov panel |
| GET | `/analytics/pollution-zones` | Highest pollution zones |
| GET | `/analytics/complaint-stats` | Complaint statistics |

## Features

- **Live Map**: Pollution hotspots with risk-colored markers; complaint markers
- **Heatmap**: Intensity visualization of pollution
- **Sensor Table**: Real-time sensor readings
- **Citizen Report**: Form to submit pollution complaints with photos
- **Government Panel**: Analytics, charts, highest pollution zones
