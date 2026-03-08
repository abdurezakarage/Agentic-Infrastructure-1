from specs.technical import TrendData
from skills.skill_fetch_trends.core import fetch_trends

def test_trend_data_schema():
    """Test that trend data matches our spec (API-002)"""
    # This should fail initially - defines the contract
    valid_data = {
        "trend_id": "123e4567-e89b-12d3-a456-426614174000",
        "topic": "AI Fashion",
        "niche": "fashion",
        "score": 0.85,
        "volume": 1500,
        "sources": ["twitter", "news"],
        "timestamp": "2026-02-05T10:30:00Z",
        "relevant_keywords": ["AI", "fashion", "trend"]
    }
    
    # This should pass when TrendData is implemented
    trend = TrendData(**valid_data)
    assert trend.topic == "AI Fashion"
    assert trend.score == 0.85
    
def test_trend_fetcher_returns_valid_structure():
    """Test the fetch_trends function returns spec-compliant data"""
    # This will fail until implementation
    result = fetch_trends(niche="fashion")
    
    # Contract from functional spec AS-001
    assert "trends" in result
    assert isinstance(result["trends"], list)
    assert len(result["trends"]) > 0
    assert "fetched_at" in result
    
    # Validate each trend against schema
    for trend in result["trends"]:
        TrendData(**trend)

def test_trend_filtering_by_niche():
    """Test that trends are filtered by niche"""
    # Implementation should filter irrelevant trends
    result = fetch_trends(niche="crypto")
    
    for trend in result["trends"]:
        assert trend["niche"] == "crypto"