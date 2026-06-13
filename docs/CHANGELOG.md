# Changelog

## 2026-06-13

- `langgraph.json`: grafo `kitchen` renomeado/substituído — agora registra `chat` (`src/graph/graph_chat.py:app`, fluxo ativo do ChatAgent) e `example` (`src/graph/graph_build.py:app`, template). Habilita uso do LangGraph Studio (`langgraph dev`) para interagir e debugar o ChatAgent, com tracing via LangSmith.
- `src/main.py` simplificado: o menu de usuários simulados foi removido; agora é um smoke test que invoca o ChatAgent uma vez. A interação/debug interativo passa a ser feita via LangGraph Studio.
- `src/tools/writer_filer.py` reescrito como tool `@tool save_article(filename, content)` (convenção `create_agent`), com sanitização de nome de arquivo (evita path traversal) e diretório de saída configurável via `ARTICLES_DIR` (`src/llm/constants.py`, default `data/articles`). Reservada para um futuro WriterAgent (ChatAgent continua sem tools). Testes unitários em `tests/tools/test_writer_filer.py`.
- Iniciada a pipeline de criação de artigos (`brainstorm → estruturação → escrita → publicação`):
  - `src/schemas/state_pipeline.py`: `PipelineState` (subclasse de `AgentState`) define o contrato compartilhado entre os agentes da pipeline (`brainstorm_output`, `structure_output`, `draft_content`, `published_path`) — cada agente lê o campo da etapa anterior e escreve apenas o seu, permitindo adicionar/remover agentes do grafo sem alterar os demais.
  - `src/schemas/models.py`: novo `BrainstormOutput` (saída estruturada do BrainstormAgent: `tema`, `publico_alvo`, `pontos_chave`).
  - `src/agents/brainstorm/`: primeiro agente da pipeline (`create_agent` com `state_schema=PipelineState`, `response_format=BrainstormOutput`), com `system_prompt.md` e testes unitários em `tests/agents/test_brainstorm_agent.py`.
  - `langgraph.json`: registrado o grafo `brainstorm` (`src/agents/brainstorm/agent.py:agent`) para testar/debugar o BrainstormAgent isoladamente via LangGraph Studio.
  - `src/schemas/models.py`: novo `StructureOutput` (saída estruturada do StructureAgent: `titulo`, `introducao`, `secoes`, `conclusao`).
  - `src/agents/structure/`: segundo agente da pipeline (`create_agent` com `state_schema=PipelineState`, `response_format=StructureOutput`), com `system_prompt.md` e testes unitários em `tests/agents/test_structure_agent.py`. Registrado em `langgraph.json` como `structure`.

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
