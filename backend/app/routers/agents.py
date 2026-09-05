from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import hunar_client
from app.agent_templates import attendance_payload, outreach_payload, screening_payload
from app.db import get_db
from app.models import VoiceAgent
from app.schemas import AgentCreate
from app.serializers import agent_out

router = APIRouter(prefix="/api/agents", tags=["agents"])


def template_for(kind: str) -> dict:
    if kind == "outreach":
        return outreach_payload()
    if kind == "attendance":
        return attendance_payload()
    return screening_payload()


@router.get("")
def list_local_agents(db: Session = Depends(get_db)):
    return [agent_out(a) for a in db.query(VoiceAgent).order_by(VoiceAgent.id.desc()).all()]


@router.get("/hunar")
async def list_hunar_agents():
    return await hunar_client.list_agents()


@router.post("")
async def create_local_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    base = template_for(payload.kind)
    if payload.name:
        base["name"] = payload.name[:64]
    base["language"] = payload.language
    base["voice_persona"] = payload.voice_persona
    if payload.objective:
        base["objective"] = payload.objective
    if payload.introduction:
        base["introduction"] = payload.introduction
    if payload.agent_prompt:
        base["agent_prompt"] = payload.agent_prompt
    if payload.result_prompt:
        base["result_prompt"] = payload.result_prompt
    if payload.result_schema:
        base["result_schema"] = payload.result_schema
    remote = await hunar_client.create_agent(base)
    hunar_id = str(remote.get("id") or "")
    row = VoiceAgent(
        hunar_agent_id=hunar_id,
        name=base["name"],
        kind=payload.kind,
        language=base["language"],
        voice_persona=base["voice_persona"],
        objective=base["objective"],
        result_schema=base["result_schema"],
        raw=remote,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return agent_out(row)


@router.get("/{agent_id}")
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    row = db.query(VoiceAgent).filter(VoiceAgent.id == agent_id).first()
    if not row:
        raise HTTPException(404, "Agent not found")
    remote = None
    if row.hunar_agent_id:
        remote = await hunar_client.get_agent(row.hunar_agent_id)
    return {**agent_out(row), "hunar": remote}
