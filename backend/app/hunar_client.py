from typing import Any

import httpx
from fastapi import HTTPException

from app.config import settings

HUNAR_BASE = settings.hunar_api_base.rstrip("/")


def _headers() -> dict[str, str]:
    if not settings.hunar_api_key:
        raise HTTPException(
            status_code=503,
            detail="HUNAR_API_KEY is not configured. Add it to .env (never commit it).",
        )
    return {"X-API-Key": settings.hunar_api_key, "Content-Type": "application/json"}


async def hunar_request(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{HUNAR_BASE}{path}"
    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.request(method, url, headers=_headers(), **kwargs)
    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail={"hunar_error": response.text, "path": path},
        )
    if not response.content:
        return None
    return response.json()


async def list_agents(page: int = 1, page_size: int = 50) -> Any:
    return await hunar_request("GET", "/external/v1/agents/", params={"page": page, "page_size": page_size})


async def create_agent(payload: dict[str, Any]) -> Any:
    return await hunar_request("POST", "/external/v1/agents/", json=payload)


async def get_agent(agent_id: str) -> Any:
    return await hunar_request("GET", f"/external/v1/agents/{agent_id}/")


async def update_agent(agent_id: str, payload: dict[str, Any]) -> Any:
    return await hunar_request("PUT", f"/external/v1/agents/{agent_id}/", json=payload)


async def create_call(payload: dict[str, Any]) -> Any:
    return await hunar_request("POST", "/external/v1/calls/", json=payload)


async def create_calls_bulk(payload: dict[str, Any]) -> Any:
    return await hunar_request("POST", "/external/v1/calls/bulk/", json=payload)


async def list_calls(**params: Any) -> Any:
    clean = {k: v for k, v in params.items() if v is not None}
    return await hunar_request("GET", "/external/v1/calls/", params=clean)


async def get_call(call_id: str) -> Any:
    return await hunar_request("GET", f"/external/v1/calls/{call_id}/")


async def list_numbers(page: int = 1, page_size: int = 50) -> Any:
    return await hunar_request("GET", "/external/v1/numbers/", params={"page": page, "page_size": page_size})


def callback_config() -> dict[str, str] | None:
    """Hunar requires HTTPS webhook URLs. Skip callbacks for local http:// setups."""
    base = settings.public_base_url.rstrip("/")
    if not base.startswith("https://"):
        return None
    webhook = f"{base}/api/webhooks/hunar"
    return {
        "call_status_callback_url": webhook,
        "call_recording_callback_url": webhook,
        "call_result_callback_url": webhook,
        "call_summary_callback_url": webhook,
    }


def default_retry_config() -> dict[str, int]:
    # Hunar only accepts retry_interval_hours in {3, 6, 9, 12, 24}
    return {"max_retry_count": 1, "retry_interval_hours": 3}
