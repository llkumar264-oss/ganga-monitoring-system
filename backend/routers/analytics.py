"""
Analytics and government monitoring API routes.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import SensorData
from schemas import (
    PollutionZoneStats,
    ComplaintStats,
    SensorDataResponse,
)
from services.pollution_service import get_highest_pollution_zones, get_complaint_statistics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _sensor_to_response(s: SensorData) -> SensorDataResponse:
    return SensorDataResponse(
        id=s.id,
        location=s.location,
        ph=s.ph,
        turbidity=s.turbidity,
        chemical=s.chemical,
        lat=s.latitude,
        lon=s.longitude,
        status=s.status,
        risk_level=s.risk_level,
        created_at=s.created_at,
    )


@router.get("")
def get_analytics(db: Session = Depends(get_db)):
    """Full analytics for government monitoring panel."""
    zones = get_highest_pollution_zones(db, limit=10)
    complaint_stats = get_complaint_statistics(db)
    latest = db.query(SensorData).order_by(SensorData.id.desc()).limit(20).all()
    return {
        "pollution_zones": zones,
        "complaint_stats": complaint_stats,
        "latest_sensors": [_sensor_to_response(s) for s in latest],
    }


@router.get("/pollution-zones", response_model=List[PollutionZoneStats])
def get_pollution_zones(db: Session = Depends(get_db), limit: int = 10):
    """Highest pollution zones for charts."""
    return get_highest_pollution_zones(db, limit=limit)


@router.get("/complaint-stats", response_model=ComplaintStats)
def get_complaint_analytics(db: Session = Depends(get_db)):
    """Complaint statistics for charts."""
    return get_complaint_statistics(db)
