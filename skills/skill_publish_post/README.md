
## Purpose
Publishes content to social media platforms via MCP tools.

## Input Schema
```json
{
  "platform": "twitter|instagram|tiktok (required)",
  "content": {
    "text": "string (required)",
    "media_urls": ["string (optional)"]
  },
  "schedule_time": "timestamp (optional)",
  "ai_disclosure": "boolean (default: true)"
}

## Output Schema
{
  "success": "boolean",
  "post_id": "string (if successful)",
  "published_at": "timestamp",
  "platform_response": "object (optional)"
}