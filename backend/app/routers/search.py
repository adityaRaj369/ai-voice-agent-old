from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.job_parser import parse_job_description
from app.models import Candidate, Job
from app.people_search import search_people
from app.schemas import SearchRequest
from app.serializers import candidate_out

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("")
async def search(payload: SearchRequest, db: Session = Depends(get_db)):
    description = payload.description
    title = payload.title
    location = payload.location
    job = None
    if payload.job_id:
        job = db.query(Job).filter(Job.id == payload.job_id).first()
        if job:
            description = description or job.description
            title = title or job.title
            location = location or job.location
    parsed = parse_job_description(description, title, location)
    people = await search_people(parsed, provider=payload.provider, limit=payload.limit)
    saved = []
    if payload.save_to_job and job:
        for person in people:
            existing = (
                db.query(Candidate)
                .filter(Candidate.job_id == job.id, Candidate.full_name == person["full_name"])
                .first()
            )
            if existing:
                saved.append(candidate_out(existing))
                continue
            row = Candidate(
                job_id=job.id,
                full_name=person["full_name"],
                phone=person.get("phone") or "",
                email=person.get("email") or "",
                headline=person.get("headline") or "",
                location=person.get("location") or "",
                skills=person.get("skills") or [],
                source=person.get("source") or "demo",
                profile_url=person.get("profile_url") or "",
                raw=person.get("raw") or person,
                status="sourced",
                score=float(person.get("score") or 0),
            )
            db.add(row)
            db.flush()
            saved.append(candidate_out(row))
        db.commit()
    return {"parsed": parsed, "provider_used": people[0]["source"] if people else "demo", "people": people, "saved": saved}
