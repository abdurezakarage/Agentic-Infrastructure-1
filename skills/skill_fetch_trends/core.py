from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from pydantic import BaseModel, Field, conint

from specs.technical import TrendData


class TrendFetchInput(BaseModel):
    """Input contract for AS-001 trend fetcher."""

    niche: str = Field(..., min_length=1)
    timeframe: str = Field("24h", min_length=1)
    limit: conint(ge=1) = 10  # type: ignore[valid-type]


def validate_input(payload: Dict) -> TrendFetchInput:
    """Validate and normalize input for fetching trends."""

    return TrendFetchInput(**payload)


def _seed_trends_for_niche(niche: str) -> List[Dict]:
    topics_by_niche = {
        "fashion": [
            "AI Couture",
            "Sustainable Fabrics",
            "Virtual Try-On",
        ],
        "crypto": [
            "Layer-2 Adoption",
            "DeFi Yield Reset",
            "On-chain Identity",
        ],
        "gaming": [
            "Co-op Roguelikes",
            "Indie Pixel Revival",
            "Crossplay Updates",
        ],
    }

    topics = topics_by_niche.get(niche, [f"{niche.title()} Trend"])
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    trends: List[Dict] = []

    for idx, topic in enumerate(topics, start=1):
        trends.append(
            {
                "trend_id": str(uuid4()),
                "topic": topic,
                "niche": niche,
                "score": max(0.1, 1 - (idx * 0.1)),
                "volume": 1000 + idx * 250,
                "sources": ["twitter", "news"],
                "timestamp": now,
                "relevant_keywords": [niche, "trend", topic.split()[0]],
            }
        )

    return trends


def fetch_trends(niche: str, timeframe: str = "24h", limit: int = 10) -> Dict:
    """Return spec-compliant trend data for a niche."""

    validate_input({"niche": niche, "timeframe": timeframe, "limit": limit})
    trends = _seed_trends_for_niche(niche)[:limit]

    # Validate against technical spec schema (AS-001 contract).
    for trend in trends:
        TrendData(**trend)

    return {
        "trends": trends,
        "fetched_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
