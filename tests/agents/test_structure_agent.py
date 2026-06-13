from langgraph.graph.state import CompiledStateGraph

from src.agents.structure.agent import agent, build_structure_agent
from src.schemas.models import StructureOutput


def test_build_structure_agent_returns_compiled_graph():
    built = build_structure_agent()
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


def test_structure_output_schema_has_expected_fields():
    fields = StructureOutput.model_fields

    assert set(fields) == {"titulo", "introducao", "secoes", "conclusao"}
