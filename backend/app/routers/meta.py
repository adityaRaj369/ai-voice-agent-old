from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import hunar_client
from app.config import settings
from app.db import get_db
from app.models import Candidate, Job, OutreachCampaign, VoiceAgent, VoiceCall

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
def health():
    return {"ok": True, "product": "Frontline OS"}


@router.get("/status")
async def status(db: Session = Depends(get_db)):
    numbers = None
    hunar_ok = False
    hunar_error = None
    if settings.hunar_api_key:
        try:
            numbers = await hunar_client.list_numbers()
            hunar_ok = True
        except Exception as exc:
            hunar_error = str(exc)
    return {
        "hunar_configured": bool(settings.hunar_api_key),
        "hunar_ok": hunar_ok,
        "hunar_error": hunar_error,
        "pdl_configured": bool(settings.pdl_api_key),
        "apollo_configured": bool(settings.apollo_api_key),
        "twilio_configured": bool(settings.twilio_account_sid),
        "smtp_configured": bool(settings.smtp_host),
        "public_base_url": settings.public_base_url,
        "counts": {
            "jobs": db.query(func.count(Job.id)).scalar(),
            "candidates": db.query(func.count(Candidate.id)).scalar(),
            "agents": db.query(func.count(VoiceAgent.id)).scalar(),
            "calls": db.query(func.count(VoiceCall.id)).scalar(),
            "campaigns": db.query(func.count(OutreachCampaign.id)).scalar(),
        },
        "numbers": numbers,
    }
