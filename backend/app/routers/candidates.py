from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate
from app.schemas import CandidateCreate
from app.serializers import candidate_out

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("")
def list_candidates(job_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Candidate).order_by(Candidate.id.desc())
    if job_id:
        q = q.filter(Candidate.job_id == job_id)
    return [candidate_out(c) for c in q.all()]


@router.post("")
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)):
    row = Candidate(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return candidate_out(row)


@router.patch("/{candidate_id}")
def update_candidate(candidate_id: int, status: str, db: Session = Depends(get_db)):
    row = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not row:
        raise HTTPException(404, "Candidate not found")
    row.status = status
    db.commit()
    db.refresh(row)
    return candidate_out(row)
