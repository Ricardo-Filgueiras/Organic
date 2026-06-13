# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the main interactive chatbot
python -m src.main

# Install dependencies (Python 3.13+ required)
pip install -e .
# or
pip install -r requirements.txt

# Run tests
pytest
```

## Environment Setup

Copy `.env.example` to `.env` and fill in values. Key variables read by the code:

| Variable | Default | Purpose |
|---|---|---|
| `CHAT_MODEL` | `ollama:llama3.1:8b` | LLM used by the chat agent |
| `EXTRACTION_MODEL` | `ollama:granite4.1:3b` | LLM used by other (non-chat) agents, e.g. router |
| `DB_DSN` | `data/database.db` | SQLite path (or Postgres DSN) for checkpointer |
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama server URL |

Ollama must be running locally for the default model configuration. Cloud models (OpenAI, Anthropic, Google) are supported via `langchain.chat_models.init_chat_model` — set the appropriate API key and change the model env vars to e.g. `openai:gpt-4o`.

## Architecture

This project is an **Organic Intelligence Engine** — a multi-agent LangChain/LangGraph system that transforms business intelligence into strategic content and product naming.

### Agent convention (`langchain.agents.create_agent`)

Agents are built with `create_agent` from `langchain.agents` (see `.agent/skills/langchain-agent/SKILL.md` for the full convention):

- Each agent lives in `src/agents/<agent>/` with `agent.py` and `system_prompt.md`.
- `agent.py` exposes a module-level `agent` (built via `create_agent(model=..., tools=[...], system_prompt=...)`) and, where a checkpointer is needed, a `build_<agent>_agent(checkpointer=None)` factory.
- System prompts are loaded via `get_system_prompt_for_agent(agent_type)` from `src/llm/config.py`, cached in-process.

### Main graph (`graph_chat`, `src/main.py`)

- `src/graph/graph_chat.py` wraps `build_chat_agent(checkpointer)` from `src/agents/chat/agent.py`. The chat agent currently has no tools — it's a brainstorming assistant that converses with the user.
- Persisted with `AsyncSqliteSaver` (or Postgres); per-user sessions keyed by `thread_id`.

### Other agents

- `src/agents/router/`: normalizes raw user input via structured output (`RouterOutput` in `src/schemas/models.py`, state in `src/schemas/state_router.py`). Not currently wired into a graph — kept for future use (e.g. as the entry step of a future extraction pipeline).
- `src/agents/example/`: minimal scaffold agent kept as a template for building new agents. Uses `src/schemas/state.py` (`AgentState`) and `src/graph/graph_build.py` as the reference graph wiring.

### LLM configuration (`src/llm/config.py`)

`get_model(role)` returns different models by role:
- `role="chat"` → `CHAT_MODEL` env var
- `role="extraction"` (default) → `EXTRACTION_MODEL` env var

Both validate against Ollama at startup and warn if not found.

### Checkpointer

`src/llm/checkpointer.py` exports three factory functions. `main.py` uses `build_checkpointer_sqlite` (async context manager). Switch to `build_checkpointer_psql` for Postgres by setting `DB_DSN` to a valid Postgres connection string.

### Tools

`src/tools/writer_filer.py` provides `MarkdownWriter` for writing agent output to `.md` files (not currently wired into any agent). `src/skills/artigo/` is a placeholder skill directory for future article-generation capability.
