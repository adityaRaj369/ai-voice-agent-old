from typing import Any

from app.models import AttendanceEvent, Candidate, Job, OutreachCampaign, OutreachMessage, Site, VoiceAgent, VoiceCall, Worker


def job_out(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "employment_type": job.employment_type,
        "parsed": job.parsed,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def candidate_out(c: Candidate) -> dict[str, Any]:
    return {
        "id": c.id,
        "job_id": c.job_id,
        "full_name": c.full_name,
        "phone": c.phone,
        "email": c.email,
        "headline": c.headline,
        "location": c.location,
        "skills": c.skills,
        "source": c.source,
        "profile_url": c.profile_url,
        "status": c.status,
        "score": c.score,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def agent_out(a: VoiceAgent) -> dict[str, Any]:
    return {
        "id": a.id,
        "hunar_agent_id": a.hunar_agent_id,
        "name": a.name,
        "kind": a.kind,
        "language": a.language,
        "voice_persona": a.voice_persona,
        "objective": a.objective,
        "result_schema": a.result_schema,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def call_out(call: VoiceCall) -> dict[str, Any]:
    return {
        "id": call.id,
        "hunar_call_id": call.hunar_call_id,
        "request_id": call.request_id,
        "agent_id": call.agent_id,
        "candidate_id": call.candidate_id,
        "job_id": call.job_id,
        "campaign_id": call.campaign_id,
        "worker_id": call.worker_id,
        "purpose": call.purpose,
        "callee_name": call.callee_name,
        "mobile_number": call.mobile_number,
        "status": call.status,
        "result": call.result,
        "recording_url": call.recording_url,
        "custom_data": call.custom_data,
        "created_at": call.created_at.isoformat() if call.created_at else None,
        "updated_at": call.updated_at.isoformat() if call.updated_at else None,
        "candidate": candidate_out(call.candidate) if call.candidate else None,
        "agent": agent_out(call.agent) if call.agent else None,
    }


def campaign_out(c: OutreachCampaign) -> dict[str, Any]:
    return {
        "id": c.id,
        "job_id": c.job_id,
        "name": c.name,
        "agent_id": c.agent_id,
        "channels": c.channels,
        "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "call_count": len(c.calls or []),
        "message_count": len(c.messages or []),
    }


def message_out(m: OutreachMessage) -> dict[str, Any]:
    return {
        "id": m.id,
        "campaign_id": m.campaign_id,
        "candidate_id": m.candidate_id,
        "channel": m.channel,
        "body": m.body,
        "status": m.status,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


def site_out(s: Site, present: int | None = None, headcount: int | None = None) -> dict[str, Any]:
    return {
        "id": s.id,
        "code": s.code,
        "name": s.name,
        "city": s.city,
        "landline": s.landline,
        "supervisor_name": s.supervisor_name,
        "supervisor_phone": s.supervisor_phone,
        "present": present,
        "headcount": headcount,
    }


def worker_out(w: Worker) -> dict[str, Any]:
    return {
        "id": w.id,
        "employee_code": w.employee_code,
        "name": w.name,
        "site_id": w.site_id,
        "shift": w.shift,
        "spoken_pin": w.spoken_pin,
        "rfid": w.rfid,
        "site": site_out(w.site) if w.site else None,
    }


def event_out(e: AttendanceEvent) -> dict[str, Any]:
    return {
        "id": e.id,
        "worker_id": e.worker_id,
        "site_id": e.site_id,
        "method": e.method,
        "status": e.status,
        "notes": e.notes,
        "hunar_call_id": e.hunar_call_id,
        "created_at": e.created_at.isoformat() if e.created_at else None,
        "worker": worker_out(e.worker) if e.worker else None,
        "site": site_out(e.site) if e.site else None,
    }
