from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import hunar_client
from app.db import get_db
from app.messaging import build_email_body, build_whatsapp_body, deliver_channel, queue_message
from app.models import Candidate, Job, OutreachCampaign, VoiceAgent, VoiceCall
from app.schemas import OutreachLaunch
from app.serializers import campaign_out, call_out, message_out

router = APIRouter(prefix="/api/outreach", tags=["outreach"])


@router.get("")
def list_campaigns(db: Session = Depends(get_db)):
    rows = db.query(OutreachCampaign).options(joinedload(OutreachCampaign.calls), joinedload(OutreachCampaign.messages)).all()
    return [campaign_out(c) for c in rows]


@router.get("/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(OutreachCampaign)
        .options(joinedload(OutreachCampaign.calls).joinedload(VoiceCall.candidate), joinedload(OutreachCampaign.messages))
        .filter(OutreachCampaign.id == campaign_id)
        .first()
    )
    if not row:
        raise HTTPException(404, "Campaign not found")
    return {
        **campaign_out(row),
        "calls": [call_out(c) for c in row.calls],
        "messages": [message_out(m) for m in row.messages],
    }


@router.post("/launch")
async def launch(payload: OutreachLaunch, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    agent = None
    if payload.agent_id:
        agent = db.query(VoiceAgent).filter(VoiceAgent.id == payload.agent_id).first()
    if not agent:
        agent = db.query(VoiceAgent).filter(VoiceAgent.kind == "outreach").first()
    if "voice" in payload.channels and (not agent or not agent.hunar_agent_id):
        raise HTTPException(400, "Create a Hunar outreach agent before launching voice reachout.")
    candidates = db.query(Candidate).filter(Candidate.id.in_(payload.candidate_ids)).all()
    if not candidates:
        raise HTTPException(400, "No candidates selected")
    campaign = OutreachCampaign(
        job_id=job.id,
        name=f"{job.title} reachout",
        agent_id=agent.id if agent else None,
        channels=payload.channels,
        status="running",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    calls = []
    for cand in candidates:
        cand.status = "contacted"
        if "whatsapp" in payload.channels and cand.phone:
            body = build_whatsapp_body(cand.full_name, job.title, job.company, job.location)
            status = deliver_channel("whatsapp", cand.phone, cand.email, body)
            queue_message(db, campaign.id, cand.id, "whatsapp", body, status)
        if "email" in payload.channels and cand.email:
            body = build_email_body(cand.full_name, job.title, job.company)
            status = deliver_channel("email", cand.phone, cand.email, body)
            queue_message(db, campaign.id, cand.id, "email", body, status)
        if "voice" in payload.channels and cand.phone and agent:
            custom = {
                "candidate_name": cand.full_name,
                "job_role": job.title,
                "company": job.company,
                "location": job.location or "",
            }
            remote_body = {
                "agent_id": agent.hunar_agent_id,
                "callee_name": cand.full_name,
                "mobile_number": cand.phone,
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
                candidate_id=cand.id,
                job_id=job.id,
                campaign_id=campaign.id,
                purpose="outreach",
                callee_name=cand.full_name,
                mobile_number=cand.phone,
                status=str(remote.get("status") or "NOT_STARTED"),
                custom_data=custom,
                raw=remote,
            )
            db.add(row)
            db.flush()
            calls.append(row)
    db.commit()
    db.refresh(campaign)
    return {
        **campaign_out(campaign),
        "calls_placed": len(calls),
        "candidates": len(candidates),
    }
