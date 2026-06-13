from collections.abc import Sequence
from typing import Annotated, TypedDict

from langgraph.graph.message import BaseMessage, add_messages


class State(TypedDict):
    """Estado do RouterAgent: histórico de mensagens e entrada normalizada."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    normalized_input: str
