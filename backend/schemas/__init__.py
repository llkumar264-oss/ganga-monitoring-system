"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Sensor Data ---
class SensorDataCreate(BaseModel):
    location: str = Field(..., min_length=1, max_length=255)
    ph: float = Field(..., ge=0, le=14)
    turbidity: float = Field(..., ge=0)
    chemical: float = Field(..., ge=0)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class SensorDataResponse(BaseModel):
    id: int
    location: str
    ph: float
    turbidity: float
    chemical: float
    lat: float
    lon: float
    status: Optional[str]
    risk_level: Optional[str]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorDataIngestResponse(BaseModel):
    status: str
    location: str
    risk_level: str
    suggestion: Optional[str] = None


# --- Complaint ---
class ComplaintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class ComplaintResponse(BaseModel):
    id: int
    name: str
    description: str
    latitude: float
    longitude: float
    media: Optional[str]
    status: Optional[str] = "pending"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Hotspots & Map ---
class HotspotPoint(BaseModel):
    id: int
    location: str
    ph: float
    turbidity: float
    chemical: float
    lat: float
    lon: float
    status: str
    risk_level: Optional[str]


class ComplaintPoint(BaseModel):
    id: int
    name: str
    description: str
    lat: float
    lon: float
    status: str
    created_at: Optional[datetime] = None


# --- Analytics ---
class PollutionZoneStats(BaseModel):
    location: str
    avg_ph: float
    avg_turbidity: float
    avg_chemical: float
    max_chemical: float
    risk_count: int
    total_readings: int


class ComplaintStats(BaseModel):
    total: int
    pending: int
    in_review: int
    resolved: int
    by_month: Optional[dict] = None


class AnalyticsResponse(BaseModel):
    pollution_zones: List[PollutionZoneStats]
    complaint_stats: ComplaintStats
    latest_sensors: List[SensorDataResponse]
