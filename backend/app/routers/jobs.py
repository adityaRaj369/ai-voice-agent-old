from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.job_parser import parse_job_description
from app.models import Job
from app.schemas import JobCreate
from app.serializers import job_out

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("")
def list_jobs(db: Session = Depends(get_db)):
    return [job_out(j) for j in db.query(Job).order_by(Job.id.desc()).all()]


@router.post("")
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    parsed = parse_job_description(payload.description, payload.title, payload.location)
    job = Job(
        title=payload.title or parsed["title_guess"],
        company=payload.company,
        location=payload.location or parsed.get("location_guess") or "",
        description=payload.description,
        employment_type=payload.employment_type,
        parsed=parsed,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job_out(job)


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return job_out(job)
