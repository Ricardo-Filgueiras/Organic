from langchain_core.messages import SystemMessage
from src.schemas.state import AgentState
from src.llm.config import get_model, get_system_prompt_for_agent
from langchain_core.runnables.config import RunnableConfig

# 1. Configuração de Personalidade
SYSTEM_PROMPT = get_system_prompt_for_agent("example")

# tools = [control_oven, read_notes]

model = get_model() #.bind_tools(tools)

def call_example(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Nó do Agent Exemplo: Lê a tigela, consulta o caderno e executa a transformação.
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

    # if 'ESTADO_STATUS: "batida"' in res_content:
    #     updates["status_massa"] = "batida"
    # elif 'ESTADO_STATUS: "assada"' in res_content:
    #     updates["status_massa"] = "assada"

    return updates