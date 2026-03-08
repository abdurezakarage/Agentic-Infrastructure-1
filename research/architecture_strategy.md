# Architecture Strategy (Task 1.2)

## Purpose
Define the architecture choices for Project Chimera before implementation. This document focuses on agent pattern selection, human approval points, and database strategy for high-velocity video metadata.

## Agent Pattern Selection
**Recommended Pattern:** Hierarchical Swarm (Planner → Worker → Judge)

**Rationale**
- **Planner** decomposes goals (campaigns, calendars, platform mix).
- **Workers** execute specialized skills (trend fetch, captioning, posting).
- **Judge** verifies safety, spec alignment, and budget controls.
- The swarm approach allows parallel task execution with explicit governance.

```mermaid
flowchart TB
    User[Human Operator] -->|Goal/Brief| Planner[Planner Agent]
    Planner -->|Tasks| WorkerA[Worker: Trend Fetch]
    Planner -->|Tasks| WorkerB[Worker: Caption Gen]
    Planner -->|Tasks| WorkerC[Worker: Publish]
    WorkerA --> Judge
    WorkerB --> Judge
    WorkerC --> Judge
    Judge -->|Approved| Scheduler[Execution Queue]
    Judge -->|Rejected| Planner
```

## Human-in-the-Loop (Safety Layer)
**Approval Points**
- **Content Approval Gate:** Before publishing, the Judge requests approval for:
  - Platform-sensitive content (e.g., regulated or financial topics)
  - Low-confidence outputs
  - High-risk or new personas
- **Budget Approval Gate:** Any financial actions above threshold require CFO Judge + human sign-off.

```mermaid
sequenceDiagram
    participant W as Worker
    participant J as Judge
    participant H as Human
    participant Q as Queue
    W->>J: Draft content + metadata
    J->>H: Approval request (if risk or low confidence)
    H-->>J: Approve / Reject
    J->>Q: Publish task (approved)
```

## Database Strategy for High-Velocity Video Metadata
**Recommendation:** PostgreSQL (SQL) as the primary store, with optional Redis cache.

**Why SQL**
- Strong schema enforcement for metadata integrity.
- Relational joins across campaigns, assets, and agent outputs.
- Supports JSONB for flexible tags and model diagnostics.

**When to Extend with NoSQL**
- High-scale analytics or event logs can be offloaded to a time-series/NoSQL store.
- Weaviate remains the semantic memory layer for agent retrieval.

```mermaid
erDiagram
    VIDEO_ASSET ||--o{ VIDEO_VERSION : has
    VIDEO_ASSET ||--o{ CAPTION : has
    VIDEO_ASSET {
        uuid id
        string title
        string platform
        string status
        timestamp created_at
    }
    VIDEO_VERSION {
        uuid id
        uuid asset_id
        string resolution
        string storage_url
        jsonb render_metadata
    }
    CAPTION {
        uuid id
        uuid asset_id
        string text
        jsonb hashtags
    }
```

## Notes
- Aligns with Prime Directives: specs-first, MCP-only integration, agentic design.
- Designed for safe scaling with clear audit trails.
