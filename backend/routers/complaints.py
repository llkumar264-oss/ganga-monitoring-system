"""
Complaint reporting API routes.
"""
import logging
import os
import shutil
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from models import Complaint
from schemas import ComplaintResponse, ComplaintPoint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/complaint", tags=["Complaints"])
UPLOAD_FOLDER = "uploads"


def _ensure_upload_dir():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("", status_code=201)
def submit_complaint(
    name: str = Form(...),
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Submit a citizen complaint with media attachment."""
    _ensure_upload_dir()
    ext = os.path.splitext(file.filename or "img.jpg")[1]
    safe_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, safe_name)
    try:
        with open(filepath, "wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save upload")
    comp = Complaint(
        name=name,
        description=description,
        latitude=lat,
        longitude=lon,
        media=filepath,
        status="pending",
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    logger.info(f"Complaint submitted: {comp.id} by {name}")
    return {
        "status": "Complaint registered successfully",
        "id": comp.id,
        "name": name,
        "location": {"lat": lat, "lon": lon},
        "file_saved": filepath,
    }


@router.get("/list", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)):
    """List all complaints."""
    return db.query(Complaint).order_by(Complaint.id.desc()).all()


@router.get("/map", response_model=List[ComplaintPoint])
def get_complaint_map_points(db: Session = Depends(get_db)):
    """Get complaints as map points for dashboard."""
    rows = db.query(Complaint).all()
    return [
        ComplaintPoint(
            id=r.id,
            name=r.name,
            description=r.description,
            lat=r.latitude,
            lon=r.longitude,
            status=r.status or "pending",
            created_at=r.created_at,
        )
        for r in rows
    ]
