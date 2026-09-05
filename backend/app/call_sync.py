from sqlalchemy.orm import Session

from app.models import AttendanceEvent, Candidate, VoiceCall, Worker

TERMINAL_STATUSES = {"COMPLETED", "NOT_CONNECTED", "CANCELLED", "FAILED"}


def map_candidate_status_from_result(result: dict) -> str:
    interested = str((result or {}).get("interested") or "").strip().lower()
    rec = str((result or {}).get("recommendation") or (result or {}).get("next_step") or "").strip().lower()
    unknown = interested in {"", "unknown", "not available", "n/a", "-", "na"}
    if not unknown and ("not interest" in interested or interested in {"no", "not interested"}):
        return "not_interested"
    if rec in {"reject", "do_not_contact"}:
        return "not_interested"
    if rec in {"hire_now", "screen"} or (not unknown and ("yes" in interested or "interest" in interested)):
        return "engaged"
    return "contacted"


def apply_hunar_call_payload(db: Session, payload: dict) -> VoiceCall | None:
    hunar_id = str(payload.get("id") or payload.get("call_id") or "")
    if not hunar_id:
        return None
    call = db.query(VoiceCall).filter(VoiceCall.hunar_call_id == hunar_id).first()
    if not call:
        return None
    if payload.get("status"):
        call.status = payload["status"]
    if payload.get("result"):
        call.result = payload["result"]
    if payload.get("recording_url"):
        call.recording_url = payload["recording_url"]
    call.raw = payload

    if call.candidate_id:
        cand = db.query(Candidate).filter(Candidate.id == call.candidate_id).first()
        if cand:
            status = str(call.status or "").upper()
            if status in {"INITIATED", "RINGING", "SCHEDULED", "NOT_STARTED"}:
                cand.status = "calling"
            elif status == "IN_PROGRESS":
                cand.status = "on_call"
            elif status in {"NOT_CONNECTED", "CANCELLED", "FAILED"}:
                cand.status = "no_answer"
            elif status == "COMPLETED":
                if call.result:
                    cand.status = map_candidate_status_from_result(call.result)
                else:
                    cand.status = "contacted"

    if call.purpose == "attendance" and call.result:
        code = str((call.result or {}).get("employee_code") or "")
        worker = call.worker
        if not worker and code:
            worker = db.query(Worker).filter(Worker.employee_code == code).first()
        if worker:
            status = str((call.result or {}).get("attendance_status") or "present").lower()
            if status not in {"present", "late", "absent", "leave"}:
                status = "present"
            db.add(
                AttendanceEvent(
                    worker_id=worker.id,
                    site_id=worker.site_id,
                    method="voice",
                    status=status,
                    notes=str((call.result or {}).get("notes") or ""),
                    hunar_call_id=call.hunar_call_id,
                )
            )
    db.commit()
    db.refresh(call)
    return call
