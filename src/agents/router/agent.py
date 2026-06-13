from langchain_core.messages import SystemMessage
from src.schemas.state_router import State
from src.schemas.models import RouterOutput
from src.llm.config import get_model, get_system_prompt_for_agent
from langchain_core.runnables.config import RunnableConfig

SYSTEM_PROMPT = get_system_prompt_for_agent("router")
model = get_model().with_structured_output(RouterOutput)

def call_router(state: State, config: RunnableConfig) -> dict:
    """
    Nó do Router: Normaliza a entrada e a repassa adiante.
    """
    current_messages = list(state.get("messages", []))
    
    if not current_messages or not isinstance(current_messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + current_messages
    else:
        messages = current_messages

    response: RouterOutput = model.invoke(messages, config=config)
    
    return {"normalized_input": response.normalized_input}