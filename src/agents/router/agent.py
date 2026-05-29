from langchain_core.messages import SystemMessage
from src.schemas.state import AgentState
from src.llm.config import get_model, get_system_prompt_for_agent
from src.tools.kitchen_tools import control_oven
from src.tools.caderno import read_notes
from langchain_core.runnables.config import RunnableConfig

# 1. Configuração de Personalidade
SYSTEM_PROMPT = get_system_prompt_for_agent("router")


tools = [control_oven, read_notes]

model = get_model().bind_tools(tools)

def call_router(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Nó do Router: Decide qual agente deve processar a tigela com base no 
    estado atual e nas mensagens.

    """
    current_messages = list(state.get("messages", []))
    
    if not current_messages or not isinstance(current_messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + current_messages
    else:
        messages = current_messages

    response = model.invoke(messages, config=config)

    res_content = response.content
    updates = {"messages": [response]}

    # rescreva essa logica para extrair o status do nó.


    if 'ESTADO_STATUS: "batida"' in res_content:
        updates["status_massa"] = "batida"
    elif 'ESTADO_STATUS: "assada"' in res_content:
        updates["status_massa"] = "assada"

    return updates