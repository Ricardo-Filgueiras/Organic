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

# AGORA IMPORTAMOS O NOVO GRAFO PRINCIPAL CONVERSACIONAL
from src.graph.graph_chat import graph_chat as build_graph
from src.llm.config import async_lifespan


async def run_graph(checkpointer: BaseCheckpointSaver) -> None:
    graph = build_graph(checkpointer)

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
        user_choice = prompt.ask("[bold cyan]👤 Selecione o usuário (1, 2, 3) ou 'q' para sair: \n")
        
        if user_choice.lower() in ["q", "quit", "/encerrar"]:
            print("[bold green]Encerrando testes...[/bold green]")
            break
            
        if user_choice not in simulated_users:
            print("[bold red]❌ Usuário inválido. Por favor, escolha 1, 2 ou 3.[/bold red]\n")
            continue
            
        active_user = simulated_users[user_choice]
        print(f"\n[bold green]✅ Conectado como {active_user['name']}. Digite 'voltar' para trocar de usuário.[/bold green]")
        
        # Loop de chat contínuo para o usuário selecionado
        while True:
            user_input = prompt.ask(f"\n[bold cyan]💬 {active_user['name']} diz: \n")
            
            if user_input.lower() == "voltar":
                print("[bold yellow]Voltando para o menu de usuários...[/bold yellow]\n")
                break
                
            if user_input.lower() in ["q", "quit", "/encerrar"]:
                print("[bold green]Encerrando testes...[/bold green]")
                return # Sai da função run_graph

            print(Markdown("\n\n  ---  \n\n"))

            config = RunnableConfig(
                configurable={"thread_id": active_user["thread_id"]},
            )

            human_message = HumanMessage(user_input)

            print(f"[dim]Enviando para o Chatbot...[/dim]")

            # Invoca a esteira principal
            result = await graph.ainvoke(
                {"messages": [human_message]}, config=config
            )

            # Pegamos a lista de mensagens devolvida e lemos a última (A resposta da LLM)
            messages = result.get("messages", [])
            if messages:
                last_ai_message = messages[-1]
                print(f"\n[bold green]🤖 Chatbot:[/bold green]")
                print(Markdown(last_ai_message.content))
                
            print(Markdown("\n\n  ---  \n\n"))

    print("\n[bold yellow]Mostrando o Estado (Memória) Final armazenado no Checkpointer para cada Usuário:[/bold yellow]")
    for k, user in simulated_users.items():
        user_config = RunnableConfig(configurable={"thread_id": user["thread_id"]})
        state = await graph.aget_state(config=user_config)
        print(f"\n[bold cyan]Histórico da sessão de {user['name']}:[/bold cyan]")
        print(f"Número de mensagens na memória: {len(state.values.get('messages', []))}")


async def main() -> None:
    async with (
        async_lifespan(),
        # build_checkpointer_psql(DB_DSN) as checkpointer,
        build_checkpointer_sqlite(DB_DSN) as checkpointer,
    ):
        await run_graph(checkpointer)


if __name__ == "__main__":
    asyncio.run(main())