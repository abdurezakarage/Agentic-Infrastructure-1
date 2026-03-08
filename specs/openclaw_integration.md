# OpenClaw Integration Specification

## Overview
OpenClaw integration makes Project Chimera agents discoverable and operable
within agent social networks, while enforcing MCP-only access and
Planner-Worker-Judge separation.

## Related Specs
- AS-001, AS-002, AS-003, AS-004 (functional stories)
- TECH-API (technical contracts in `specs/technical.md`)
- META-OPENCLAW (OpenClaw readiness in `specs/_meta.md`)

## Requirements

### OCL-001: Agent Registry Exposure
Expose each agent as an OpenClaw-compatible profile with immutable identity.

**Acceptance Criteria**
- Each agent has a stable `agent_id` (UUID v4) and human-readable `name`.
- Agent profile includes `soul_md_path`, `capabilities`, `mcp_endpoints`.
- Profiles are read-only outside the system.

### OCL-002: MCP-Only Task Invocation
All task execution in OpenClaw context must be invoked via MCP tools.

**Acceptance Criteria**
- No direct API calls to social platforms.
- Task payload includes `required_resources` as MCP URIs.
- If any resource is non-MCP, task is rejected with a structured error.

### OCL-003: Planner-Worker-Judge Enforcement
Incoming OpenClaw tasks must route through Planner, then Worker, then Judge.

**Acceptance Criteria**
- Planner produces a `task_plan` with `task_type`, `priority`, and constraints.
- Worker executes only approved plan steps.
- Judge can approve/reject before external side effects (posts, transactions).

### OCL-004: Economic Autonomy Guardrails
Transactions initiated via OpenClaw must be validated by CFO Judge agent.

**Acceptance Criteria**
- Enforce `daily_spend_limit` from `agents` table.
- Log all transaction intents with `status = pending` before signing.
- Large transactions trigger HITL escalation (threshold configurable).

### OCL-005: Auditability and Trace
All OpenClaw interactions must be auditable end-to-end.

**Acceptance Criteria**
- Each OpenClaw request has a `trace_id` (UUID v4).
- Store inputs/outputs in `tasks` table with `confidence_score`.
- Emit MCP Sense telemetry for all external actions.

## Data Contracts
OpenClaw payloads must map to `Task` and `Agent` objects defined in
`specs/technical.md` and validated via Pydantic models.

## Error Handling
- `OCL_ERR_NON_MCP_RESOURCE`: non-MCP resource in payload.
- `OCL_ERR_PLAN_REQUIRED`: planner output missing.
- `OCL_ERR_JUDGE_REJECTED`: judge denied external action.

## Non-Goals
- Real-time streaming
- Direct human voice control
- Physical robotics integration
