from langgraph.graph.state import CompiledStateGraph

from src.agents.brainstorm.agent import agent, build_brainstorm_agent
from src.schemas.models import BrainstormOutput


def test_build_brainstorm_agent_returns_compiled_graph():
    built = build_brainstorm_agent()
    assert isinstance(built, CompiledStateGraph)


def test_agent_entry_point_is_compiled_graph():
    assert isinstance(agent, CompiledStateGraph)


def test_agent_state_schema_exposes_pipeline_fields():
    input_properties = agent.get_input_jsonschema().get("properties", {})

    assert "messages" in input_properties
    assert "brainstorm_output" in input_properties
    assert "structure_output" in input_properties
    assert "draft_content" in input_properties
    assert "published_path" in input_properties


def test_agent_output_schema_includes_structured_response():
    output_properties = agent.get_output_jsonschema().get("properties", {})

    assert "structured_response" in output_properties


def test_brainstorm_output_schema_has_expected_fields():
    fields = BrainstormOutput.model_fields

    assert set(fields) == {"tema", "publico_alvo", "pontos_chave"}
