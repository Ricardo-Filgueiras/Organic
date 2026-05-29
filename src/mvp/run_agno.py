import json
import os
from pathlib import Path
from agno.agent import Agent
from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent
from agno.models.ollama import OllamaResponses
from agno.skills import Skills, LocalSkills
from agno.workflow import Workflow
from agno.tools.websearch import WebSearchTools
from agno.tools.file import FileTools


# salvar a saida em um arquivo de texto na pasta data/output.
output_dir = Path(__file__).parent / "data/output"
output_dir.mkdir(parents=True, exist_ok=True)

data_dir = Path(__file__).parent.parent / "data"
data_tools = FileTools(
    base_dir=data_dir,
    enable_save_file=True,
    enable_read_file=True,
    enable_list_files=True,
)

file_tools = FileTools(
    base_dir=output_dir,
    enable_save_file=True,
    enable_read_file=True,
    enable_list_files=True,
)


skills_dir = Path(__file__).parent / "skills"
shared_skills = Skills(
    loaders=[
        LocalSkills(str(skills_dir)),
    ]
)

primeiro = Agent(
    name="Primeiro Agente",
    description="Lê o texto de entrada e extrai tópicos/chaves.",
    model=OllamaResponses("granite4.1:3b"),
    instructions=(
        "Receba um texto e responda com um JSON contendo: "
        "'topics' (lista curta de tópicos/chaves extraídas) e 'summary' (resumo breve). "
        "Retorne apenas JSON."
    ),
    skills=shared_skills,
    tools=[file_tools, data_tools],
    markdown=False,
)


segundo = Agent(
    name="Segundo Agente",
    description="Expande cada tópico em parágrafos detalhados.",
    model=OllamaResponses("granite4:350m"),
    instructions=(
        "Entrada: JSON com 'topics' e 'summary'. Para cada tópico, escreva um parágrafo explicativo. "
        "Retorne um texto concatenado com um parágrafo por tópico."
    ),
    tools=[file_tools],
    markdown=False,
)


terceiro = Agent(
    name="Terceiro Agente",
    description="Consolida o texto final e adiciona uma observação final.",
    model=OllamaResponses("gemma3:270m"),
    instructions=(
        "Entrada: texto expandido. Gere um texto final consolidado (1-2 parágrafos) "
        "e acrescente uma observação sobre o conteúdo. Retorne apenas o texto final."
    ),
    tools=[file_tools],
    markdown=False,
)




new_worflow = Workflow(
    name="Workflow de Teste",
    description="Este é um workflow de teste para demonstrar a funcionalidade do Agno.",
    steps=[primeiro, segundo, terceiro],
)

if __name__ == "__main__":
    kepp_path = Path(__file__).parent.parent / "data" / "kepp.txt"
    print("REPL: digite 'run' para executar, 'exit' para sair.")
    while True:
        cmd = input("> ").strip().lower()
        if cmd in ("exit", "quit"):
            break
        if cmd != "run":
            print("Comando desconhecido. Use 'run' ou 'exit'.")
            continue
        if not kepp_path.exists():
            print(f"Arquivo não encontrado: {kepp_path}")
            continue
        text = kepp_path.read_text(encoding="utf-8")
        # passo 1
        run1 = primeiro.run(text)
        try:
            j = json.loads(run1.content)
            topics = j.get("topics", [])
            summary = j.get("summary", "")
        except Exception as e:
            print("Erro ao parsear JSON do primeiro agente:", e)
            print("Conteúdo retornado:", run1.content)
            continue
        # passo 2: montar entrada para segundo agente
        entrada_segundo = json.dumps({"topics": topics, "summary": summary}, ensure_ascii=False)
        run2 = segundo.run(entrada_segundo)
        # passo 3
        run3 = terceiro.run(run2.content)
        # salvar resultado
        out_path = Path(__file__).parent / "data" / "output" / "result.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(run3.content, encoding="utf-8")
        print(f"Workflow concluído — resultado salvo em: {out_path}")