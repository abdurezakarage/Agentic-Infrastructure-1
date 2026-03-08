# Skills Overview

This directory defines runtime skills for Project Chimera. Each skill has a strict input/output contract and must align with specs.

## Available Skills
- **skill_fetch_trends**: Fetch trending topics for a niche.
- **skill_generate_caption**: Produce platform-specific captions.
- **skill_publish_post**: Publish content via MCP.

## Conventions
- Each skill lives in its own folder with a `README.md` describing IO contracts.
- Implementations must validate inputs with Pydantic.
- External calls must be done via MCP tools only.
