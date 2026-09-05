from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.models import *  # noqa: F401,F403
from app.routers import agents, attendance, calls, candidates, dashboard, jobs, meta, outreach, search, webhooks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Frontline OS", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(agents.router)
app.include_router(calls.router)
app.include_router(search.router)
app.include_router(outreach.router)
app.include_router(attendance.router)
app.include_router(webhooks.router)
app.include_router(dashboard.router)
