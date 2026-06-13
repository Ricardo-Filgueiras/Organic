from typing import NotRequired

from langchain.agents import AgentState


class PipelineState(AgentState):
    """Estado compartilhado da pipeline brainstorm -> estruturação -> escrita -> publicação.

    Cada agente lê o output da etapa anterior e escreve apenas o seu próprio
    campo, permitindo adicionar/remover agentes do grafo sem afetar os demais.
    """

    brainstorm_output: NotRequired[str]
    structure_output: NotRequired[str]
    draft_content: NotRequired[str]
    published_path: NotRequired[str]
