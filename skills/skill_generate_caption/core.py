from typing import Dict, List, Literal

from pydantic import BaseModel, Field, conint


class CaptionInput(BaseModel):
    """Input contract for caption generation."""

    context: str = Field(..., min_length=1)
    image_description: str | None = None
    platform: Literal["twitter", "instagram", "tiktok"]
    tone: Literal["witty", "professional", "casual"]
    hashtags: conint(ge=0, le=10) = 3  # type: ignore[valid-type]


def _build_hashtags(context: str, count: int) -> List[str]:
    words = [w.strip("#.,!?:;").lower() for w in context.split()]
    unique = []
    for word in words:
        if word and word not in unique:
            unique.append(word)
    base = [f"#{word}" for word in unique[:count]]
    while len(base) < count:
        base.append("#trend")
    return base


def generate_caption(
    context: str,
    platform: Literal["twitter", "instagram", "tiktok"],
    tone: Literal["witty", "professional", "casual"],
    image_description: str | None = None,
    hashtags: int = 3,
) -> Dict:
    """Generate a caption payload matching the skill schema."""

    payload = CaptionInput(
        context=context,
        image_description=image_description,
        platform=platform,
        tone=tone,
        hashtags=hashtags,
    )

    tone_prefix = {
        "witty": "Hot take:",
        "professional": "Insight:",
        "casual": "Vibes:",
    }[payload.tone]

    caption = f"{tone_prefix} {payload.context}"
    if payload.image_description:
        caption = f"{caption} ({payload.image_description})"

    return {
        "caption": caption,
        "hashtags": _build_hashtags(payload.context, payload.hashtags),
        "confidence_score": 0.72,
        "reasoning": "Rule-based template for deterministic output.",
    }
