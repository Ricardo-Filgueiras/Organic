import pytest

from src.tools import writer_filer
from src.tools.writer_filer import _sanitize_filename, save_article


@pytest.fixture(autouse=True)
def _articles_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(writer_filer, "ARTICLES_DIR", str(tmp_path))
    return tmp_path


def test_save_article_writes_file(_articles_dir):
    result = save_article.invoke({"filename": "meu-artigo", "content": "# Título\n\nConteúdo"})

    saved_path = _articles_dir / "meu-artigo.md"
    assert result == str(saved_path)
    assert saved_path.read_text(encoding="utf-8") == "# Título\n\nConteúdo\n"


def test_save_article_overwrites_existing_file(_articles_dir):
    save_article.invoke({"filename": "meu-artigo", "content": "versão 1"})
    save_article.invoke({"filename": "meu-artigo", "content": "versão 2"})

    saved_path = _articles_dir / "meu-artigo.md"
    assert saved_path.read_text(encoding="utf-8") == "versão 2\n"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("meu artigo", "meu artigo"),
        ("meu-artigo_2024", "meu-artigo_2024"),
        ("../../etc/passwd", "passwd"),
        ("artigo/sub/diretorio", "diretorio"),
        ("artigo<>?.md", "artigo"),
    ],
)
def test_sanitize_filename(raw, expected):
    assert _sanitize_filename(raw) == expected


def test_sanitize_filename_rejects_empty_result():
    with pytest.raises(ValueError):
        _sanitize_filename("../../")
