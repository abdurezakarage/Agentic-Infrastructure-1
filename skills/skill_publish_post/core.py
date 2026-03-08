from datetime import datetime, timezone
from typing import Dict, Literal

from pydantic import BaseModel, Field


class PublishPostInput(BaseModel):
    """Input contract for publishing content via MCP."""

    platform: Literal["twitter", "instagram", "tiktok"]
    content: Dict = Field(..., description="Post body containing text/media.")
    schedule_time: str | None = None
    ai_disclosure: bool = True


def publish_post(
    content: Dict | None = None,
    platform: Literal["twitter", "instagram", "tiktok"] | None = None,
    schedule_time: str | None = None,
    ai_disclosure: bool = True,
) -> Dict:
    """Validate publish request and return a stubbed response."""

    if not platform:
        raise ValueError("platform is required")
    if content is None or "text" not in content:
        raise ValueError("content.text is required")

    payload = PublishPostInput(
        platform=platform,
        content=content,
        schedule_time=schedule_time,
        ai_disclosure=ai_disclosure,
    )

    return {
        "success": True,
        "post_id": f"{payload.platform}-stub",
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "platform_response": {"ai_disclosure": payload.ai_disclosure},
    }
