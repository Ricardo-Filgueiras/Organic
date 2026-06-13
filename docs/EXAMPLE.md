# Exemplos e Guia de Execução

Este guia demonstra como configurar, testar e executar os fluxos da **Organic Intelligence Engine** localmente.

---

## ⚙️ Configuração do Ambiente

Antes de executar o projeto, configure as variáveis de ambiente necessárias. Copie o arquivo `.env.example` para `.env`:

```bash
copy .env.example .env
```

Abra o arquivo `.env` e configure as variáveis:

| Variável | Valor Padrão | Descrição |
|---|---|---|
| `CHAT_MODEL` | `ollama:llama3.1:8b` | Modelo LLM usado pelo ChatAgent principal |
| `EXTRACTION_MODEL` | `ollama:granite4.1:3b` | Modelo para outros agentes standalone (como o router) |
| `DB_DSN` | `data/database.db` | Caminho do arquivo SQLite (ou DSN PostgreSQL) para memória persistente |
| `OLLAMA_API_URL` | `http://localhost:11434` | Endpoint do seu servidor Ollama local |

!!! note "Servidores de LLM locais vs. Nuvem"
    * Para usar modelos locais, certifique-se de que o **Ollama** está rodando em sua máquina e possui os modelos instalados (`ollama run llama3.1:8b`).
    * Para usar modelos em nuvem (como OpenAI, Anthropic ou Google), basta apontar as variáveis de modelo (ex: `CHAT_MODEL=openai:gpt-4o`), configurar a API Key correspondente no `.env` (ex: `OPENAI_API_KEY`) e o sistema fará a inicialização automática via `init_chat_model`.

---

## 🚀 Executando o Smoke Test

Você pode rodar um teste básico do **ChatAgent** (que valida a conexão com o LLM e o funcionamento do fluxo de mensagens) executando o script `src/main.py`:

```bash
python -m src.main
```

A saída esperada será algo como:

```text
🤖 ChatAgent:
Olá! Sim, estou funcionando perfeitamente. Como posso te ajudar hoje com a inteligência orgânica ou brainstorming?
```

---

## 🎨 Utilizando o LangGraph Studio

Para interagir com o ChatAgent de forma visual, debugar fluxos e inspecionar o histórico de execução de maneira completa, você pode usar o **LangGraph Studio**:

1. Garanta que o LangGraph CLI está instalado (ele já vem listado nas dependências de desenvolvimento do projeto).
2. Execute o comando de desenvolvimento na raiz do projeto:

```bash
langgraph dev
```

3. Abra o link fornecido no seu navegador para acessar a interface visual do LangGraph Studio. O grafo será carregado dinamicamente a partir de `langgraph.json` que expõe:
    * `chat`: O grafo do ChatAgent (`src/graph/graph_chat.py:app`).
    * `example`: O grafo esqueleto/template (`src/graph/graph_build.py:app`).

---

## 📚 Gerando e Visualizando a Documentação Localmente

Como a documentação agora está configurada com o **MkDocs**, você pode subir um servidor local para visualizar as páginas com o tema premium e responsivo.

### Iniciar o servidor de desenvolvimento
Execute o comando a seguir na raiz do projeto:

```bash
uv run mkdocs serve
```

Isso iniciará um servidor local em `http://127.0.0.1:8000/`. Qualquer alteração nos arquivos `.md` dentro da pasta `docs/` será recarregada automaticamente no navegador (hot-reload).

### Gerar os arquivos HTML de produção
Para exportar a documentação no formato HTML estático e publicá-la em qualquer lugar (como GitHub Pages, Netlify ou servidor interno):

```bash
uv run mkdocs build
```

Os arquivos HTML estáticos serão gerados na pasta `site/` na raiz do projeto.
