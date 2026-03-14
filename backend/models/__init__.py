"""
SQLAlchemy models for Ganga Guardian.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Text
from database import Base


class SensorData(Base):
    """Sensor reading from a monitoring station."""

    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(255), nullable=False, index=True)
    ph = Column(Float, nullable=False)
    turbidity = Column(Float, nullable=False)
    chemical = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(500), nullable=True)
    risk_level = Column(String(50), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_sensor_location_created", "location", "created_at"),
        Index("ix_sensor_risk_created", "risk_level", "created_at"),
    )


class Complaint(Base):
    """Citizen-reported pollution complaint with media."""

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    media = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")  # pending, in_review, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_complaint_location", "latitude", "longitude"),
        Index("ix_complaint_created", "created_at"),
    )
