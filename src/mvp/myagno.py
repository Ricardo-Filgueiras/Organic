import json
import os
from pathlib import Path
from agno.agent import Agent
from dotenv import load_dotenv

load_dotenv()

from typing import Any, cast
import logging

logging.basicConfig(level=logging.INFO)

from agno.agent import Agent
from agno.models.ollama import OllamaResponses
from collections import Counter
import re
from agno.skills import Skills, LocalSkills
from agno.workflow import Workflow
from agno.tools.file import FileTools 
from agno.tools import tool 

def extract_json_from_text(s):
    """Tenta extrair um JSON embutido em texto livre.
    Estratégia:
    1) tentar json.loads direto
    2) procurar tags <JSON>...</JSON>
    3) procurar a primeira substring {...} balanceada e tentar parse
    Retorna o dict parseado ou None se falhar.
    """
    if not s:
        return None
    # tentativa direta
    try:
        return json.loads(s)
    except Exception:
        pass
    # procurar tags <JSON>...</JSON>
    m = re.search(r'<JSON>(.*?)</JSON>', s, flags=re.S | re.I)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except Exception:
            pass
    # procurar primeira chaveta e tentar emparelhamento
    for m in re.finditer(r'\{', s):
        i = m.start()
        stack = 0
        for j in range(i, len(s)):
            if s[j] == '{':
                stack += 1
            elif s[j] == '}':
                stack -= 1
            if stack == 0:
                candidate = s[i:j+1]
                try:
                    return json.loads(candidate)
                except Exception:
                    break
    return None


# salvar a saida em um arquivo de texto na pasta data/output.
# resolvendo raiz do projecto e diretórios de dados/saída

project_root = Path(__file__).resolve().parent.parent.parent
data_dir = project_root / "data"
output_dir = data_dir / "output"
output_dir.mkdir(parents=True, exist_ok=True)


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
        "Você receberá um texto bruto. Analise o conteúdo e RETORNE APENAS UM JSON VÁLIDO, envolto nas tags <JSON> e </JSON>.\n"
        "REQUISITOS EXATOS:\n"
        "- Responda SOMENTE com: <JSON>{\"topics\": [...], \"summary\": \"...\"}</JSON>\n"
        "- 'topics': lista (3-8) de strings; 'summary': resumo conciso (1-2 frases).\n"
        "NÃO envie texto fora das tags. Exemplo: <JSON>{\"topics\": [\"amor\",\"fidelidade\"], \"summary\": \"Resumo...\"}</JSON>\n"
        "Se sua primeira resposta não contiver um JSON válido entre as tags, a aplicação pedirá que você reenvie apenas o bloco JSON entre <JSON>...</JSON>."
    ),
    skills=shared_skills,
    tools=[data_tools],
    markdown=False,
    debug_mode=True, # ativa debug para ver a entrada/saída do modelo no console
)


segundo = Agent(
    name="Segundo Agente",
    description="Expande cada tópico em parágrafos detalhados.",
    model=OllamaResponses("granite4:350m"),
    instructions=(
        "Entrada: JSON com 'topics' e 'summary'. Para cada tópico, escreva um parágrafo explicativo. "
        "Retorne um texto concatenado com um parágrafo por tópico."
    ),
    tools=[data_tools],
    markdown=False,
    debug_mode=True, # ativa debug para ver a entrada/saída do modelo no console
)


terceiro = Agent(
    name="Terceiro Agente",
    description="Consolida o texto final e adiciona uma observação final.",
    model=OllamaResponses("llama3.2:3b"),
    instructions=(
        "Entrada: texto expandido. Gere um texto final consolidado (1-2 parágrafos) "
        "e acrescente uma observação sobre o conteúdo. Retorne apenas o texto final."
    ),
    tools=[data_tools], # o modelo não precisaria usar a tool_data para ler o arquivo pois ele ja foi lido e resumido pelo primeiro agente.
    markdown=False,
    debug_mode=True, # ativa debug para ver a entrada/saída do modelo no console
)




new_worflow = Workflow(
    name="Workflow de Teste",
    description="Este é um workflow de teste para demonstrar a funcionalidade do Agno.",
    steps=cast(Any, [primeiro, segundo, terceiro]),
)

if __name__ == "__main__":
    kepp_path = data_dir / "kepp.txt"
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
        # passo 1: chamar o primeiro agente e garantir JSON válido (retry)
        RETRIES = 2
        attempt = 0
        run1_text = ""
        debug_run1_path = output_dir / "run1.json"
        while attempt <= RETRIES:
            run1 = primeiro.run(text)
            run1_text = str(run1.content) if (run1 is not None and getattr(run1, 'content', None) is not None) else ""
            debug_run1_path.write_text(run1_text, encoding="utf-8")
            print(f"run1 (primeiro) — attempt {attempt} preview:", run1_text[:1000])
            if not run1_text:
                print("Primeiro agente retornou conteúdo vazio; tentando novamente...")
                attempt += 1
                continue
            # tentar extrair JSON de forma robusta
            parsed = extract_json_from_text(run1_text)
            if parsed:
                topics = parsed.get("topics", [])
                summary = parsed.get("summary", "")
                break
            # tentar pedir reenvio estrito com tags <JSON>
            print("Saída do primeiro agente não é JSON válido; tentando extrair ou pedindo reenvio com tags <JSON>.")
            prompt_fix = (
                "Sua resposta anterior não era JSON válido. Responda AGORA apenas com o bloco JSON entre <JSON> e </JSON> no formato: {\"topics\": [..], \"summary\": \"..\"}.\n"
                "Resposta esperada EXATA (exemplo): <JSON>{\"topics\": [\"amor\", \"fidelidade\"], \"summary\": \"Resumo...\"}</JSON>\n"
                "Aqui está o texto original (novamente):\n" + text
            )
            run1_fix = primeiro.run(prompt_fix)
            run1_text = str(run1_fix.content) if (run1_fix is not None and getattr(run1_fix, 'content', None) is not None) else ""
            debug_run1_path.write_text(run1_text, encoding="utf-8")
            # tentar extrair da resposta de correção
            parsed2 = extract_json_from_text(run1_text)
            if parsed2:
                topics = parsed2.get("topics", [])
                summary = parsed2.get("summary", "")
                break
            attempt += 1
        else:
            # fallback simples: extrair tópicos por frequência de palavras (pt-br stopwords)
            print("Fallback: extraindo tópicos por frequência de palavras.")
            def fallback_topics(s, n=5):
                s = s.lower()
                words = re.findall(r"\w+", s, flags=re.UNICODE)
                stop = {
                    'de','a','o','e','do','da','dos','das','que','em','um','uma','para','com','não','se','por','mais',
                    'os','as','no','na','nos','nas','ao','à','às','as','sou','sou','me','meu','minha','já','como','quem'
                }
                filtered = [w for w in words if w not in stop and len(w) > 2]
                most = [w for w, _ in Counter(filtered).most_common(n)]
                return most
            topics = fallback_topics(text, n=5)
            summary = (text.strip().split('\n')[:3])
            summary = ' '.join([l.strip() for l in summary if l.strip()])[:400]
            # salvar fallback como run1
            debug_run1_path.write_text(json.dumps({'topics': topics, 'summary': summary}, ensure_ascii=False), encoding='utf-8')
        # passo 2: montar entrada para segundo agente
        entrada_segundo = json.dumps({"topics": topics, "summary": summary}, ensure_ascii=False)
        run2 = segundo.run(entrada_segundo)
        run2_text = run2.content if (run2 is not None and getattr(run2, 'content', None)) else ""
        debug_run2_path = output_dir / "run2.txt"
        debug_run2_path.write_text(str(run2_text), encoding="utf-8")
        print("run2 (segundo) — preview:", str(run2_text)[:1000])
        # passo 3
        # garantir que run2_text é uma string antes de passar para o terceiro agente
        if not run2_text:
            print("Segundo agente retornou conteúdo vazio; abortando etapa 3.")
            continue
        run3 = terceiro.run(run2_text)
        # salvar resultado
        out_path = output_dir / "result.txt"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(str(run3.content or ""), encoding="utf-8")
        print(f"Workflow concluído — resultado salvo em: {out_path}")