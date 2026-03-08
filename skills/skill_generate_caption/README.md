
## Purpose
Generates engaging social media captions in the agent's persona voice.

## Input Schema
```json
{
  "context": "string (required)",
  "image_description": "string (optional)",
  "platform": "twitter|instagram|tiktok",
  "tone": "witty|professional|casual",
  "hashtags": "integer (optional, default: 3)"
}

## output Schema
{
  "caption": "string",
  "hashtags": ["string"],
  "confidence_score": "float",
  "reasoning": "string (optional)"
}
