# Changelog

## 2026-06-13

- Refatoração para a convenção `create_agent` (`.agent/skills/langchain-agent/SKILL.md`):
  - `ChatAgent` (`src/agents/chat/`) reescrito com `create_agent`, exportando `agent` e `build_chat_agent(checkpointer)`.
  - `src/graph/graph_chat.py` simplificado para apenas encapsular `build_chat_agent(checkpointer)`.
- Removida a tool `extract_product_details` e o sub-grafo de extração (`graph_name`, agentes `name`/`namesub`, `state_name.py`) — serão reprojetados futuramente.
- `RouterAgent` mantido como agente standalone para uso futuro; corrigido import quebrado criando `src/schemas/state_router.py`.
- `ExampleAgent` mantido como template de agente baseado em `StateGraph` clássico (não `create_agent`).
- Removida pipeline "kitchen" não implementada (`src/graph/pipeline.py`, `src/graph/edges.py`).
- Limpeza de configuração (`src/llm/config.py`): removidas variáveis mortas (`DATABASE_URL`, `BASE_MODEL`, `SYSTEM_PROMPT_PATH`) e fallback global de system prompt.
- Corrigido mix-up entre `src/agents/chat/system_prompt.md` e `src/agents/example/system_prompt.md` (conteúdos estavam trocados).
- `.env.example` atualizado para refletir as variáveis realmente lidas (`CHAT_MODEL`, `EXTRACTION_MODEL`, `DB_DSN`, `OLLAMA_API_URL`).
- `CLAUDE.md` e `docs/architecture.md` atualizados para descrever a arquitetura atual.
