from pydantic import BaseModel, Field
from typing import List

class RouterOutput(BaseModel):
    """Output for the router agent."""
    normalized_input: str = Field(description="The normalized text input from the user")

class NameOutput(BaseModel):
    """Output for the name generation agent."""
    name: List[str] = Field(description="List of generated main names")

class NameSubOutput(BaseModel):
    """Output for the subname and description generation agent."""
    subname: List[str] = Field(description="List of generated subnames or variants")
    Description: List[str] = Field(description="List of detailed descriptions for the item")
