import re
from pathlib import Path

from langchain.tools import tool

from src.llm.constants import ARTICLES_DIR

# Permite apenas letras, números, espaço, hífen e underscore no nome do arquivo.
_INVALID_FILENAME_CHARS = re.compile(r"[^a-zA-Z0-9 _-]")


def _sanitize_filename(filename: str) -> str:
    name = Path(filename).stem
    name = _INVALID_FILENAME_CHARS.sub("", name).strip()
    if not name:
        raise ValueError(f"Nome de arquivo inválido: {filename!r}")
    return name


@tool
def save_article(filename: str, content: str) -> str:
    """Salva o conteúdo de um artigo em um arquivo .md no diretório de artigos.

    Args:
        filename: nome do arquivo, sem extensão (ex: "como-plantar-tomates").
        content: conteúdo do artigo em markdown.

    Returns:
        Caminho do arquivo salvo.
    """
    safe_name = _sanitize_filename(filename)

    articles_dir = Path(ARTICLES_DIR)
    articles_dir.mkdir(parents=True, exist_ok=True)

    file_path = articles_dir / f"{safe_name}.md"
    file_path.write_text(content + "\n", encoding="utf-8")

    return str(file_path)
