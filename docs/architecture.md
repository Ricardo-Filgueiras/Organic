# Arquitetura e Fluxo de Trabalho (Organic)

Esta documentação detalha a arquitetura construída, o fluxo dos agentes e o mecanismo de gerenciamento de estado para desenvolvimento multi-usuário da aplicação.

## Visão Geral do Pipeline (LangGraph)

O núcleo do projeto é uma esteira de agentes autônomos operando sob a orquestração do LangGraph. O objetivo central é receber a descrição de um item (produto, objeto, pessoa) em linguagem natural e processar essas informações extraindo e preenchendo as "lacunas" (propriedades estruturadas).

### 1. O Grafo de Agentes (`src/graph/graph_name.py`)
O fluxo é estritamente sequencial e segue os seguintes passos:

1. **`router`**: Recebe a entrada bruta do usuário, analisa, normaliza e decide o roteamento do fluxo de dados.
2. **`name`**: O agente principal focado em interpretar as intenções extraídas e gerar ou recuperar o nome principal (`name`) do item.
3. **`namesub`**: Um agente especialista invocado no final da esteira para processar os metadados gerados pelo `name`, gerando sobrenomes, variantes (`subname`) e redigindo a descrição final polida (`Description`).

### 2. Fluxo de Dados e Passagem de Contexto (Otimização de Tokens)
Um detalhe crucial desta arquitetura é como a informação flui de forma cirúrgica entre os nós, especialmente na transição do `name` para o `namesub`.

Embora o LangGraph armazene o histórico **completo** da conversa no array `messages` (através do Checkpointer), os agentes especialistas não processam esse histórico em suas execuções. O fluxo opera da seguinte maneira:
- O agente **`name`** extrai do estado global apenas o campo `normalized_input` (a entrada limpa pelo router).
- O agente **`namesub`** também não recebe o histórico da conversa, mas sim um prompt super focado contendo apenas o `normalized_input` e o array `name` preenchido no passo anterior pelo nó `name` (`state.get("name", [])`).

**Benefícios dessa abordagem:**
Ao enviar apenas recortes específicos do `State` em vez da conversa toda, nós garantimos que o prompt da LLM seja extremamente enxuto e focado na tarefa imediata. Essa estratégia corta custos (menor consumo de tokens), acelera radicalmente o tempo de resposta e previne o risco do modelo "alucinar" devido a ruídos de interações antigas presentes no histórico.

## Gerenciamento de Estado e Memória

Um dos pontos fortes do projeto é como a memória da conversa e os metadados extraídos são preservados e isolados. 

- **State Schema**: O estado transita por todos os nós contendo as mensagens da LLM e listas estruturadas (ex.: `name: list[str]`, `subname: list[str]`). 
- **Checkpointer (`SQLite / PostgreSQL`)**: Usando o `BaseCheckpointSaver`, todo o histórico é persistido localmente ou em banco de dados. Isso traz a propriedade de *idempotência* e recuperação rápida.

### Isolamento Multi-Usuários (`thread_id`)
Durante a fase de desenvolvimento/testes interativos pelo terminal, precisávamos garantir que as conversas de diferentes usuários não fossem mescladas no Checkpointer.

Para isso, o pipeline diferencia as sessões injetando um **UUID único** como `thread_id` na variável `configurable` do LangGraph.
```python
config = RunnableConfig(
    configurable={"thread_id": "98ebbae6-93c7-4d58-859f-006f814889bf"}
)
```
Isso permite que dezenas de sessões simultâneas operem sobre a mesma esteira sem vazamento de contexto ou colisão de histórico.

## Interface de Teste e Validação (CLI)

O arquivo `src/main.py` serve como o ponto de entrada para testes interativos em terminal. 

**Como executar:**
```bash
uv run src/main.py
```

**Como funciona a simulação:**
O script instancializa o checkpointer e inicia um loop interativo rico (usando a biblioteca `rich`). 
1. Apresenta uma lista de 3 "usuários simulados", cada um com seu UUID.
2. O desenvolvedor escolhe como qual usuário deseja interagir (1, 2 ou 3).
3. O desenvolvedor digita a "Descrição do Produto".
4. O `main.py` aciona a esteira LangGraph enviando o UUID daquele usuário como `thread_id`.
5. O retorno da LLM (`name`, `subname`, `Description` normalizados) é impresso colorizado na tela.
6. Ao digitar `q`, o script finaliza e exibe o estado da memória segmentada de todos os usuários utilizados.

## Próximos Passos (Possíveis)
- Criação de testes automatizados com `pytest` utilizando UUIDs simulados no setup.
- Exposição do Grafo através de uma API HTTP assíncrona (FastAPI/LangServe).
- Refinamento adicional dos prompts base (`system_prompts.md`).
