from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.call_sync import apply_hunar_call_payload
from app.db import get_db

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/hunar")
async def hunar_webhook(payload: dict, db: Session = Depends(get_db)):
    nested = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    call = apply_hunar_call_payload(db, nested)
    return {"ok": True, "matched": bool(call), "call_id": call.id if call else None}
