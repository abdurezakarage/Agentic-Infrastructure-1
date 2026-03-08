
## Purpose
Fetches trending topics from configured sources for content planning.

## Input Schema
```json
{
  "niche": "string (required)",
  "timeframe": "string (optional, default: '24h')",
  "limit": "integer (optional, default: 10)"
}


 ## output Schema

 {
  "trends": [
    {
      "topic": "string",
      "score": "float",
      "volume": "integer",
      "sources": ["string"],
      "keywords": ["string"]
    }
  ],
  "fetched_at": "timestamp"
}
