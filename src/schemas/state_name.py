from collections.abc import Sequence
from typing import Annotated, TypedDict, List

from langgraph.graph.message import BaseMessage, add_messages


class InputState(TypedDict):
    """Schema mínimo aceito na entrada do grafo — apenas a mensagem do usuário."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


class State(TypedDict):
    """Estado completo do grafo com todos os campos gerados pelos agentes."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    normalized_input: str
    name: List[str]
    subname: List[str]
    Description: List[str]