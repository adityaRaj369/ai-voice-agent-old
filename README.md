# Frontline OS — Hunar.ai Assignment

End-to-end web app for the Hunar AI selection assignment:

1. **AI Hiring Assistant** — create Hunar Voice AI screening agents, place candidate calls, store structured answers  
2. **People Search & Reachout** — JD → people search (PDL / Apollo / demo graph) → voice + WhatsApp/email outreach → answers dashboard  
3. **Attendance without smartphones** — design + working prototype for 1,000 workers × 100 sites via landline IVR, PIN, and Voice AI  

**Stack:** Python FastAPI · Next.js · TypeScript · React · shadcn/ui · SQLite  

**Deadline reminder:** submit deployed URL + GitHub by **7 Sep 2026, 4:47 PM IST**. API key expires ~3 days after issue.

---

## Security (critical)

- Put `HUNAR_API_KEY` only in `.env` (backend). **Never commit it.**  
- `.gitignore` already excludes `.env`.  
- Rotate/revoke the key after submission if Hunar does not.

```bash
# root .env
HUNAR_API_KEY=your_key_here
HUNAR_API_BASE=https://api.voice.hunar.ai
PUBLIC_BASE_URL=https://your-backend.example.com   # needed for live webhooks
FRONTEND_ORIGIN=http://localhost:3000
```

Optional: `PDL_API_KEY`, `APOLLO_API_KEY`, Twilio WhatsApp, SMTP — without them, demo talent graph + simulated messaging still work.

---

## Local run

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
# If Windows blocks 8000, use --port 8001 and set NEXT_PUBLIC_API_URL accordingly
```

API docs: http://localhost:8000/docs  

### Frontend

```bash
cd frontend
npm install
# match backend port:
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
npm run dev
```

App: http://localhost:3000  

---

## Demo script (covers every feature)

1. Open **Overview** — confirm Hunar status (set API key first).  
2. **AI Hiring** — Create job → Create screening agent on Hunar → Add candidate with *your* phone → Screen with Voice AI → Refresh call / check **Answers Dashboard**.  
3. **People Search** — Select job → Search (demo graph works without PDL/Apollo) → select matches → Launch reachout (voice + WhatsApp).  
4. **Attendance** — See 100 sites / 1000 workers → mark via employee code + PIN → open a site → Voice check-in.  
5. **Q3 Design** — read the no-smartphone attendance plan.

For live webhooks from Hunar, expose the backend (ngrok / Railway / Render) and set `PUBLIC_BASE_URL` to that **HTTPS** URL (Hunar rejects `http://localhost`). Webhook path: `POST /api/webhooks/hunar`. Until then, use **Refresh** on calls / dashboard polling to pull results from Hunar.

---

## Deploy (suggested)

| Layer | Option |
|--------|--------|
| Backend | Railway / Render / Fly.io — run `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Vercel — set `NEXT_PUBLIC_API_URL` to backend URL |
| Env | Set `HUNAR_API_KEY`, `PUBLIC_BASE_URL`, `FRONTEND_ORIGIN` on the host |

After deploy, update CORS `FRONTEND_ORIGIN` to the Vercel domain.

---

## Hunar Voice API used

| Method | Path |
|--------|------|
| GET/POST | `/external/v1/agents/` |
| GET/PUT | `/external/v1/agents/{id}/` |
| GET/POST | `/external/v1/calls/` |
| POST | `/external/v1/calls/bulk/` |
| GET | `/external/v1/calls/{id}/` |
| GET | `/external/v1/numbers/` |

Auth header: `X-API-Key`. Docs: https://api.voice.hunar.ai/docs/external/

---

## Repo layout

```
backend/app/          FastAPI routers, Hunar client, models
backend/seed.py       2 jobs + 100 sites × 10 workers
frontend/src/app/     Hiring, Search, Dashboard, Attendance, Design
.env.example          Template only — no secrets
```

## Submission checklist

- [ ] Deployed frontend URL  
- [ ] Deployed backend URL (or same host)  
- [ ] GitHub repo (no API keys in history)  
- [ ] Live Hunar call tested with your phone  
- [ ] Screenshots of dashboard answers optional but helpful  
