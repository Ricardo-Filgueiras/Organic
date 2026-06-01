import os
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.schemas.state import AgentState
from src.graph.edges import evaluate_quality

# Importação dos Agentes Reais
from src.agents.sous_chef.agent import call_sous_chef, tools as sous_chef_tools
from src.agents.confeiteiro.agent import call_confeiteiro, tools as confeiteiro_tools
from src.agents.inspector.agent import call_inspector, tools as inspector_tools


def create_pipeline():
    """
    Ao escrever a pipeline, estamos definindo o fluxo lógico e as transições 
    entre os agentes, bem como os pontos de uso das ferramentas.
    O grafo resultante é uma representação clara de como a tigela deve ser 
    processada

    """
    workflow = StateGraph(AgentState)

    # 1. Adicionando os Nós (As Estações de Trabalho)
    workflow.add_node("sous_chef", call_sous_chef)
    workflow.add_node("confeiteiro", call_confeiteiro)
    workflow.add_node("inspector", call_inspector)
    
    # Nós de Ferramentas específicos para garantir o retorno correto ao agente
    workflow.add_node("sous_chef_tools", ToolNode(sous_chef_tools))
    workflow.add_node("confeiteiro_tools", ToolNode(confeiteiro_tools))
    workflow.add_node("inspector_tools", ToolNode(inspector_tools))

    # 2. Definindo o Fluxo da Tigela

    # INÍCIO -> SOUS CHEF (Reunir e Adicionar)
    workflow.add_edge(START, "sous_chef")
    workflow.add_conditional_edges(
        "sous_chef",
        lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
        {"tools": "sous_chef_tools", "continue": "confeiteiro"}
    )
    workflow.add_edge("sous_chef_tools", "sous_chef") # Volta para o Sous Chef após usar tool

    # SOUS CHEF -> CONFEITEIRO (Bater e Assar)
    workflow.add_conditional_edges(
        "confeiteiro",
        lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
        {"tools": "confeiteiro_tools", "continue": "inspector"}
    )
    workflow.add_edge("confeiteiro_tools", "confeiteiro") # Volta para o Confeiteiro após usar tool

    # CONFEITEIRO -> INSPETOR (Avaliar e Aprovar)
    workflow.add_conditional_edges(
        "inspector",
        lambda state: "tools" if state["messages"][-1].tool_calls else "continue",
        {"tools": "inspector_tools", "continue": "quality_check_logic"}
    )
    workflow.add_edge("inspector_tools", "inspector")

    # LÓGICA DE QUALIDADE (O Engenheiro de Tráfego)
    def quality_check_node(state: AgentState):
        return state # Nó de passagem para aplicar a lógica de aresta
    
    workflow.add_node("quality_check_logic", quality_check_node)
    
    workflow.add_conditional_edges(
        "quality_check_logic",
        evaluate_quality,
        {
            "gather_ingredients": "sous_chef", # Se nota < 7, volta tudo!
            END: END
        }
    )
    # # Use storege em ./data para persistência de estado e histórico
    # storage_path = os.path.join("data", ".langgraph_api")
    # os.makdirs(storage_path, exist_ok=True)

    # Compile com storage personalizado
    storage_path = os.path.join("data", ".langgraph_api")
    os.makedirs(storage_path, exist_ok=True)

    from langgraph.checkpoint.sqlite import SqliteSaver
    memory = SqliteSaver.from_conn_string(os.path.join(storage_path, "langgraph.db"))

# return workflow.compile(checkpointer=memory)
    
    # return workflow.compile(checkpointer=memory) 

    return workflow.compile()

# Instância global do grafo pronto para uso
app = create_pipeline()