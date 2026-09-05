from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import hunar_client
from app.db import get_db
from app.models import AttendanceEvent, Site, VoiceAgent, VoiceCall, Worker
from app.schemas import AttendanceMark, AttendanceVoice
from app.serializers import event_out, site_out, worker_out, call_out

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.get("/sites")
def list_sites(db: Session = Depends(get_db)):
    today = datetime.combine(date.today(), datetime.min.time())
    sites = db.query(Site).order_by(Site.id).all()
    out = []
    for site in sites:
        headcount = db.query(func.count(Worker.id)).filter(Worker.site_id == site.id).scalar() or 0
        present = (
            db.query(func.count(AttendanceEvent.id))
            .filter(
                AttendanceEvent.site_id == site.id,
                AttendanceEvent.created_at >= today,
                AttendanceEvent.status.in_(["present", "late"]),
            )
            .scalar()
            or 0
        )
        out.append(site_out(site, present=present, headcount=headcount))
    return out


@router.get("/sites/{site_id}")
def get_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(404, "Site not found")
    workers = db.query(Worker).filter(Worker.site_id == site_id).all()
    events = (
        db.query(AttendanceEvent)
        .options(joinedload(AttendanceEvent.worker))
        .filter(AttendanceEvent.site_id == site_id)
        .order_by(AttendanceEvent.id.desc())
        .limit(50)
        .all()
    )
    return {
        **site_out(site, present=None, headcount=len(workers)),
        "workers": [worker_out(w) for w in workers],
        "recent_events": [event_out(e) for e in events],
    }


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    today = datetime.combine(date.today(), datetime.min.time())
    workers = db.query(func.count(Worker.id)).scalar() or 0
    sites = db.query(func.count(Site.id)).scalar() or 0
    marked = (
        db.query(func.count(AttendanceEvent.id)).filter(AttendanceEvent.created_at >= today).scalar() or 0
    )
    present = (
        db.query(func.count(AttendanceEvent.id))
        .filter(AttendanceEvent.created_at >= today, AttendanceEvent.status.in_(["present", "late"]))
        .scalar()
        or 0
    )
    by_method = (
        db.query(AttendanceEvent.method, func.count(AttendanceEvent.id))
        .filter(AttendanceEvent.created_at >= today)
        .group_by(AttendanceEvent.method)
        .all()
    )
    return {
        "sites": sites,
        "workers": workers,
        "marked_today": marked,
        "present_today": present,
        "missing_today": max(workers - present, 0),
        "by_method": {k: v for k, v in by_method},
    }


@router.post("/mark")
def mark(payload: AttendanceMark, db: Session = Depends(get_db)):
    worker = None
    if payload.worker_id:
        worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    elif payload.employee_code:
        worker = db.query(Worker).filter(Worker.employee_code == payload.employee_code).first()
    if not worker:
        raise HTTPException(404, "Worker not found")
    if payload.spoken_pin and payload.spoken_pin != worker.spoken_pin:
        raise HTTPException(401, "Spoken PIN did not match. Supervisor confirmation required.")
    event = AttendanceEvent(
        worker_id=worker.id,
        site_id=worker.site_id,
        method=payload.method,
        status=payload.status,
        notes=payload.notes,
        hunar_call_id=payload.hunar_call_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event_out(event)


@router.post("/voice-checkin")
async def voice_checkin(payload: AttendanceVoice, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if not worker:
        raise HTTPException(404, "Worker not found")
    agent = None
    if payload.agent_id:
        agent = db.query(VoiceAgent).filter(VoiceAgent.id == payload.agent_id).first()
    if not agent:
        agent = db.query(VoiceAgent).filter(VoiceAgent.kind == "attendance").first()
    if not agent or not agent.hunar_agent_id:
        raise HTTPException(400, "Create the attendance Voice AI agent first.")
    number = payload.mobile_number or worker.site.landline
    custom = {
        "candidate_name": worker.name,
        "job_role": worker.shift,
        "company": "Attendance desk",
        "location": worker.site.code,
        "employee_code": worker.employee_code,
        "spoken_pin": worker.spoken_pin,
    }
    remote_body = {
        "agent_id": agent.hunar_agent_id,
        "callee_name": worker.name,
        "mobile_number": number,
        "timezone": "Asia/Kolkata",
        "custom_data": custom,
        "retry_config": hunar_client.default_retry_config(),
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
        worker_id=worker.id,
        purpose="attendance",
        callee_name=worker.name,
        mobile_number=number,
        status=str(remote.get("status") or "NOT_STARTED"),
        custom_data=custom,
        raw=remote,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return call_out(row)
