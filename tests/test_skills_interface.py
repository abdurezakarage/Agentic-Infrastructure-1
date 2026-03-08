import pytest
from pydantic import ValidationError

def test_skill_fetch_trends_input_validation():
    """Test that skill accepts correct parameters"""
    # This defines the input contract from skill README
    from skills.skill_fetch_trends.core import validate_input
    
    valid_input = {
        "niche": "fashion",
        "timeframe": "24h",
        "limit": 10
    }
    
    # Should not raise error
    validate_input(valid_input)
    
    # Should raise for missing required field
    with pytest.raises(ValidationError):
        validate_input({"timeframe": "24h"})  # missing niche

def test_skill_generate_caption_output_schema():
    """Test caption generation output matches spec"""
    from skills.skill_generate_caption.core import generate_caption
    
    # This will fail until implementation
    result = generate_caption(
        context="New AI fashion trend",
        platform="instagram",
        tone="witty"
    )
    
    # Output contract from skill README
    assert "caption" in result
    assert isinstance(result["caption"], str)
    assert len(result["caption"]) > 0
    assert "hashtags" in result
    assert isinstance(result["hashtags"], list)
    assert "confidence_score" in result
    assert 0 <= result["confidence_score"] <= 1

def test_skill_publish_post_requires_platform():
    """Test platform is required for publishing"""
    from skills.skill_publish_post.core import publish_post
    
    with pytest.raises(ValueError, match="platform"):
        publish_post(content={"text": "Hello world"})
        # Missing platform should raise error