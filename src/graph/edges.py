from src.schemas.state import AgentState
from langgraph.graph import END

# Este nó é responsável por decidir o fluxo, direcionando para o agente correto 
# com base no estado atual e nas mensagens. Ele atua como um "roteador" que 
# avalia as condições e determina o próximo passo lógico no processo.

def decide_next_step(state: AgentState) -> str:
    """
    Decide qual etapa do processo deve ser executada em seguida.

    """
    if state.get("etapa01") == "etapa01_concluida":
        return "etapa02"
    return "etapa01"

def evaluate_quality(state: AgentState) -> str:
    """
    ...

    """
    # Rever logica de avaliuação do fluxo
    
    nota = state.get("nota_inspetor", 0)
    if nota < 7:
        return "gather_ingredients" # Volta para o início se estiver ruim
    return END