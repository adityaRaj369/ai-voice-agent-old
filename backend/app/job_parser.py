from __future__ import annotations

import re
from typing import Any

TITLE_HINTS = [
    "store manager",
    "warehouse associate",
    "delivery executive",
    "field sales",
    "customer support",
    "nurse",
    "security guard",
    "data analyst",
    "software engineer",
    "recruiter",
    "operations executive",
    "rider",
    "picker",
    "packer",
    "team leader",
]

SKILL_HINTS = [
    "excel",
    "sales",
    "python",
    "sql",
    "hindi",
    "english",
    "driving",
    "inventory",
    "pos",
    "excel",
    "whatsapp",
    "negotiation",
    "first aid",
    "forklift",
]


def parse_job_description(text: str, title: str = "", location: str = "") -> dict[str, Any]:
    lowered = text.lower()
    found_titles = [t for t in TITLE_HINTS if t in lowered]
    skills = sorted({s for s in SKILL_HINTS if s in lowered})
    years = None
    year_match = re.search(r"(\d+)\+?\s*(?:years|yrs)", lowered)
    if year_match:
        years = int(year_match.group(1))
    langs = [lang for lang in ("hindi", "english", "tamil", "telugu", "kannada", "marathi", "bengali", "gujarati") if lang in lowered]
    loc = location
    if not loc:
        city_match = re.search(
            r"\b(bengaluru|bangalore|mumbai|delhi|hyderabad|chennai|pune|kolkata|jaipur|ahmedabad|lucknow|noida|gurgaon|gurugram)\b",
            lowered,
        )
        if city_match:
            loc = city_match.group(1).title()
    return {
        "title_guess": title or (found_titles[0].title() if found_titles else "Open Role"),
        "location_guess": loc,
        "skills": skills,
        "min_years": years,
        "languages": langs,
        "must_haves": found_titles,
        "keywords": sorted(set(re.findall(r"[a-zA-Z]{4,}", lowered)))[:40],
    }
