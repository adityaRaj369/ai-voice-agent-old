SCREENING_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "interested": {"type": "string"},
        "qualified": {"type": "string"},
        "experience_years": {"type": "string"},
        "notice_period": {"type": "string"},
        "expected_ctc": {"type": "string"},
        "current_location": {"type": "string"},
        "languages": {"type": "string"},
        "can_join_shift": {"type": "string"},
        "recommendation": {"type": "string"},
        "summary": {"type": "string"},
    },
}

OUTREACH_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "interested": {"type": "string"},
        "current_role": {"type": "string"},
        "availability_for_screening": {"type": "string"},
        "preferred_language": {"type": "string"},
        "objections": {"type": "string"},
        "next_step": {"type": "string"},
        "summary": {"type": "string"},
    },
}

ATTENDANCE_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "employee_code": {"type": "string"},
        "worker_name": {"type": "string"},
        "site_code": {"type": "string"},
        "attendance_status": {"type": "string"},
        "shift": {"type": "string"},
        "identity_verified": {"type": "string"},
        "notes": {"type": "string"},
    },
}


def screening_payload(job_title: str = "open role") -> dict:
    return {
        "name": "Hiring Screener",
        "language": "ENGLISH",
        "voice_persona": "NEHA",
        "persona_name": "NEHA",
        "objective": "Screen a job candidate for a frontline or operations role and collect structured hiring signals.",
        "introduction": "Namaste, this is Neha calling from the hiring team. I would like to ask a few short questions about a job opening.",
        "agent_prompt": (
            "You are Neha, a polite bilingual hiring assistant. The candidate name is {candidate_name}. "
            "The role is {job_role} at {company} in {location}. "
            "Ask one question at a time: interest, years of experience, current city, languages spoken, "
            "notice period or joining date, expected salary, and whether they can work the required shift. "
            "If they are not interested, thank them and end. Keep the call under four minutes. "
            "Do not discuss politics. Speak simply. Confirm answers by repeating key facts."
        ),
        "result_prompt": (
            "From the conversation, extract hiring signals as JSON matching the schema. "
            "If unknown, use 'unknown'. recommendation should be hire_now, maybe, or reject."
        ),
        "result_schema": SCREENING_RESULT_SCHEMA,
    }


def outreach_payload() -> dict:
    return {
        "name": "Talent Outreach",
        "language": "ENGLISH",
        "voice_persona": "ROY",
        "persona_name": "ROY",
        "objective": "Reach out to a sourced professional, introduce an open role, and capture interest plus availability.",
        "introduction": "Hello, this is Roy calling about a role that matched your profile. Do you have two minutes?",
        "agent_prompt": (
            "You are Roy, a concise talent outreach agent. Speak with {candidate_name}. "
            "You found them for {job_role} at {company} in {location}. "
            "Explain why they were matched in one sentence. Ask if they are open to hearing about it. "
            "If yes, ask current role, when they can take a screening call, preferred language, and any concerns. "
            "If no, thank them and end. Never pressure. Keep under three minutes."
        ),
        "result_prompt": "Extract outreach outcome JSON. next_step should be screen, nurture, or do_not_contact.",
        "result_schema": OUTREACH_RESULT_SCHEMA,
    }


def attendance_payload() -> dict:
    return {
        "name": "Site Attendance Clerk",
        "language": "HINDI",
        "voice_persona": "MIRA",
        "persona_name": "MIRA",
        "objective": "Verify a worker's identity over a shared site phone and record today's attendance.",
        "introduction": "Namaste, main Mira bol rahi hoon, attendance desk se. Attendance mark karne ke liye naam aur employee code boliye.",
        "agent_prompt": (
            "You are Mira, an attendance clerk for factories and stores. Workers may share one landline. "
            "Ask for name, employee code, site code, spoken PIN, and whether they are present, late, or on leave. "
            "The expected worker may be {candidate_name} at site {location} for shift {job_role}. "
            "If the PIN or name does not match, mark identity_verified as no and ask a supervisor to confirm. "
            "Keep the call under two minutes. Speak Hindi mixed with simple English numbers."
        ),
        "result_prompt": "Extract attendance JSON. attendance_status should be present, late, absent, or leave.",
        "result_schema": ATTENDANCE_RESULT_SCHEMA,
    }
