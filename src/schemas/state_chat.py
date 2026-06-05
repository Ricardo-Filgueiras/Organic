from collections.abc import Sequence
from typing import Annotated, TypedDict

from langgraph.graph.message import BaseMessage, add_messages


class ChatState(TypedDict):
    """Estado do grafo conversacional.
    Armazena apenas o histórico de mensagens entre o usuário e o chatbot.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
