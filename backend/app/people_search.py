from __future__ import annotations

from typing import Any

import httpx

from app.config import settings
from app.talent_graph import DEMO_PEOPLE, score_person


async def search_people(parsed_jd: dict[str, Any], provider: str = "auto", limit: int = 20) -> list[dict[str, Any]]:
    provider = (provider or "auto").lower()
    if provider in ("pdl", "auto") and settings.pdl_api_key:
        live = await _search_pdl(parsed_jd, limit)
        if live:
            return live
    if provider in ("apollo", "auto") and settings.apollo_api_key:
        live = await _search_apollo(parsed_jd, limit)
        if live:
            return live
    return _search_demo(parsed_jd, limit, used_provider="demo")


def _search_demo(parsed_jd: dict[str, Any], limit: int, used_provider: str) -> list[dict[str, Any]]:
    ranked = []
    for person in DEMO_PEOPLE:
        item = {**person, "source": used_provider, "score": score_person(person, parsed_jd)}
        ranked.append(item)
    ranked.sort(key=lambda p: p["score"], reverse=True)
    return ranked[:limit]


async def _search_pdl(parsed_jd: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    must: list[dict[str, Any]] = []
    title = parsed_jd.get("title_guess")
    location = parsed_jd.get("location_guess")
    if title:
        must.append({"match": {"job_title": title}})
    if location:
        must.append({"match": {"location_name": location}})
    query = {"query": {"bool": {"must": must or [{"exists": {"field": "full_name"}}]}}, "size": limit}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.peopledatalabs.com/v5/person/search",
            headers={"X-Api-Key": settings.pdl_api_key, "Content-Type": "application/json"},
            json=query,
        )
    if response.status_code >= 400:
        return []
    data = response.json()
    people = []
    for row in data.get("data") or []:
        people.append(
            {
                "full_name": row.get("full_name") or "",
                "headline": row.get("job_title") or "",
                "location": row.get("location_name") or "",
                "phone": (row.get("mobile_phone") or row.get("phone_numbers") or [""])[0]
                if isinstance(row.get("phone_numbers"), list)
                else (row.get("mobile_phone") or ""),
                "email": (row.get("recommended_personal_email") or ""),
                "skills": row.get("skills") or [],
                "profile_url": row.get("linkedin_url") or "",
                "source": "pdl",
                "score": 80,
                "raw": row,
            }
        )
    return people


async def _search_apollo(parsed_jd: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    payload = {
        "q_keywords": parsed_jd.get("title_guess") or "",
        "person_locations": [parsed_jd["location_guess"]] if parsed_jd.get("location_guess") else [],
        "page": 1,
        "per_page": limit,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.apollo.io/api/v1/mixed_people/search",
            headers={"X-Api-Key": settings.apollo_api_key, "Content-Type": "application/json"},
            json=payload,
        )
    if response.status_code >= 400:
        return []
    data = response.json()
    people = []
    for row in data.get("people") or []:
        people.append(
            {
                "full_name": f"{row.get('first_name', '')} {row.get('last_name', '')}".strip(),
                "headline": row.get("title") or "",
                "location": row.get("city") or "",
                "phone": "",
                "email": row.get("email") or "",
                "skills": [],
                "profile_url": row.get("linkedin_url") or "",
                "source": "apollo",
                "score": 75,
                "raw": row,
            }
        )
    return people
