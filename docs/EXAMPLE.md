# Pipeline Multi-Agents — EXEMPLO

## Visão Geral

- Objetivo: Receber uma descrição (objeto / pessoa / produto) do usuário e gerar um `name`, `subname` e `Description` através de uma esteira de agents: `router` → `name` → `namesub`.
- Ideia central: o `router` normaliza a entrada e decide o fluxo; `name` produz o nome principal; `namesub` produz sobrenome/variante e a descrição final.

## Componentes

- `router`: decide roteamento e normaliza entrada.
- `name`: gera o nome principal (campo `name`).
- `namesub`: gera sobrenome/variante e descrição (campos `subname`, `Description`).

Arquivos de referência: `src/agents/router/agent.py`, `src/agents/name/agent.py`, `src/agents/namesub/agent.py`.

## Estado e Schema

- Estado central com histórico de mensagens e campos estruturados (ex.: `messages`, `name`, `subname`, `Description`).
- Use o schema em `src/schemas/state_name.py` como referência para os campos esperados.

## Fluxo de Execução

1. START
2. `call_router` — recebe a mensagem do usuário e decide o próximo passo.
3. `call_name` — gera e retorna o `name`.
4. `call_namesub` — gera `subname` e `Description` final.
5. END

## Contrato dos Agents

- Entrada: recebe `state` e `config`.
- Comportamento: pré-pende `SYSTEM_PROMPT`, invoca o modelo e retorna atualizações de estado como dicionário, por exemplo:

	```json
	{"messages": [response], "name": ["NomeGerado"], "subname": ["Sobrenome"], "Description": ["Texto descritivo"]}
	```

- Recomenda-se exigir que o LLM responda em JSON estruturado para facilitar parsing.

## Prompting e System Prompts

- Cada agente deve ter um `system_prompt.md` claro solicitando saída JSON com exemplos e regras de formato.

## Validação e Sanitização

- Sempre parsear a resposta (JSON), validar campos e normalizar (trim, capitalização) antes de gravar no estado.

## Checkpointing e Idempotência

- Use `BaseCheckpointSaver` ou o checkpointer do LangGraph ao compilar o grafo para permitir retomadas seguras.

## Testes e Observabilidade

- Criar testes unitários que simulam entradas e verificam presença/formatos de `name`, `subname`, `Description`.
- Logar prompts, respostas e decisão do `router` para depuração e tuning de prompts.

## Exemplo de entrada/saída

- Entrada (usuário): {"input": "Um sofá modular, minimalista, tecido cinza, foco em conforto"}
- Saída esperada:

	```json
	{"name":["LoungeMinimal"], "subname":["GreyWeave"], "Description":["Sofá modular minimalista em tecido cinza, projetado para conforto..."]}
	```

## Próximos Passos

1. Aplicar este rascunho em `docs/EXAMPLE.md` (feito).
2. Atualizar `src/graph/graph_name.py` para adicionar nodes e arestas: `call_router`, `call_name`, `call_namesub`.
3. Ajustar agentes para retornarem campos estruturados no estado.
4. Criar testes básicos.

---
Favor revisar este rascunho e indicar alterações antes de eu modificar os códigos fonte.

