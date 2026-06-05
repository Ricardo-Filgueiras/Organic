import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # adiciona raiz do projeto

import uuid

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
from src.graph.graph_name import graph_name as build_graph
from src.llm.config import async_lifespan


async def run_graph(checkpointer: BaseCheckpointSaver) -> None:
    graph = build_graph(checkpointer)

    # Dicionário simulando 3 usuários diferentes com sessões (thread_id) únicas
    simulated_users = {
        "1": {"name": "Alice", "thread_id": str(uuid.uuid4())},
        "2": {"name": "Bob", "thread_id": str(uuid.uuid4())},
        "3": {"name": "Charlie", "thread_id": str(uuid.uuid4())},
    }

    prompt = Prompt()
    Prompt.prompt_suffix = ""

    print("[bold yellow]Dica: Digite 'q', 'quit' ou '/encerrar' a qualquer momento para sair.[/bold yellow]\n")
    
    print("[bold magenta]🧑‍🤝‍🧑 Usuários Simulados Disponíveis para Teste:[/bold magenta]")
    for k, v in simulated_users.items():
        print(f"  [[bold cyan]{k}[/bold cyan]] {v['name']} (Sessão UUID: {v['thread_id']})")
    print("\n")

    while True:
        # 1. Seleciona quem está interagindo
        user_choice = prompt.ask("[bold cyan]👤 Selecione o usuário que vai enviar a mensagem (1, 2, 3) ou 'q' para sair: \n")
        
        if user_choice.lower() in ["q", "quit", "/encerrar"]:
            print("[bold green]Conversa encerrada.[/bold green]")
            break
            
        if user_choice not in simulated_users:
            print("[bold red]❌ Usuário inválido. Por favor, escolha 1, 2 ou 3.[/bold red]\n")
            continue
            
        active_user = simulated_users[user_choice]
        
        # 2. Captura a mensagem do usuário selecionado
        user_input = prompt.ask(f"\n[bold cyan]📝 Descrição do Produto de {active_user['name']}: \n")
        print(Markdown("\n\n  ---  \n\n"))

        if user_input.lower() in ["q", "quit", "/encerrar"]:
            print("[bold green]Conversa encerrada.[/bold green]")
            break

        # A diferenciação mágica acontece aqui!
        # Usamos o uuid atrelado àquele usuário para criar a configuração do LangGraph
        config = RunnableConfig(
            configurable={"thread_id": active_user["thread_id"]},
        )

        human_message = HumanMessage(user_input)

        print(f"[dim]Enviando como {active_user['name']} (thread: {active_user['thread_id']})...[/dim]")

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

    print("\n[bold yellow]Mostrando o Estado (Memória) Final armazenado no Checkpointer para cada Usuário:[/bold yellow]")
    for k, user in simulated_users.items():
        user_config = RunnableConfig(configurable={"thread_id": user["thread_id"]})
        state = await graph.aget_state(config=user_config)
        print(f"\n[bold cyan]Estado Final de {user['name']}:[/bold cyan]")
        print(state)


async def main() -> None:
    async with (
        async_lifespan(),
        # build_checkpointer_psql(DB_DSN) as checkpointer,
        build_checkpointer_sqlite(DB_DSN) as checkpointer,
    ):
        await run_graph(checkpointer)


if __name__ == "__main__":
    asyncio.run(main())