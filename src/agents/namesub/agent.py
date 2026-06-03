from langchain_core.messages import SystemMessage, HumanMessage
from src.schemas.state_name import State
from src.schemas.models import NameSubOutput
from src.llm.config import get_model, get_system_prompt_for_agent
from langchain_core.runnables.config import RunnableConfig

SYSTEM_PROMPT = get_system_prompt_for_agent("namesub")
model = get_model().with_structured_output(NameSubOutput)

def call_namesub(state: State, config: RunnableConfig) -> dict:
    """
    Nó do Agent NomeSub: Gera sobrenomes e descrição com base no input e nomes anteriores.
    """
    normalized_input = state.get("normalized_input", "")
    names = state.get("name", [])
    
    names_str = ", ".join(names) if names else "None"
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Normalized Input:\n{normalized_input}\n\nGenerated Names:\n{names_str}")
    ]

    response: NameSubOutput = model.invoke(messages, config=config)
    
    return {"subname": response.subname, "Description": response.Description}