# Architecture

## Layers
- `app/core/`: config, logging, trace IDs, exceptions, model provider factory.
- `app/agents/`: Agno-specific agent definitions, registry, tool adapter. All Agno imports live here (+ orchestrator).
- `app/orchestrator/`: supervisor routing (Agno Team, route mode).
- `app/tools/`: framework-agnostic tool specs, schemas, registry, execution (policy + approval + audit).
- `app/policy/`: deterministic rules evaluated before tool execution.
- `app/approval/`: approval queue + service.
- `app/db/`: SQLAlchemy models, sessions, Alembic migrations.
- `app/interfaces/api/`: FastAPI routes.
- `app/core/observability.py`: optional LangSmith tracing for chat turns, tool calls, and token usage.

## TODO (backbone phase only)
- Frontend, Slack/email integrations.
- Vector DB / RAG.
- Guardrails / PII filtering (only field-level redaction in audit exists).
- Sandboxed code execution.
- Multi-tenant auth.
- Production-grade observability beyond structured logs.
