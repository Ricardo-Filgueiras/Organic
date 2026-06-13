# Arquitetura e Fluxo de Trabalho (Organic)

Esta documentação descreve a arquitetura atual do projeto: como os agentes são construídos, qual fluxo está ativo hoje e como o estado/memória é gerenciado entre usuários.

## Visão Geral

O projeto é um sistema multi-agente baseado em **LangChain (`create_agent`) + LangGraph**. Cada agente vive em `src/agents/<agente>/` com dois arquivos:

- `agent.py`: constrói o agente via `create_agent(model=..., tools=[...], system_prompt=...)` e expõe uma variável `agent` (entry point).
- `system_prompt.md`: prompt do agente, carregado e cacheado por `get_system_prompt_for_agent()` em `src/llm/config.py`.

Essa convenção está descrita em `.agent/skills/langchain-agent/SKILL.md`.

## Fluxo Ativo: ChatAgent (`src/agents/chat/`)

O fluxo principal hoje é o **ChatAgent**, um assistente de brainstorming que conversa com o usuário sobre ideias de produtos/objetos/pessoas.

- `src/agents/chat/agent.py` exporta:
  - `agent`: instância padrão (sem checkpointer).
  - `build_chat_agent(checkpointer=None)`: factory usada para anexar o checkpointer da sessão.
- `src/graph/graph_chat.py` apenas encapsula `build_chat_agent(checkpointer)` — não há nós/edges manuais; `create_agent` já constrói o loop de tool-calling internamente.
- Atualmente o ChatAgent **não possui tools** (`tools=[]`). A antiga tool `extract_product_details`, que acionava um sub-grafo de extração (`router → name → namesub`), foi removida junto com esse sub-grafo e ainda não tem substituto.

## Agentes não conectados (mantidos para uso futuro)

### RouterAgent (`src/agents/router/`)

Responsável por normalizar a entrada bruta do usuário (corrigir ortografia, espaçamento, capitalização) via saída estruturada (`RouterOutput` em `src/schemas/models.py`). Estado em `src/schemas/state_router.py` (`messages` + `normalized_input`).

Não está plugado a nenhum grafo no momento — é o candidato natural a primeiro passo de uma futura pipeline de extração.

### ExampleAgent (`src/agents/example/`)

Agente "esqueleto" usado como **template** para novos agentes baseados em `StateGraph` clássico (não `create_agent`). Usa `src/schemas/state.py` (`AgentState`) e `src/graph/graph_build.py` como referência de wiring (nó + `ToolNode` vazio + conditional edges).

## Configuração de LLMs (`src/llm/config.py`)

`get_model(role)` retorna o modelo conforme o papel do agente:

- `role="chat"` → variável de ambiente `CHAT_MODEL` (default `ollama:llama3.1:8b`)
- `role="extraction"` (default) → `EXTRACTION_MODEL` (default `ollama:granite4.1:3b`)

Ambos validam contra o servidor Ollama (`OLLAMA_API_URL`) na inicialização e emitem aviso caso o modelo não esteja disponível localmente. Modelos em nuvem (OpenAI, Anthropic, Google) são suportados via `init_chat_model` — basta apontar `CHAT_MODEL`/`EXTRACTION_MODEL` para, por exemplo, `openai:gpt-4o` e configurar a respectiva API key.

## Gerenciamento de Estado e Memória

- **Checkpointer**: `src/llm/checkpointer.py` expõe `build_checkpointer_sqlite` (usado por `main.py`) e `build_checkpointer_psql`. Ambos implementam `BaseCheckpointSaver` e persistem o histórico de mensagens por `thread_id`.
- **Isolamento multi-usuário (`thread_id`)**: cada sessão de usuário recebe um UUID próprio, passado via `RunnableConfig(configurable={"thread_id": ...})`. Isso permite múltiplas conversas simultâneas sem colisão de histórico.

## Interface de Teste e Validação (CLI)

`src/main.py` é o ponto de entrada para testes interativos via terminal:

```bash
python -m src.main
```

Funcionamento:
1. Apresenta 3 "usuários simulados", cada um com seu UUID (`thread_id`).
2. O usuário escolhe com qual perfil interagir (1, 2 ou 3).
3. Cada mensagem digitada é enviada ao `graph_chat` (ChatAgent) com o `thread_id` daquele perfil.
4. A resposta da LLM é impressa formatada (via `rich`).
5. Ao digitar `q`/`quit`/`/encerrar`, o script encerra e mostra quantas mensagens ficaram salvas no checkpointer de cada usuário.

## Status dos Pilares de Construção de Agentes (`create_agent`)

Checklist dos conceitos centrais ao construir agentes com `create_agent`, e o que já existe (ou não) neste projeto:

| Pilar | Status | Onde / Observação |
|---|---|---|
| **State (memória de curto prazo)** | ✅ Implementado | `AgentState` padrão (`messages`) usado pelo ChatAgent. |
| **Checkpointer (persistência por sessão)** | ✅ Implementado | `src/llm/checkpointer.py`, injetado via `build_chat_agent(checkpointer)` / `graph_chat`. |
| **System prompt** | ✅ Implementado (estático) | `system_prompt.md` por agente, via `get_system_prompt_for_agent()`. Variante dinâmica (`dynamic_prompt`) não usada. |
| **Structured output (`response_format`)** | ⚠️ Parcial | RouterAgent usa `with_structured_output` (padrão antigo), não o `response_format` do `create_agent`. |
| **Observabilidade (LangSmith)** | ⚠️ Parcial | Variáveis `LANGSMITH_API_KEY`/`LANGSMITH_TRACING` configuráveis via `.env`, mas não confirmado/validado em uso. |
| **Tools** | ❌ Não implementado | ChatAgent está com `tools=[]`. Candidato: `MarkdownWriter` (`src/tools/writer_filer.py`). |
| **Store (memória cross-thread)** | ❌ Não implementado | Nenhum `store=` configurado; preferências/perfis não persistem entre threads. |
| **Middleware** (`wrap_model_call`, `model_fallback`, `model_retry`, limites) | ❌ Não implementado | Nenhum middleware registrado em `create_agent`. |
| **Context/Runtime** (`context_schema`, `ToolRuntime`) | ❌ Não implementado | Sem `context_schema`; tools (quando existirem) não recebem `runtime.context`. |
| **Human-in-the-loop** | ❌ Não implementado | `HumanInTheLoopMiddleware` não usado. |

## Próximos Passos (Possíveis)

- Reprojetar a pipeline de extração de nomes (agentes `name`/`namesub`, removidos) seguindo a convenção `create_agent`, reaproveitando o `RouterAgent` como primeiro passo.
- Definir e conectar tools ao ChatAgent (ex.: `MarkdownWriter` em `src/tools/writer_filer.py`).
- Testes automatizados com `pytest` usando `thread_id`s simulados.
- Exposição do grafo via API HTTP assíncrona (FastAPI/LangServe).
