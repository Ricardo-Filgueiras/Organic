from typing import Optional

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.main import BaseCheckpointSaver

from src.llm.config import get_model, get_system_prompt_for_agent

SYSTEM_PROMPT = get_system_prompt_for_agent("chat")

model = get_model(role="chat")


def build_chat_agent(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledStateGraph:
    """Constrói o ChatAgent: assistente de brainstorming do projeto Organic."""
    return create_agent(
        model=model,
        tools=[],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )


# Entry point padrão, sem checkpointer próprio.
agent = build_chat_agent()
