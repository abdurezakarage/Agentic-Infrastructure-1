# Tooling Strategy (Task 2.3)

## Purpose
Define development MCP tools and runtime Agent Skills. This is the tooling map for Project Chimera.

## Sub-Task A: Developer Tools (MCP)
**Goal:** Accelerate development and governance with MCP servers.

**Selected MCP Servers**
- **git-mcp**: repository operations, diff review, metadata.
- **filesystem-mcp**: structured file edits and project scaffolding.
- **cursor-browser-extension**: UI verification for frontend/webapp tasks.
- **cursor-ide-browser**: IDE-driven UI checks and quick validations.

**Usage Guidelines**
- Use MCP for all external interactions (Prime Directive: MCP only).
- Log tool usage in MCP Sense when performing impactful actions.

## Sub-Task B: Agent Skills (Runtime)
**Definition:** A Skill is a capability package with a strict IO contract.

**Core Skills (Initial)**
- **skill_fetch_trends**
  - Input: `niche`, `timeframe`, `limit`
  - Output: list of trends with score, volume, sources, keywords
- **skill_generate_caption**
  - Input: `context`, `platform`, `tone`, optional `image_description`
  - Output: caption string, hashtags list, confidence score
- **skill_publish_post**
  - Input: `platform`, `content`, `schedule_time`, `ai_disclosure`
  - Output: publish result with post ID and platform response

