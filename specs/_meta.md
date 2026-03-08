# Project Chimera: Meta Specification

## Vision
Build a factory for autonomous AI influencers that can research, create, and engage at scale using the Planner-Worker-Judge swarm pattern.

## Core Constraints
1. Agentic First: All components must be AI-agent accessible via specs and structured interfaces.
2. MCP Everywhere: No direct API calls; all external integration via Model Context Protocol.
3. Swarm Architecture: Planner, Worker, Judge separation with optimistic concurrency.
4. OpenClaw Ready: Agents must be discoverable in agent social networks.

## Non-Goals
1. Real-time video streaming
2. Direct human-AI voice interaction
3. Physical robotics integration

## Success Metrics
- 1000+ concurrent agents manageable by single orchestrator
- <10s end-to-end response for high-priority interactions
- Zero ungoverned financial transactions
- Full audit trail via MCP Sense telemetry