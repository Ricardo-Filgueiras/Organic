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


class BrainstormOutput(BaseModel):
    """Output for the brainstorm agent: ideia de artigo de blog refinada."""
    tema: str = Field(description="Tema central da ideia de artigo")
    publico_alvo: str = Field(description="Público-alvo do artigo")
    pontos_chave: List[str] = Field(description="Lista de pontos/tópicos principais a abordar")


class StructureOutput(BaseModel):
    """Output for the structure agent: esqueleto/outline do artigo."""
    titulo: str = Field(description="Título proposto para o artigo")
    introducao: str = Field(description="Breve resumo do que a introdução deve abordar")
    secoes: List[str] = Field(description="Lista ordenada das seções/tópicos do corpo do artigo")
    conclusao: str = Field(description="Breve resumo do que a conclusão deve abordar")
