from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Candidate, VoiceCall
from app.serializers import call_out, candidate_out

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db)):
    calls = (
        db.query(VoiceCall)
        .options(joinedload(VoiceCall.candidate), joinedload(VoiceCall.agent))
        .order_by(VoiceCall.id.desc())
        .limit(50)
        .all()
    )
    answers = []
    for call in calls:
        if call.result:
            answers.append(
                {
                    "call_id": call.id,
                    "purpose": call.purpose,
                    "person": call.callee_name,
                    "status": call.status,
                    "answers": call.result,
                    "recording_url": call.recording_url,
                }
            )
    pipeline = {}
    for cand in db.query(Candidate).all():
        pipeline[cand.status] = pipeline.get(cand.status, 0) + 1
    return {
        "pipeline": pipeline,
        "recent_calls": [call_out(c) for c in calls],
        "structured_answers": answers,
        "candidates": [candidate_out(c) for c in db.query(Candidate).order_by(Candidate.id.desc()).limit(20)],
    }
