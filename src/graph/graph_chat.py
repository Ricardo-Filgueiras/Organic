from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.pregel.main import BaseCheckpointSaver
from langgraph.prebuilt import ToolNode
from typing import Optional

from src.schemas.state_chat import ChatState
from src.agents.chat.agent import call_chatbot, tools

def should_continue(state: ChatState):
    """Nó Condicional: Verifica se a LLM do chatbot decidiu chamar uma ferramenta."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"
    return END

def graph_chat(
    checkpointer: Optional[BaseCheckpointSaver] = None,
) -> CompiledStateGraph:
    builder = StateGraph(
        state_schema=ChatState,
    )

    builder.add_node("chatbot", call_chatbot)
    
    # ToolNode nativo do LangGraph executa qualquer @tool chamada pela LLM (no nosso caso, invoca o Sub-Grafo)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "chatbot")
    
    # Se o chatbot chamou a tool, roteia para 'tools', senão encerra (aguarda o usuário responder)
    builder.add_conditional_edges("chatbot", should_continue, ["tools", END])
    
    # Depois que a Tool rodar e trouxer os dados do Sub-Grafo, o controle volta para o Chatbot processar a resposta
    builder.add_edge("tools", "chatbot")

    return builder.compile(checkpointer=checkpointer)

app = graph_chat()
