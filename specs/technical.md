# Technical Specification (TECH-API)

This document specifies the backend services, contracts, and workflows required to
ship the Chimera agent platform. It complements [specs/functional.md](specs/functional.md)
and [specs/openclaw_integration.md](specs/openclaw_integration.md) by making the
implementation-ready decisions explicit.

## 1. Scope and Goals
- Provide unambiguous requirements so an AI coder can implement the backend.
- Cover REST APIs, MCP tool contracts, Redis event envelopes, and PostgreSQL
  schemas.
- Describe Planner-Worker-Judge orchestration, OpenClaw integration protocol,
  and human-in-the-loop (HITL) placement.

## 2. Backend Services
| Service | Tech Stack | Responsibilities | Interfaces |
| --- | --- | --- | --- |
| Orchestrator API | FastAPI + Uvicorn | Accept tasks, expose agent state, provide OpenClaw webhook, surface HITL escalations | HTTPS JSON, OpenAPI, Auth via HMAC header |
| Agent Runtime | LangChain/Superagent (Planner-Worker-Judge) | Execute task lifecycle, call MCP tools, enforce guardrails | Redis streams, MCP, Postgres |
| Queue & Scheduler | Redis Streams + RQ workers | Durable task routing between Planner, Worker, Judge lanes | redis:// channels (`planner.queue`, `worker.queue`, `judge.queue`) |
| Persistence | PostgreSQL + SQLAlchemy | Store agents, tasks, plans, transactions, audit events | psycopg, Alembic migrations |
| Memory Layer | Weaviate (vector) + S3 (artifacts) | Long-term memory, media storage referenced by tasks | HTTP(S) + signed URLs |
| Telemetry | MCP Sense emitter + OpenTelemetry | Emit traces, metrics, audit logs | gRPC OTLP, JSON lines |

All services are packaged as Docker containers orchestrated via Makefile targets.

## 3. Agent Framework & Orchestration
1. **Planner (AS-001 focus)**: builds `task_plan` documents with ordered steps.
2. **Worker (AS-002/AS-003)**: executes plan steps via MCP skills, streams
   interim outputs to Redis and persists artifacts to S3.
3. **Judge (AS-003/AS-004)**: verifies outputs before side effects, uses
   persona policies (`SOUL.md`) and compliance rules.
4. **CFO Judge**: specialized Judge for monetary actions; enforces
   `daily_spend_limit`, triggers HITL for amounts above `hitl_threshold`.
5. **HITL Escalation Point**: operations team can approve/deny via `/hitl`
   endpoint; results feed back into Judge lane.

### Orchestration Pattern
```
OpenClaw/Web client -> Orchestrator POST /tasks
Orchestrator -> Redis planner.queue event (TaskQueued)
Planner -> Redis worker.queue event (PlanReady)
Worker -> MCP tools (skills/*), writes output -> Redis judge.queue event (WorkSubmitted)
Judge -> Approves -> Orchestrator PATCH /tasks/{id} status=complete
Judge -> Rejects -> sends revision request to worker queue
Judge (financial) -> CFO -> optional HITL -> Transactions table update
```

## 4. Inter-System Communication
### 4.1 REST/HTTPS
- JSON payloads only, UTF-8, enforced by FastAPI validation.
- Authentication via `X-Chimera-Signature` (HMAC-SHA256 over body).

### 4.2 Redis Event Envelopes
All events share the envelope:
```json
{
  "event_id": "uuid_v4",
  "trace_id": "uuid_v4",
  "event_type": "TaskQueued|PlanReady|WorkSubmitted|JudgeDecision|HitlEscalated",
  "payload": {},
  "emitted_at": "iso8601",
  "replayable": true
}
```

### 4.3 MCP Tool Calls
- Skills ship as MCP tools under namespace `chimera.skills.*`.
- Tool invocation history stored in `audit_events` table.

### 4.4 OpenClaw Integration
- Incoming webhook described in Section 6.4 references
  [specs/openclaw_integration.md](specs/openclaw_integration.md) requirements.
- Outgoing discovery feed uses signed task metadata posted to OpenClaw hub.

## 5. Data Layer & Schemas
### 5.1 PostgreSQL
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    soul_md_path TEXT NOT NULL,
    wallet_address VARCHAR(42),
    capabilities JSONB NOT NULL,
    mcp_endpoints JSONB NOT NULL,
    daily_spend_limit NUMERIC(14,2) DEFAULT 0,
    hitl_threshold NUMERIC(14,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    task_type VARCHAR(64) NOT NULL,
    priority VARCHAR(16) DEFAULT 'medium',
    status VARCHAR(32) DEFAULT 'pending',
    context JSONB NOT NULL,
    plan JSONB,
    output_data JSONB,
    confidence_score REAL,
    trace_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    agent_id UUID REFERENCES agents(id),
    amount NUMERIC(18,4) NOT NULL,
    currency VARCHAR(8) DEFAULT 'USD',
    to_address VARCHAR(64) NOT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    signed_at TIMESTAMPTZ,
    trace_id UUID NOT NULL
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY,
    event_type VARCHAR(64) NOT NULL,
    actor VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    task_id UUID,
    agent_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE memories (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.2 Pydantic Models
- `Trend` model matches Section 6.1 schema with validation on `score` range.
- `TaskContext` enforces `required_resources` as MCP URIs via regex
  `^mcp://[a-z0-9_/.-]+$`.
- `TransactionIntent` ensures `amount > 0` and `currency in {'USD','ETH','SOL'}`.

## 6. API Contracts
All endpoints live under `/api/v1`. Responses wrap payloads:
```json
{
  "data": {},
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.1 POST /api/v1/tasks
Create a task from Planner, OpenClaw, or operator input.

**Request**
```json
{
  "agent_id": "uuid_v4",
  "task_type": "fetch_trends|generate_content|publish_post|execute_transaction",
  "priority": "high|medium|low",
  "context": {
    "goal_description": "string",
    "persona_constraints": ["string"],
    "required_resources": ["mcp://twitter/trends", "mcp://memory/recent"],
    "niche": "fashion|crypto|gaming"
  },
  "origin": "openclaw|internal|manual",
  "trace_id": "uuid_v4"
}
```

**Response**
```json
{
  "data": {
    "task_id": "uuid_v4",
    "status": "pending"
  },
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.2 GET /api/v1/tasks/{task_id}
Returns task, plan, outputs, and audit trail pointers.

**Response**
```json
{
  "data": {
    "task_id": "uuid_v4",
    "agent_id": "uuid_v4",
    "task_type": "fetch_trends",
    "status": "in_progress",
    "plan": {"steps": [{"id": "plan-1", "action": "call_skill", "skill": "chimera.skills.trends"}]},
    "output_data": {"trends": []},
    "confidence_score": 0.82,
    "audit_events": ["uuid_v4"],
    "created_at": "iso8601"
  },
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.3 POST /api/v1/tasks/{task_id}/worker-output
Worker submits results for Judge review.

**Request**
```json
{
  "step_id": "plan-1",
  "output_data": {
    "trends": [{
      "trend_id": "uuid_v4",
      "topic": "Modular Synth Day",
      "score": 0.73,
      "volume": 9215,
      "sources": ["twitter"],
      "timestamp": "iso8601",
      "relevant_keywords": ["synth", "music"]
    }]
  },
  "tool_invocations": [
    {
      "tool_name": "chimera.skills.skill_fetch_trends",
      "input": {"niche": "music"},
      "output_ref": "s3://chimera-artifacts/trends.json"
    }
  ]
}
```

**Response**
```json
{
  "data": {"status": "under_review"},
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.4 POST /api/v1/openclaw/hooks
Receives OpenClaw tasks. Validates MCP-only resources per OCL-002.

**Request**
```json
{
  "trace_id": "uuid_v4",
  "agent_profile": {
    "agent_id": "uuid_v4",
    "capabilities": ["trend_research", "content_generation"],
    "mcp_endpoints": ["https://chimera/mcp/trends"]
  },
  "task": {
    "task_type": "generate_content",
    "priority": "high",
    "required_resources": ["mcp://memory/recent"],
    "objective": "Create teaser thread"
  }
}
```

**Response**
```json
{
  "data": {"task_id": "uuid_v4", "status": "queued"},
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.5 POST /api/v1/hitl/escalations
HITL reviewers approve or reject Judge requests.

**Request**
```json
{
  "task_id": "uuid_v4",
  "transaction_id": "uuid_v4",
  "decision": "approved|rejected",
  "comment": "string",
  "reviewer": "email"
}
```

**Response**
```json
{
  "data": {"status": "approved"},
  "meta": {"trace_id": "uuid_v4"}
}
```

### 6.6 GET /api/v1/agents/{agent_id}
Provides immutable agent profile for registry exposure.

**Response**
```json
{
  "data": {
    "agent_id": "uuid_v4",
    "name": "Ava",
    "soul_md_path": "s3://chimera/souls/ava.md",
    "capabilities": ["trend_research", "content_generation"],
    "mcp_endpoints": ["https://chimera/mcp/trends"],
    "wallet_address": "0x...",
    "daily_spend_limit": 500.00,
    "hitl_threshold": 250.00
  },
  "meta": {"trace_id": "uuid_v4"}
}
```

## 7. Tools, Skills, and Data Integrations
| Skill | MCP Name | Input Schema | Output Schema | Data Touchpoints |
| --- | --- | --- | --- | --- |
| Trend Fetcher | chimera.skills.skill_fetch_trends | `{ "niche": "string", "sources": ["twitter"] }` | `{ "trends": [Trend] }` | Reads Weaviate memory for context; writes artifact to S3 |
| Caption Generator | chimera.skills.skill_generate_caption | `{ "trend_id": "uuid", "persona": "string" }` | `{ "caption": "string", "tone": "string" }` | Updates tasks.output_data |
| Post Publisher | chimera.skills.skill_publish_post | `{ "platform": "twitter", "content": "string", "media_urls": [] }` | `{ "platform_id": "string", "permalink": "url" }` | Creates audit event + telemetry |

All MCP tools must surface JSON Schema definitions inside their manifest (`tools/*.json`).

## 8. Human-in-the-Loop Placement
- Triggered when `transaction.amount >= agents.hitl_threshold` or when
  Judge flags compliance issues (`judge_reason = 'policy_violation'`).
- `/api/v1/hitl/escalations` records reviewer decision; results stored in
  `audit_events` with `actor = 'hitl'`.
- Until decision arrives, tasks remain in `status = awaiting_hitl` and Workers
  are paused from executing further plan steps.

## 9. Acceptance Criteria
1. **TECH-AC-1:** Every external task invocation flows through Planner -> Worker -> Judge without bypass.
2. **TECH-AC-2:** All REST endpoints enforce JSON schema validation with descriptive errors and trace IDs.
3. **TECH-AC-3:** OpenClaw webhook rejects payloads containing non-MCP resources (`OCL_ERR_NON_MCP_RESOURCE`).
4. **TECH-AC-4:** `transactions` cannot transition to `approved` unless CFO Judge + optional HITL decision logged.
5. **TECH-AC-5:** Redis events are replayable (idempotent consumers) and persist for 7 days.
6. **TECH-AC-6:** Pydantic models prevent invalid `score` (0-1) and enforce ISO8601 timestamps.

## 10. Test Strategy
- **Unit Tests:** Pydantic models, Redis event serializers, skill adapters.
- **Contract Tests:** JSON schema snapshots for REST endpoints + MCP tool manifests.
- **Integration Tests:** Spin up docker-compose (FastAPI + Redis + Postgres), execute full Planner-Worker-Judge happy path and failure paths (non-MCP resource, HITL rejection).
- **Load Tests:** k6 scripts hitting `/tasks` at 50 RPS ensuring <200 ms p95.
- **Security Tests:** HMAC signature verification, RBAC on HITL endpoints, SQL injection fuzzing.
- **Data Tests:** Alembic migration smoke tests, referential integrity checks for orphaned tasks/transactions.

Meeting the acceptance criteria and passing the test strategy is required before
shipping backend code for Chimera agents.

## 11. Frontend Specification (TECH-FE)
This section defines the full intent for the operator-facing Chimera Console so
an AI coder can implement the UI without ambiguity.

### 11.1 Personas & Entry Points
- **Ops Lead:** monitors agents, reviews content, manages HITL decisions.
- **Data Analyst:** explores trend analytics, filters KPIs, exports data.
- **Compliance Officer:** reviews Judge decisions, audits transactions.
All users authenticate via enterprise SSO and land on the **Command Dashboard**.

### 11.2 Screen Inventory & Data Links
| Screen/View | Purpose | Backend Contracts |
| --- | --- | --- |
| Command Dashboard | Snapshot of tasks, alerts, spend | GET /api/v1/tasks (summary), GET /api/v1/agents/{id}, telemetry feed |
| Trend Explorer | Inspect trend outputs, filter niches | GET /api/v1/tasks?task_type=fetch_trends, tasks.output_data.trends schema |
| Content Review Queue | Approve/revise Worker outputs before publish | GET /api/v1/tasks?status=under_review, POST /api/v1/tasks/{id}/worker-output, Judge status updates |
| Agent Monitor | Real-time agent health, queue depth | GET /api/v1/agents/{id}, Redis metrics adapter, audit_events |
| Analytics & Filters | KPI board (engagement, velocity, spend) with filtering | Aggregated from tasks + transactions tables via /api/v1/tasks (with query params) and /api/v1/transactions |
| HITL Escalations | Resolve financial/content escalations | GET /api/v1/hitl/escalations (to be implemented), POST /api/v1/hitl/escalations |
| Audit & Transcript Viewer | Inspect Judge decisions, tool invocations | GET /api/v1/tasks/{id} (audit_events refs), GET /api/v1/audit-events/{event_id} (future) |
| Settings & Personas | Manage SOUL references, thresholds | GET/PUT /api/v1/agents/{id}, POST /api/v1/agents/{id}/thresholds (future) |

### 11.3 Critical Interaction Flows
#### Content Review Flow
1. Ops selects task from Content Review Queue (status `under_review`).
2. UI fetches task via GET /api/v1/tasks/{task_id} to populate plan, outputs, tool invocations.
3. Reviewer can **Approve**, **Request Revisions**, or **Escalate to HITL**.
   - Approve triggers PATCH /api/v1/tasks/{id} `{status: "complete"}` (future) + emits Judge decision.
   - Request Revisions posts comment to POST /api/v1/tasks/{id}/worker-output with `status = needs_revision`.
   - Escalate calls POST /api/v1/hitl/escalations (Section 6.5 schema).
4. UI updates queue via optimistic update + refetch list.

#### Analytics Filtering Flow
1. Analyst opens Analytics view; default date range 7 days.
2. UI calls GET /api/v1/tasks with query params `task_type`, `date_from`, `date_to` and GET /api/v1/transactions for spend.
3. Filters (niche, platform, agent) emit debounced requests; charts rerender.
4. Export action triggers CSV generation client-side from returned JSON.

#### Agent Monitoring Flow
1. Agent Monitor loads via GET /api/v1/agents/{id} plus websocket to telemetry stream (OTLP proxy).
2. Component renders status cards (queue depth, average latency) by polling `/metrics/redis` (future) every 10s.
3. Clicking an agent opens drawer with latest tasks (GET /api/v1/tasks?agent_id=...).

#### Human Approval (HITL) Flow
1. Escalated items populate HITL queue via GET /api/v1/hitl/escalations.
2. Reviewer inspects linked task via GET /api/v1/tasks/{task_id}.
3. Decision form requires `decision`, optional `comment`, auto-fills `transaction_id`.
4. Submitting POST /api/v1/hitl/escalations updates status; UI moves card to Resolved tab and notifies Judge lane via websocket update.

### 11.4 Component Hierarchy
- **AppShell**
  - `TopNav` (global search, alerts, profile)
  - `SideNav` (Dashboard, Trends, Review, Analytics, Agents, HITL, Audit, Settings)
  - `MainViewport`
    - Route-specific component (e.g., `DashboardView`)
      - `Header` (title, filters, actions)
      - `ContentArea`
        - Layout-specific subcomponents (cards, tables, timelines)

#### Example: Content Review View
- `ReviewHeader` (filters, quick stats)
- `TaskListPanel` (virtualized list of tasks)
- `TaskDetailPanel`
  - `PlanAccordion`
  - `OutputPreview` (JSON -> human view, media carousel)
  - `ToolInvocationLog` (table bound to `tool_invocations` schema)
  - `ActionBar` (Approve, Revise, Escalate buttons -> API calls)

### 11.5 Wireframe Notes
ASCII layout for Content Review:
```
-----------------------------------------------------
| Filters | Status=Under Review | Niche ▼ | Priority |
-----------------------------------------------------
| Task List (left 30%) | Task Detail (right 70%)    |
| [Task #1] status pill | Plan Accordion            |
| [Task #2] ...         | Output preview (json tab) |
|                       | Tool log table            |
|                       | ------------------------- |
|                       | [Approve] [Revise] [HITL] |
-----------------------------------------------------
```
Design system uses an expressive serif for headings (e.g., "Fraunces") and geometric sans for body ("Sora"). Background employs low-contrast gradient (`#05070f` → `#0f1b2f`) with glass panels to avoid boilerplate look, adhering to frontend task guidance.

### 11.6 Interaction Patterns & Validation
- **Tables:** column-level filters, persistent column state in localStorage.
- **Forms:** inline validation, map each field to backend property (e.g., `daily_spend_limit` → PATCH /api/v1/agents/{id}).
- **Notifications:** toast for success/error referencing `trace_id` from API response meta.
- **Loading states:** skeleton screens for tables, spinner for cards.
- **Empty states:** CTA linking to relevant action (e.g., "No HITL items" → link to Analytics).

### 11.7 Accessibility & Internationalization
- WCAG 2.1 AA contrast (4.5:1 min) with theme tokens documented in design kit.
- Keyboard navigation: focus outlines, skip links, modals trap focus.
- Screen-reader labels referencing action context (e.g., `aria-label="Approve task TASK_ID"`).
- Supports locale switcher for dates/numbers; copy remains English in v1 but CLDR formatting ready.

### 11.8 Traceability Matrix
| UI Element | Backend Contract | Data Schema |
| --- | --- | --- |
| Task status pill | GET /api/v1/tasks/{id} `status` | tasks.status enum |
| Trend card | tasks.output_data.trends | Trend model Section 6.1 |
| Agent spend meter | GET /api/v1/transactions aggregates | transactions.amount |
| HITL card | GET /api/v1/hitl/escalations | Section 6.5 request schema |
| Audit timeline | audit_events payload | audit_events table |

### 11.9 Frontend Acceptance Criteria
1. **FE-AC-1:** Every screen listed in Table 11.2 implemented with routing and linked data sources.
2. **FE-AC-2:** Critical flows (Section 11.3) demonstrably work using mocked backend following schemas.
3. **FE-AC-3:** UI enforces MCP-only context by surfacing warnings when task context contains non-MCP URIs (client-side regex).
4. **FE-AC-4:** HITL decisions cannot submit without `comment` when rejecting.
5. **FE-AC-5:** All interactive elements reachable via keyboard and have ARIA labels.
6. **FE-AC-6:** Charts/tables export selected filters meta with trace IDs.

### 11.10 Frontend Test Strategy
- **Storybook visual specs** for each component (AppShell, TaskListPanel, TrendCard, etc.).
- **Cypress E2E flows** covering Content Review, Analytics filtering, Agent monitor, HITL decision.
- **Accessibility audits** using axe-core automated checks per route.
- **Contract mocks** generated from OpenAPI + JSON schemas defined in Sections 6.1–6.6 to ensure front-back alignment.
- **Performance budgets**: Largest Contentful Paint < 2.5s on reference hardware; interactivity target < 100 ms for queue actions.
