from typing import Optional

from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.main import BaseCheckpointSaver

from src.agents.chat.agent import build_chat_agent


def graph_chat(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledStateGraph:
    return build_chat_agent(checkpointer)


app = graph_chat()
