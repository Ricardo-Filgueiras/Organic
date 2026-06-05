from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from src.schemas.state_chat import ChatState
from src.llm.config import get_model
from src.graph.graph_name import graph_name as build_extraction_graph

# Inicializa o grafo de extração (ele será o nosso Sub-Grafo acionado pela Tool)
extraction_app = build_extraction_graph()

@tool
async def extract_product_details(description: str, config: RunnableConfig) -> str:
    """Acione esta ferramenta QUANDO e SOMENTE QUANDO a ideia do usuário estiver madura e pronta para ser processada na fábrica de extração de nomes.
    Passe a descrição finalizada e detalhada do produto como argumento.
    """
    # Acionamos o sub-grafo de extração passando o input do usuário
    # O `config` é repassado para manter o rastro (opcionalmente)
    result = await extraction_app.ainvoke(
        {"messages": [HumanMessage(content=description)]}, 
        config=config
    )
    
    names = result.get("name", [])
    subnames = result.get("subname", [])
    desc = result.get("Description", [])
    
    # Retornamos o resultado estruturado de volta para o Chatbot ler e informar o usuário
    return f"SUCESSO! Extração concluída pela fábrica.\nNomes Gerados: {names}\nSobrenomes/Variantes: {subnames}\nDescrição Final: {desc}"

tools = [extract_product_details]

# Ligamos as ferramentas à nossa LLM
model = get_model(role="chat").bind_tools(tools)

SYSTEM_PROMPT = """Você é um assistente criativo de Brainstorming do projeto Organic.
Seu objetivo é ajudar o usuário a formatar e detalhar ideias de produtos, objetos ou pessoas.
Faça perguntas pertinentes se a ideia for muito vaga.
QUANDO a ideia estiver clara e o usuário pedir para gerar, ou disser que está pronto, você DEVE chamar a ferramenta `extract_product_details` passando a descrição completa da ideia.
IMPORTANTE: Não tente inventar nomes ou descrições por conta própria! Use SEMPRE a ferramenta `extract_product_details` para fazer a extração oficial.
Quando a ferramenta retornar os dados, repasse-os ao usuário de forma amigável e comemore o resultado.
"""

async def call_chatbot(state: ChatState, config: RunnableConfig) -> dict:
    """Nó do Chatbot: Avalia o histórico, interage com o usuário e decide se chama a ferramenta."""
    messages = state.get("messages", [])
    
    # Injeta o System Prompt no início, se não existir
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
    response = await model.ainvoke(messages, config=config)
    
    return {"messages": [response]}
