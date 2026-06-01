from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.prebuilt.tool_node import tools_condition, ToolNode
from langgraph.pregel.main import BaseCheckpointSaver
from typing import Optional

from src.schemas.state_example import State
from src.agents.example.agent import call_example


def build_graph(
    checkpointer: Optional[BaseCheckpointSaver] = None,
) -> CompiledStateGraph:
    builder = StateGraph(
        state_schema=State,
        input_schema=State,
        output_schema=State,
    )

    builder.add_node("call_example", call_example)
    builder.add_node("tools", ToolNode([]))

    builder.add_edge(START, "call_example")
    builder.add_conditional_edges("call_example", tools_condition, ["tools", END])
    builder.add_edge("tools", "call_example")

    # If no checkpointer is provided, compile without one so the
    # LangGraph API/platform can manage persistence itself.
    if checkpointer is None:
        return builder.compile()

    return builder.compile(checkpointer=checkpointer)


# Export a default `app` without a custom checkpointer so the
# LangGraph API can inject its own persistence implementation.
app = build_graph()