from typing import Optional

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.main import BaseCheckpointSaver

from src.llm.config import get_model, get_system_prompt_for_agent
from src.schemas.models import StructureOutput
from src.schemas.state_pipeline import PipelineState

SYSTEM_PROMPT = get_system_prompt_for_agent("structure")

model = get_model(role="chat")


def build_structure_agent(checkpointer: Optional[BaseCheckpointSaver] = None) -> CompiledStateGraph:
    """Constrói o StructureAgent: segunda etapa da pipeline de criação de artigos."""
    return create_agent(
        model=model,
        tools=[],
        system_prompt=SYSTEM_PROMPT,
        state_schema=PipelineState,
        response_format=StructureOutput,
        checkpointer=checkpointer,
    )


# Entry point padrão, sem checkpointer próprio.
agent = build_structure_agent()
