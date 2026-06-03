from langchain_core.messages import SystemMessage, HumanMessage
from src.schemas.state_name import State
from src.schemas.models import NameOutput
from src.llm.config import get_model, get_system_prompt_for_agent
from langchain_core.runnables.config import RunnableConfig

SYSTEM_PROMPT = get_system_prompt_for_agent("name")
model = get_model().with_structured_output(NameOutput)

def call_name(state: State, config: RunnableConfig) -> dict:
    """
    Nó do Agent Nome: Recebe a entrada normalizada e gera nomes estruturados.
    """
    normalized_input = state.get("normalized_input", "")
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Normalized Input:\n{normalized_input}")
    ]

    response: NameOutput = model.invoke(messages, config=config)
    
    return {"name": response.name}