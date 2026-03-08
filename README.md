# Project Chimera

An autonomous influencer swarm system using a Planner-Worker-Judge architecture with
agentic-first design and MCP-only integrations.

## Specs First
- Meta: `specs/_meta.md`
- Functional: `specs/functional.md` (AS-001 to AS-004)
- Technical: `specs/technical.md`
- OpenClaw integration: `specs/openclaw_integration.md`

## What This Repo Contains
- `skills/`: runtime skills with strict IO contracts and Pydantic validation
- `specs/`: authoritative requirements and contracts
- `tests/`: test suite covering skill interfaces and core behaviors
- `research/`: architecture and tooling notes
- `scripts/`: spec validation utilities

## Architecture Guardrails (From Specs)
- Planner-Worker-Judge separation is sacred.
- All external integrations must use MCP tools (no direct API calls).
- Optimistic concurrency control for state management.
- Pydantic for all data validation.
- Redis for queues, PostgreSQL for persistence, Weaviate for memory.

## Quick Start
```shell
make setup
make test
make spec-check
```

## Current Functional Scope
- **AS-001 Trend Detection**: fetch trends from configured sources and output structured JSON.
- **AS-002 Content Generation**: create multimodal content aligned with persona.
- **AS-003 Social Interaction**: publish and engage via MCP tools with compliance safeguards.
- **AS-004 Financial Autonomy**: judge-agent approval with spend limits and anomaly checks.

## Development Workflow
1. Read relevant spec files in `specs/`.
2. Write failing tests first (TDD).
3. Implement minimal working code.
4. Verify with tests.
5. Commit with spec references (e.g., `AS-001`).