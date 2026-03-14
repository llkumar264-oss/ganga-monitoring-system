"""
Sensor data API routes.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import SensorData
from schemas import (
    SensorDataCreate,
    SensorDataIngestResponse,
    HotspotPoint,
)
from services.ai_pollution_service import analyze_pollution

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sensors"])


async def _parse_sensor_payload(request: Request) -> SensorDataCreate:
    """Parse sensor data from JSON body or query params (simulator compatibility)."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            return SensorDataCreate(**body)
        except Exception as e:
            raise HTTPException(422, f"Invalid JSON body: {e}")
    # Query params (simulator sends params=...)
    query = request.query_params
    return SensorDataCreate(
        location=query.get("location", "Unknown"),
        ph=float(query.get("ph", 7)),
        turbidity=float(query.get("turbidity", 0)),
        chemical=float(query.get("chemical", 0)),
        lat=float(query.get("lat", 0)),
        lon=float(query.get("lon", 0)),
    )


@router.post("/sensor-data", response_model=SensorDataIngestResponse)
async def ingest_sensor_data(
    request: Request,
    db: Session = Depends(get_db),
):
    """Ingest sensor reading. Accepts JSON body or query params."""
    payload = await _parse_sensor_payload(request)
    analysis = analyze_pollution(
        ph=payload.ph,
        turbidity=payload.turbidity,
        chemical=payload.chemical,
    )
    record = SensorData(
        location=payload.location,
        ph=payload.ph,
        turbidity=payload.turbidity,
        chemical=payload.chemical,
        latitude=payload.lat,
        longitude=payload.lon,
        status=analysis.message,
        risk_level=analysis.risk_level,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(f"Sensor data ingested: {payload.location} - {analysis.risk_level}")
    return SensorDataIngestResponse(
        status=analysis.message,
        location=payload.location,
        risk_level=analysis.risk_level,
        suggestion=analysis.suggestion,
    )


@router.get("/heatmap-data")
def get_heatmap_data(db: Session = Depends(get_db)):
    """Get sensor data as [lat, lng, intensity] for heatmap. Intensity 0-1 based on risk."""
    rows = db.query(SensorData).order_by(SensorData.id.desc()).all()
    levels = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.8, "CRITICAL": 1.0}
    return [
        [r.latitude, r.longitude, levels.get(r.risk_level or "LOW", 0.2)]
        for r in rows
    ]


@router.get("/pollution-hotspots", response_model=List[HotspotPoint])
@router.get("/sensor-data/hotspots", response_model=List[HotspotPoint])
def get_pollution_hotspots(db: Session = Depends(get_db)):
    """Get all sensor readings for map display."""
    rows = db.query(SensorData).order_by(SensorData.id.desc()).all()
    return [
        HotspotPoint(
            id=r.id,
            location=r.location,
            ph=r.ph,
            turbidity=r.turbidity,
            chemical=r.chemical,
            lat=r.latitude,
            lon=r.longitude,
            status=r.status or "",
            risk_level=r.risk_level,
        )
        for r in rows
    ]
