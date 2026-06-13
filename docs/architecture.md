# Arquitetura e Fluxo de Trabalho (Organic)

Esta documentação descreve a arquitetura do projeto: como os agentes são construídos, quais fluxos estão ativos hoje e como o estado/memória é gerenciado.

---

## Visão Geral

O projeto é um sistema multi-agente baseado em **LangChain (`create_agent`) + LangGraph**. Cada agente vive em `src/agents/<agente>/` com dois arquivos:

- `agent.py`: constrói o agente via `create_agent(model=..., tools=[...], system_prompt=...)` e expõe uma variável `agent` (entry point).
- `system_prompt.md`: prompt do agente, carregado e cacheado por `get_system_prompt_for_agent()` em `src/llm/config.py`.

Essa convenção está descrita em `.agent/skills/langchain-agent/SKILL.md`.

---

## Fluxos Ativos e Agentes

### 1. ChatAgent (`src/agents/chat/`)
Assistente de brainstorming genérico que conversa com o usuário sobre ideias de produtos/objetos/pessoas.
- `src/agents/chat/agent.py` exporta:
  - `agent`: instância padrão (sem checkpointer).
  - `build_chat_agent(checkpointer=None)`: factory usada para anexar o checkpointer da sessão.
- `src/graph/graph_chat.py` apenas encapsula `build_chat_agent(checkpointer)` — não há nós/edges manuais; `create_agent` já constrói o loop de tool-calling internamente.
- Atualmente o ChatAgent **não possui tools** (`tools=[]`).

### 2. BrainstormAgent (`src/agents/brainstorm/`)
A **primeira etapa** da pipeline contínua de criação de artigos. Ele conversa com o usuário para refinar uma ideia de post de blog até extrair informações suficientes para estruturar o artigo.
- `src/agents/brainstorm/agent.py` exporta:
  - `agent`: instância padrão (usada diretamente no LangGraph).
  - `build_brainstorm_agent(checkpointer=None)`: factory para injeção de checkpointer.
- **Saída Estruturada**: Envia a resposta no formato estruturado `BrainstormOutput` (Pydantic), contendo:
  - `tema`: Tema central do artigo.
  - `publico_alvo`: Público a quem se destina.
  - `pontos_chave`: Tópicos que o artigo deve cobrir.
- **Estado**: Baseado no `PipelineState` compartilhado.

### 3. StructureAgent (`src/agents/structure/`)
A **segunda etapa** da pipeline. Recebe a ideia refinada pelo BrainstormAgent (tema, público-alvo, pontos-chave) e a transforma em um outline/esqueleto de artigo.
- `src/agents/structure/agent.py` exporta:
  - `agent`: instância padrão (usada diretamente no LangGraph).
  - `build_structure_agent(checkpointer=None)`: factory para injeção de checkpointer.
- **Saída Estruturada**: `StructureOutput` (Pydantic), contendo:
  - `titulo`: Título proposto para o artigo.
  - `introducao`: Resumo do que a introdução deve abordar.
  - `secoes`: Lista ordenada de seções/tópicos do corpo do artigo.
  - `conclusao`: Resumo do que a conclusão deve abordar.
- **Estado**: Baseado no `PipelineState` compartilhado.

---

## Agentes não conectados (mantidos para uso futuro)

### RouterAgent (`src/agents/router/`)
Responsável por normalizar a entrada bruta do usuário (corrigir ortografia, espaçamento, capitalização) via saída estruturada (`RouterOutput` em `src/schemas/models.py`). Estado em `src/schemas/state_router.py` (`messages` + `normalized_input`).

### ExampleAgent (`src/agents/example/`)
Agente "esqueleto" usado como **template** para novos agentes baseados em `StateGraph` clássico (não `create_agent`). Usa `src/schemas/state.py` (`AgentState`) e `src/graph/graph_build.py` como referência de wiring (nó + `ToolNode` vazio + conditional edges).

---

## Configuração de LLMs (`src/llm/config.py`)

`get_model(role)` retorna o modelo conforme o papel do agente:

- `role="chat"` &rarr; variável de ambiente `CHAT_MODEL` (default `ollama:llama3.1:8b`)
- `role="extraction"` (default) &rarr; `EXTRACTION_MODEL` (default `ollama:granite4.1:3b`)

Ambos validam contra o servidor Ollama (`OLLAMA_API_URL`) na inicialização. Modelos em nuvem (OpenAI, Anthropic, Google) são suportados via `init_chat_model` — basta apontar `CHAT_MODEL`/`EXTRACTION_MODEL` para, por exemplo, `openai:gpt-4o` e configurar a respectiva API key.

---

## Gerenciamento de Estado e Memória

### Checkpointer
`src/llm/checkpointer.py` expõe `build_checkpointer_sqlite` (usado por `main.py`) e `build_checkpointer_psql`. Ambos persistem o histórico de mensagens por `thread_id`. O isolamento multi-usuário é feito passando um UUID próprio em `RunnableConfig(configurable={"thread_id": ...})`.

### Estados Específicos
* **`AgentState`** (`src/schemas/state.py`): Estado padrão com a lista de mensagens do chat.
* **`PipelineState`** (`src/schemas/state_pipeline.py`): Estado compartilhado para a pipeline de artigos. Contém:
  - `brainstorm_output`: Saída de refino gerada pelo BrainstormAgent.
  - `structure_output`: Estrutura de tópicos do artigo.
  - `draft_content`: Rascunho final do artigo.
  - `published_path`: Caminho do arquivo markdown salvo.

---

## Interface de Teste e Validação

### LangGraph Studio (`langgraph dev`)
A forma principal de debugar os agentes. O arquivo `langgraph.json` registra os seguintes caminhos:

- `chat`: `src/graph/graph_chat.py:app` &mdash; Grafo do ChatAgent.
- `brainstorm`: `src/agents/brainstorm/agent.py:agent` &mdash; Grafo do BrainstormAgent.
- `structure`: `src/agents/structure/agent.py:agent` &mdash; Grafo do StructureAgent.
- `example`: `src/graph/graph_build.py:app` &mdash; Grafo modelo (exemplo).

```bash
langgraph dev
```

### Smoke test (`src/main.py`)
Script mínimo para validar que o ChatAgent responde no console localmente:

```bash
python -m src.main
```

---

## Status dos Pilares de Construção de Agentes (`create_agent`)

| Pilar | Status | Onde / Observação |
|---|---|---|
| **State (memória de curto prazo)** | ✅ Implementado | `AgentState` para chats e `PipelineState` para o fluxo de artigos. |
| **Checkpointer (persistência)** | ✅ Implementado | `src/llm/checkpointer.py`, injetado via factories. |
| **System prompt** | ✅ Implementado (estático) | Carregados de `system_prompt.md` específicos por agente. |
| **Structured output (`response_format`)** | ✅ Implementado | O novo BrainstormAgent utiliza `BrainstormOutput` (Pydantic). RouterAgent usa o modelo antigo. |
| **Observabilidade (LangSmith)** | ⚠️ Parcial | Suporte nativo por variáveis `.env`, não verificado em produção. |
| **Tools** | ❌ Não implementado | O script de salvar artigos (`save_article` em `src/tools/writer_filer.py`) existe, mas ainda não está plugado nos agentes. |
| **Store (memória cross-thread)** | ❌ Não implementado | Nenhum `store` configurado para persistência cross-thread. |
| **Middleware** | ❌ Não implementado | Nenhum middleware registrado no `create_agent`. |

---

## Próximos Passos da Pipeline de Artigos

- Implementar e conectar os próximos agentes da pipeline (Escrita e Publicação) usando o `PipelineState`.
- Plugar a tool `save_article` ao agente de escrita/publicação para persistir os textos gerados na pasta `data/articles/`.
- Definir o grafo orquestrador (`graph_pipeline.py`) que encadeia brainstorm → estruturação → escrita → publicação e mapeia `structured_response` de cada etapa para o campo correspondente do `PipelineState`.
