"""
Pollution detection and analytics service.
"""
import logging
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from models import SensorData, Complaint

logger = logging.getLogger(__name__)


def get_highest_pollution_zones(db: Session, limit: int = 10) -> List[dict]:
    """Get locations with highest average chemical/turbidity."""
    results = (
        db.query(
            SensorData.location,
            func.avg(SensorData.ph).label("avg_ph"),
            func.avg(SensorData.turbidity).label("avg_turbidity"),
            func.avg(SensorData.chemical).label("avg_chemical"),
            func.max(SensorData.chemical).label("max_chemical"),
            func.count(SensorData.id).label("total"),
        )
        .group_by(SensorData.location)
        .order_by(desc("avg_chemical"))
        .limit(limit)
        .all()
    )

    zones = []
    for r in results:
        risk_count = (
            db.query(SensorData)
            .filter(SensorData.location == r.location)
            .filter(SensorData.risk_level.in_(["HIGH", "CRITICAL"]))
            .count()
        )
        zones.append(
            {
                "location": r.location,
                "avg_ph": round(float(r.avg_ph or 0), 2),
                "avg_turbidity": round(float(r.avg_turbidity or 0), 2),
                "avg_chemical": round(float(r.avg_chemical or 0), 2),
                "max_chemical": round(float(r.max_chemical or 0), 2),
                "risk_count": risk_count,
                "total_readings": r.total,
            }
        )
    return zones


def get_complaint_statistics(db: Session) -> dict:
    """Get complaint counts by status and optionally by month."""
    total = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == "pending").count()
    in_review = db.query(Complaint).filter(Complaint.status == "in_review").count()
    resolved = db.query(Complaint).filter(Complaint.status == "resolved").count()
    return {
        "total": total,
        "pending": pending,
        "in_review": in_review,
        "resolved": resolved,
    }
