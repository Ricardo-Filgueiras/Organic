import os
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.schemas.state import AgentState
from src.graph.edges import evaluate_quality


def create_pipeline():
    """
    Pipeline futura com agentes sous_chef, confeiteiro e inspector.
    
    ATENÇÃO: Esta pipeline está em construção. Os agentes ainda não foram
    implementados. Não instanciar diretamente até a implementação estar completa.
    
    Fluxo planejado:
        START → sous_chef → confeiteiro → inspector → quality_check_logic → (END | sous_chef)
    """
    workflow = StateGraph(AgentState)

    # TODO: Implementar e registrar os agentes abaixo antes de ativar esta pipeline.
    # workflow.add_node("sous_chef", call_sous_chef)
    # workflow.add_node("confeiteiro", call_confeiteiro)
    # workflow.add_node("inspector", call_inspector)
    # workflow.add_node("sous_chef_tools", ToolNode(sous_chef_tools))
    # workflow.add_node("confeiteiro_tools", ToolNode(confeiteiro_tools))
    # workflow.add_node("inspector_tools", ToolNode(inspector_tools))

    # TODO: Descomentar fluxo quando os agentes estiverem implementados.
    # INÍCIO → SOUS CHEF
    # workflow.add_edge(START, "sous_chef")
    # workflow.add_conditional_edges(
    #     "sous_chef",
    #     lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
    #     {"tools": "sous_chef_tools", "continue": "confeiteiro"}
    # )
    # workflow.add_edge("sous_chef_tools", "sous_chef")

    # SOUS CHEF → CONFEITEIRO
    # workflow.add_conditional_edges(
    #     "confeiteiro",
    #     lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
    #     {"tools": "confeiteiro_tools", "continue": "inspector"}
    # )
    # workflow.add_edge("confeiteiro_tools", "confeiteiro")

    # CONFEITEIRO → INSPETOR
    # workflow.add_conditional_edges(
    #     "inspector",
    #     lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
    #     {"tools": "inspector_tools", "continue": "quality_check_logic"}
    # )
    # workflow.add_edge("inspector_tools", "inspector")

    # LÓGICA DE QUALIDADE
    # def quality_check_node(state: AgentState):
    #     return state
    #
    # workflow.add_node("quality_check_logic", quality_check_node)
    # workflow.add_conditional_edges(
    #     "quality_check_logic",
    #     evaluate_quality,
    #     {
    #         "gather_ingredients": "sous_chef",
    #         END: END
    #     }
    # )

    raise NotImplementedError(
        "Pipeline 'kitchen' ainda não implementada. "
        "Implemente os agentes sous_chef, confeiteiro e inspector antes de compilar."
    )

    # Usar AsyncSqliteSaver via llm/checkpointer.py ao compilar:
    # from src.llm.checkpointer import build_checkpointer_sqlite
    # return workflow.compile(checkpointer=checkpointer)