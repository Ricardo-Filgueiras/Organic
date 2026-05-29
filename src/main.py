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

    all_messages: list[BaseMessage] = []

    prompt = Prompt()
    Prompt.prompt_suffix = ""

    while True:
        user_input = prompt.ask("[bold cyan]Você: \n")
        print(Markdown("\n\n  ---  \n\n"))

        if user_input.lower() in ["q", "quit"]:
            break

        human_message = HumanMessage(user_input)
        current_loop_messages = [human_message]

        # if len(all_messages) == 0:
        #     current_loop_messages = [SystemMessage(SYSTEM_PROMPT), human_message]

        result = await graph.ainvoke(
            {"messages": current_loop_messages}, config=config
        )

        model_name = ""
        last_message = result["messages"][-1]

        if isinstance(last_message, AIMessage):
            model_name = last_message.response_metadata.get("model", "")

        print(f"[bold cyan]RESPOSTA ({model_name}): \n")
        print(Markdown(last_message.text))
        print(last_message)
        print(Markdown("\n\n  ---  \n\n"))

        all_messages = result["messages"]

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