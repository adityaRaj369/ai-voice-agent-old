from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    title: str
    company: str = "Hunar Demo Co"
    location: str = ""
    description: str
    employment_type: str = "full_time"


class CandidateCreate(BaseModel):
    full_name: str
    phone: str = ""
    email: str = ""
    headline: str = ""
    location: str = ""
    skills: list[str] = Field(default_factory=list)
    source: str = "manual"
    profile_url: str = ""
    job_id: int | None = None
    score: float = 0


class AgentCreate(BaseModel):
    kind: str = Field(description="screening | outreach | attendance | custom")
    name: str | None = None
    language: str = "ENGLISH"
    voice_persona: str = "NEHA"
    objective: str | None = None
    introduction: str | None = None
    agent_prompt: str | None = None
    result_prompt: str | None = None
    result_schema: dict[str, Any] | None = None


class CallCreate(BaseModel):
    agent_id: int
    callee_name: str
    mobile_number: str
    candidate_id: int | None = None
    job_id: int | None = None
    campaign_id: int | None = None
    worker_id: int | None = None
    purpose: str = "screening"
    custom_data: dict[str, str] = Field(default_factory=dict)
    from_phone_number: str | None = None
    timezone: str = "Asia/Kolkata"


class SearchRequest(BaseModel):
    job_id: int | None = None
    description: str = ""
    title: str = ""
    location: str = ""
    provider: str = "auto"
    limit: int = 20
    save_to_job: bool = False


class OutreachLaunch(BaseModel):
    job_id: int
    candidate_ids: list[int]
    agent_id: int | None = None
    channels: list[str] = Field(default_factory=lambda: ["voice", "whatsapp"])
    from_phone_number: str | None = None


class AttendanceMark(BaseModel):
    worker_id: int | None = None
    employee_code: str | None = None
    spoken_pin: str | None = None
    method: str = "ivr"
    status: str = "present"
    notes: str = ""
    hunar_call_id: str = ""


class AttendanceVoice(BaseModel):
    worker_id: int
    agent_id: int | None = None
    mobile_number: str | None = None
    from_phone_number: str | None = None


class WebhookPayload(BaseModel):
    model_config = {"extra": "allow"}

    id: str | None = None
    status: str | None = None
    result: dict[str, Any] | None = None
    recording_url: str | None = None
    callee_name: str | None = None
    mobile_number: str | None = None
    received_at: datetime | None = None
