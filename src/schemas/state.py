from typing import List, Annotated, TypedDict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class AgentState(TypedDict):
    """
    A Tigela (Estado Central): guarda tudo o que está acontecendo.
    """
    # Histórico de conversas
    messages: Annotated[List[BaseMessage], add_messages]
    
    # A Tigela: Acumula ingredientes e transformações
    tigela: List[str]
    
    # Status de evolução (A anatomia do bolo)
    status_massa: Literal["crua", "batida", "assando", "assada", "decorada"]
    
    # Metadados de controle
    temperatura_forno: int
    nota_inspetor: float