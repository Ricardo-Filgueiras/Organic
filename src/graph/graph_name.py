from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.pregel.main import BaseCheckpointSaver
from typing import Optional

from src.schemas.state_name import State, InputState
from src.agents.name.agent import call_name
from src.agents.namesub.agent import call_namesub
from src.agents.router.agent import call_router

def graph_name(
    checkpointer: Optional[BaseCheckpointSaver] = None,
) -> CompiledStateGraph:
    builder = StateGraph(
        state_schema=State,
        input_schema=InputState,
        output_schema=State,
    )

    builder.add_node("router", call_router)
    builder.add_node("name", call_name)
    builder.add_node("namesub", call_namesub)

    builder.add_edge(START, "router")
    builder.add_edge("router", "name")
    builder.add_edge("name", "namesub")
    builder.add_edge("namesub", END)

    return builder.compile(checkpointer=checkpointer)

app = graph_name()