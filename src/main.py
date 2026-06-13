import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # adiciona raiz do projeto

import uuid

from langchain_core.messages import HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.pregel.main import BaseCheckpointSaver, asyncio
from rich import print
from rich.markdown import Markdown

from src.llm.checkpointer import build_checkpointer_sqlite
from src.llm.constants import DB_DSN
from src.graph.graph_chat import graph_chat as build_graph
from src.llm.config import async_lifespan


async def run_smoke_test(checkpointer: BaseCheckpointSaver) -> None:
    """
    Smoke test rápido do ChatAgent.

    Para interagir/debugar de forma completa, use o LangGraph Studio
    (`langgraph dev`), que carrega o grafo "chat" definido em langgraph.json.
    """
    graph = build_graph(checkpointer)
    config = RunnableConfig(configurable={"thread_id": str(uuid.uuid4())})

    result = await graph.ainvoke(
        {"messages": [HumanMessage("Olá! Você está funcionando?")]},
        config=config,
    )

    print("[bold green]🤖 ChatAgent:[/bold green]")
    print(Markdown(result["messages"][-1].content))


async def main() -> None:
    async with (
        async_lifespan(),
        build_checkpointer_sqlite(DB_DSN) as checkpointer,
    ):
        await run_smoke_test(checkpointer)


if __name__ == "__main__":
    asyncio.run(main())
