from collections.abc import Sequence
from typing import Annotated, TypedDict, List

from langgraph.graph.message import BaseMessage, add_messages

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    normalized_input: str
    name: List[str]
    subname: List[str]
    Description: List[str]