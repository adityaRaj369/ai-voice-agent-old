from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import hunar_client
from app.call_sync import TERMINAL_STATUSES, apply_hunar_call_payload
from app.db import get_db
from app.models import Candidate, Job, VoiceAgent, VoiceCall
from app.schemas import CallCreate
from app.serializers import call_out

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.get("")
def list_calls(purpose: str | None = None, db: Session = Depends(get_db)):
    q = db.query(VoiceCall).options(joinedload(VoiceCall.candidate), joinedload(VoiceCall.agent)).order_by(VoiceCall.id.desc())
    if purpose:
        q = q.filter(VoiceCall.purpose == purpose)
    return [call_out(c) for c in q.all()]


@router.post("/sync-open")
async def sync_open_calls(purpose: str | None = None, db: Session = Depends(get_db)):
    """Pull latest Hunar status for all non-finished calls."""
    q = db.query(VoiceCall).options(joinedload(VoiceCall.candidate), joinedload(VoiceCall.agent))
    if purpose:
        q = q.filter(VoiceCall.purpose == purpose)
    open_calls = [c for c in q.order_by(VoiceCall.id.desc()).all() if str(c.status).upper() not in TERMINAL_STATUSES]
    synced = []
    for call in open_calls[:20]:
        if not call.hunar_call_id:
            continue
        try:
            remote = await hunar_client.get_call(call.hunar_call_id)
            updated = apply_hunar_call_payload(db, remote)
            if updated:
                db.refresh(updated)
                synced.append(call_out(updated))
        except Exception:
            continue
    return {"synced": len(synced), "calls": synced}


@router.post("")
async def place_call(payload: CallCreate, db: Session = Depends(get_db)):
    agent = db.query(VoiceAgent).filter(VoiceAgent.id == payload.agent_id).first()
    if not agent or not agent.hunar_agent_id:
        raise HTTPException(400, "Voice agent is missing a Hunar agent id. Create the agent first.")
    job = db.query(Job).filter(Job.id == payload.job_id).first() if payload.job_id else None
    custom = {
        "candidate_name": payload.callee_name,
        "job_role": job.title if job else payload.purpose,
        "company": job.company if job else "Hiring team",
        "location": job.location if job else "",
        **payload.custom_data,
    }
    remote_body = {
        "agent_id": agent.hunar_agent_id,
        "callee_name": payload.callee_name,
        "mobile_number": payload.mobile_number,
        "timezone": payload.timezone,
        "custom_data": {k: str(v) for k, v in custom.items() if v is not None},
        "retry_config": hunar_client.default_retry_config(),
        "guardrails": {
            "allowed_days": ["MON", "TUE", "WED", "THU", "FRI", "SAT"],
            "earliest_call_time": "09:00",
            "last_call_time": "20:00",
        },
    }
    callbacks = hunar_client.callback_config()
    if callbacks:
        remote_body["callback_config"] = callbacks
    if payload.from_phone_number:
        remote_body["from_phone_number"] = payload.from_phone_number
    remote = await hunar_client.create_call(remote_body)
    row = VoiceCall(
        hunar_call_id=str(remote.get("id") or ""),
        request_id=str(remote.get("request_id") or ""),
        agent_id=agent.id,
        candidate_id=payload.candidate_id,
        job_id=payload.job_id,
        campaign_id=payload.campaign_id,
        worker_id=payload.worker_id,
        purpose=payload.purpose,
        callee_name=payload.callee_name,
        mobile_number=payload.mobile_number,
        status=str(remote.get("status") or "NOT_STARTED"),
        custom_data=custom,
        raw=remote,
    )
    db.add(row)
    if payload.candidate_id:
        cand = db.query(Candidate).filter(Candidate.id == payload.candidate_id).first()
        if cand:
            cand.status = "calling"
    db.commit()
    db.refresh(row)
    return call_out(row)


@router.get("/{call_id}")
async def get_call(call_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(VoiceCall)
        .options(joinedload(VoiceCall.candidate), joinedload(VoiceCall.agent))
        .filter(VoiceCall.id == call_id)
        .first()
    )
    if not row:
        raise HTTPException(404, "Call not found")
    if row.hunar_call_id:
        remote = await hunar_client.get_call(row.hunar_call_id)
        apply_hunar_call_payload(db, remote)
        db.refresh(row)
    return call_out(row)


@router.post("/{call_id}/refresh")
async def refresh_call(call_id: int, db: Session = Depends(get_db)):
    return await get_call(call_id, db)
