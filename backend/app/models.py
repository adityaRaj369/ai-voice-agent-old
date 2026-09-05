from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200), default="Hunar Demo Co")
    location: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text)
    employment_type: Mapped[str] = mapped_column(String(64), default="full_time")
    parsed: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    candidates: Mapped[list["Candidate"]] = relationship(back_populates="job")
    campaigns: Mapped[list["OutreachCampaign"]] = relationship(back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    headline: Mapped[str] = mapped_column(String(300), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    source: Mapped[str] = mapped_column(String(64), default="manual")
    profile_url: Mapped[str] = mapped_column(String(500), default="")
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(64), default="new")
    score: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    job: Mapped[Job | None] = relationship(back_populates="candidates")
    calls: Mapped[list["VoiceCall"]] = relationship(back_populates="candidate")


class VoiceAgent(Base):
    __tablename__ = "voice_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hunar_agent_id: Mapped[str] = mapped_column(String(64), default="")
    name: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(32), default="ENGLISH")
    voice_persona: Mapped[str] = mapped_column(String(32), default="NEHA")
    objective: Mapped[str] = mapped_column(Text, default="")
    result_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    calls: Mapped[list["VoiceCall"]] = relationship(back_populates="agent")


class OutreachCampaign(Base):
    __tablename__ = "outreach_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200))
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("voice_agents.id"), nullable=True)
    channels: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(64), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    job: Mapped[Job | None] = relationship(back_populates="campaigns")
    calls: Mapped[list["VoiceCall"]] = relationship(back_populates="campaign")
    messages: Mapped[list["OutreachMessage"]] = relationship(back_populates="campaign")


class VoiceCall(Base):
    __tablename__ = "voice_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hunar_call_id: Mapped[str] = mapped_column(String(64), default="")
    request_id: Mapped[str] = mapped_column(String(64), default="")
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("voice_agents.id"), nullable=True)
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("outreach_campaigns.id"), nullable=True)
    worker_id: Mapped[int | None] = mapped_column(ForeignKey("workers.id"), nullable=True)
    purpose: Mapped[str] = mapped_column(String(64), default="screening")
    callee_name: Mapped[str] = mapped_column(String(200))
    mobile_number: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(64), default="NOT_STARTED")
    result: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    recording_url: Mapped[str] = mapped_column(String(1000), default="")
    custom_data: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    agent: Mapped[VoiceAgent | None] = relationship(back_populates="calls")
    candidate: Mapped[Candidate | None] = relationship(back_populates="calls")
    campaign: Mapped[OutreachCampaign | None] = relationship(back_populates="calls")
    worker: Mapped["Worker | None"] = relationship()


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("outreach_campaigns.id"), nullable=True)
    candidate_id: Mapped[int | None] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(32))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(64), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    campaign: Mapped[OutreachCampaign | None] = relationship(back_populates="messages")


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(120))
    landline: Mapped[str] = mapped_column(String(32))
    supervisor_name: Mapped[str] = mapped_column(String(200))
    supervisor_phone: Mapped[str] = mapped_column(String(32))
    workers: Mapped[list["Worker"]] = relationship(back_populates="site")
    events: Mapped[list["AttendanceEvent"]] = relationship(back_populates="site")


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    shift: Mapped[str] = mapped_column(String(32), default="A")
    spoken_pin: Mapped[str] = mapped_column(String(8))
    rfid: Mapped[str] = mapped_column(String(32))
    site: Mapped[Site] = relationship(back_populates="workers")
    events: Mapped[list["AttendanceEvent"]] = relationship(back_populates="worker")


class AttendanceEvent(Base):
    __tablename__ = "attendance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    method: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str] = mapped_column(Text, default="")
    hunar_call_id: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    worker: Mapped[Worker] = relationship(back_populates="events")
    site: Mapped[Site] = relationship(back_populates="events")
