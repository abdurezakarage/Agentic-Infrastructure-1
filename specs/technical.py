from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, conint, confloat


class TrendData(BaseModel):
    """Trend data contract from technical spec (Trend Data Structure)."""

    trend_id: UUID = Field(..., description="Unique trend identifier (uuid_v4).")
    topic: str = Field(..., min_length=1)
    niche: str = Field(..., min_length=1)
    score: confloat(ge=0, le=1)  # type: ignore[valid-type]
    volume: conint(ge=0)  # type: ignore[valid-type]
    sources: List[str] = Field(..., min_length=1)
    timestamp: datetime
    relevant_keywords: List[str] = Field(..., min_length=1)
