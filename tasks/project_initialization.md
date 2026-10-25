# Task: Scaffold a production-ready agent backbone for an HRM automation system using Agno

## Context

I am building an AI-automated HRM system. Requirements will arrive over time (leave management, onboarding, payroll, recruitment...), so the goal NOW is only the backbone: a clean, extensible project structure where new capabilities are added as tools/modules without restructuring.

Framework: Agno (https://docs.agno.com) for agent orchestration.
Stack: Python 3.12+, FastAPI (interface), PostgreSQL + SQLAlchemy 2.0 (data), Pydantic v2 (schemas), Alembic (migrations), Docker + docker-compose (local dev). Use UV for dependency management. LLM provider is environment-driven: Groq for local dev, OpenAI for production — switching must be a config change only, never a code change.

## Architecture requirements

1. **Agno is contained in one layer.** All Agno imports live only in `app/agents/` and `app/orchestrator/`. Core logic, tools, and policies must be framework-agnostic plain Python — if I later swap Agno for LangGraph, nothing outside those two folders changes.
2. **Tools are the extension point.** Every future HRM capability (leave, payroll, etc.) is implemented as a Python function or Agno Toolkit in `app/tools/<domain>/`, with a Pydantic input/output schema. Agents reference tools by registry, never by import spaghetti. Include a `ToolRegistry` that auto-discovers tools in `app/tools/` subfolders.
3. **Agents are registered, not hardcoded.** A single Supervisor agent handles intent classification and routing. Specialist agents (only one example: a "leave_agent" with 2 stub tools: `get_leave_balance`, `submit_leave_request`) are declared in config-driven registry entries with: name, role description, allowed tool names, and model.
4. **Human-in-the-loop is a first-class step.** Any tool flagged `requires_approval=True` does not execute directly. Instead it creates a pending Approval record (DB) with a structured payload (agent reasoning, proposed args, risk level) and returns a "pending approval" status to the agent. Build a minimal approval API endpoint (list pending, approve, reject) and record the decision.
5. **Deterministic policy engine.** Rules (e.g., "leave requests > 5 days require manager approval") live in `app/policy/` as plain Python/YAML rules evaluated BEFORE tool execution, never in prompts. Provide a `PolicyEngine.validate(action, args) -> Decision(allowed, reasons)` interface and 2 example rules.
6. **Audit everything.** Append-only audit log table: timestamp, trace/conversation id, agent name, user input, tool called, tool args (redact PII fields marked sensitive), policy decision, approval decision, final outcome.
7. **Structured logging + request tracing.** Every request gets a trace ID propagated through agent, tools, policy, and audit layers.
8. **Environment-driven model provider.** Implement a provider abstraction:

- `app/core/models.py` exposes `get_chat_model(env: str)` returning a configured Agno model instance, chosen by the ENVIRONMENT variable (default "dev").
- Local dev (ENVIRONMENT=dev) → Groq (GROQ_API_KEY from .env). Production (ENVIRONMENT=production) → OpenAI (OPENAI_API_KEY).
- Model IDs per provider must live in config (e.g., Groq: llama-3.3-70b-versatile or current Groq default; OpenAI: gpt-4o-mini or similar), overridable via env vars like MODEL_PRIMARY_GROQ, MODEL_PRIMARY_OPENAI.
- Every agent definition takes its model via this factory — no agent file may import a provider SDK directly or hardcode a model string.
- Structure config so a future provider (Anthropic, local vLLM, Azure) is a new factory branch + 2 env vars, nothing more. Add a commented example in config.py.
8b. **Provider fallback config.** Define primary/fallback model pairs per environment in config (e.g., if the primary model errors or rate-limits, retry once with the fallback). Even if only one model per environment is wired now, the config shape and retry hook must exist and be unit-tested with a mocked failing provider.

9. **Testing from day one.** Include: unit tests for policy engine, tool registry, and model factory; one integration test running the Supervisor agent end-to-end with a MOCKED model (inject canned responses so CI doesn't call a real LLM), and one test proving the approval flow blocks execution until approved.
10. **Docker-compose** with app + postgres services, Alembic initial migration creating: employees, audit_log, approvals, conversations tables.

## Folder structure to create

Standard layout as follows (you may refine minor details if justified):

- app/core/ — config, logging, exceptions, trace IDs, models.py (provider factory)
- app/agents/ — Agno-specific agent definitions + registry
- app/orchestrator/ — supervisor routing logic (Agno Team or equivalent)
- app/tools/ — base classes, schemas, per-domain subfolders (employee/, leave/), registry with auto-discovery
- app/policy/ — engine + rules
- app/approval/ — queue + API handlers
- app/db/ — SQLAlchemy models, session, migrations
- app/interfaces/api/ — FastAPI routes (chat endpoint, approval endpoints, health)
- evals/ — placeholder structure with 2 example eval cases in JSONL, runnable against either provider
- tests/ — unit/, integration/, fixtures/
- scripts/ — seed demo data, run evals placeholder
- docs/ — architecture.md, how-to-add-a-tool.md
- .env.example (containing: ENVIRONMENT=dev, GROQ_API_KEY=, OPENAI_API_KEY=, MODEL_PRIMARY_GROQ=, MODEL_PRIMARY_OPENAI=, DATABASE_URL=, LOG_LEVEL=)
- pyproject.toml (uv), docker-compose.yml, Makefile with: setup, migrate, run, test

## Acceptance criteria

- `make setup && make migrate && make run` brings up the API with a working /chat endpoint (using Groq when ENVIRONMENT=dev or unset, OpenAI when ENVIRONMENT=production).
- POST /chat with "What is my leave balance?" routes through supervisor -> leave_agent -> tool (mocked model in tests; real provider via env key in dev).
- POST /chat with a leave request creates an Approval row and does NOT execute until the approval endpoint is called, then executes and writes audit entries for both steps.
- Switching providers requires changing only ENVIRONMENT and the corresponding API key in .env — no code changes. Verify this by a test asserting the factory returns the correct provider class per environment.
- All tests pass: `make test`. No LLM calls happen in CI tests.
- Verify against Agno's current documentation for correct import paths and idiomatic usage, including how Agno instantiates models for Groq and OpenAI providers (https://docs.agno.com). If a doc link is needed, fetch the docs and follow the latest stable API. Where the docs are ambiguous, prefer simple, explicit code over clever abstractions.

## What NOT to build

- No frontend, no Slack/email integrations, no vector DB, no guardrails/PII filtering, no sandboxed code execution — leave clearly marked TODO stubs in docs/architecture.md instead. This is the backbone phase only.

Start by creating the full directory structure and all files. Write complete, working code — no placeholder pass-throughs except where marked as TODO above.