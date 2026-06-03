import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # adiciona raiz do projeto


from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph.state import RunnableConfig
from langgraph.pregel.main import BaseCheckpointSaver, asyncio
from rich import print
from rich.markdown import Markdown
from rich.prompt import Prompt

from src.llm.checkpointer import (
    build_checkpointer_sqlite,
)
from src.llm.constants import DB_DSN
from src.graph.graph_build import build_graph
from src.llm.config import async_lifespan


async def run_graph(checkpointer: BaseCheckpointSaver) -> None:
    graph = build_graph(checkpointer)


    config = RunnableConfig(
        configurable={"thread_id": 1},
    )

    prompt = Prompt()
    Prompt.prompt_suffix = ""

    print("[bold yellow]Dica: Digite 'q', 'quit' ou '/encerrar' a qualquer momento para encerrar a conversa.[/bold yellow]\n")

    while True:
        user_input = prompt.ask("[bold cyan]Descrição do Produto: \n")
        print(Markdown("\n\n  ---  \n\n"))

        if user_input.lower() in ["q", "quit", "/encerrar"]:
            print("[bold green]Conversa encerrada.[/bold green]")
            break

        human_message = HumanMessage(user_input)

        # Invoca a esteira passando a mensagem inicial
        result = await graph.ainvoke(
            {"messages": [human_message]}, config=config
        )

        print("[bold green]✅ Pipeline Concluído com Sucesso![/bold green]\n")
        
        print("[bold yellow]Input Normalizado:[/bold yellow]")
        print(result.get("normalized_input", "N/A"))
        
        print("\n[bold cyan]Nomes Gerados:[/bold cyan]")
        for n in result.get("name", []):
            print(f"  • {n}")
            
        print("\n[bold magenta]Sobrenomes/Variantes:[/bold magenta]")
        for sn in result.get("subname", []):
            print(f"  • {sn}")
            
        print("\n[bold blue]Descrições:[/bold blue]")
        for d in result.get("Description", []):
            print(f"  • {d}")
            
        print(Markdown("\n\n  ---  \n\n"))

    print(await graph.aget_state(config=config))


async def main() -> None:
    async with (
        async_lifespan(),
        # build_checkpointer_psql(DB_DSN) as checkpointer,
        build_checkpointer_sqlite(DB_DSN) as checkpointer,
    ):
        await run_graph(checkpointer)


if __name__ == "__main__":
    asyncio.run(main())