import os
import requests
from typing import List, Optional, AsyncGenerator

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.runnables.config import RunnableConfig
from contextlib import asynccontextmanager, contextmanager

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "data/checkpoints.db")
BASE_MODEL = os.getenv("BASE_MODEL", "ollama:granite4.1:3b")
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../..", ".agent", "system_prompt.md")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
AGENTS_DIR = os.path.join(os.path.dirname(__file__), "../agents")

# Lista estática dos modelos em nuvem que sua aplicação suporta e tem chaves de API configuradas
CLOUD_MODELS = [
    {"id": "openai:gpt-4o", "name": "GPT-4o (OpenAI)", "type": "cloud"},
    {"id": "openai:gpt-4o-mini", "name": "GPT-4o Mini (OpenAI)", "type": "cloud"},
    {"id": "anthropic:claude-3-5-sonnet", "name": "Claude 3.5 Sonnet (Anthropic)", "type": "cloud"},
    {"id": "google_genai:gemini-1.5-flash", "name": "Gemini 1.5 Flash (Google)", "type": "cloud"}
]

# Quero listar os modelos locais disponíveis no ollama, 
# com uma função ollama lista os modelos disponíveis, 
# e depois escolher o modelo com base na variável de ambiente BASE_MODEL.

def list_ollama_models() -> List[str]:
    """
    Lista todos os modelos disponíveis no Ollama.
    
    Returns:
        List[str]: Lista de nomes dos modelos disponíveis
        
    Raises:
        ConnectionError: Se não conseguir conectar ao Ollama
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Extrai os nomes dos modelos
        models = [model["name"] for model in data.get("models", [])]
        return models
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Não foi possível conectar ao Ollama em {OLLAMA_API_URL}. "
            "Certifique-se de que o Ollama está rodando."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Timeout ao conectar ao Ollama")
    except Exception as e:
        raise RuntimeError(f"Erro ao listar modelos do Ollama: {e}")

def validate_model(model_name: str) -> bool:
    """
    Valida se um modelo está disponível no Ollama.
    
    Args:
        model_name (str): Nome do modelo a validar
        
    Returns:
        bool: True se o modelo existe, False caso contrário
    """
    try:
        available_models = list_ollama_models()
        return model_name in available_models
    except Exception:
        return False

def get_model():
    """
    Inicializa o modelo de chat baseado na variável de ambiente BASE_MODEL.
    Valida se o modelo está disponível no Ollama.
    """
    model_name = os.getenv("BASE_MODEL", "ollama:granite4.1:3b")
    
    # Validar modelo disponível
    if not validate_model(model_name.replace("ollama:", "")):
        print(f"Aviso: Modelo '{model_name}' pode não estar disponível no Ollama")
        print("Modelos disponíveis:")
        try:
            for model in list_ollama_models():
                print(f"  - {model}")
        except Exception as e:
            print(f"  Erro ao listar modelos: {e}")
    
    return init_chat_model(model_name)

# Configurações globais
def load_system_prompt(agent_type: Optional[str] = None) -> str:
    """
    Carrega o system prompt específico do agente ou um padrão global.
    
    Args:
        agent_type: Nome do agente (ex: 'writer', 'strategist', 'seo')
                   Se None, carrega o prompt padrão
    
    Returns:
        str: O system prompt para o agente
    """
    if agent_type:
        # Tenta carregar prompt específico do agente
        agent_prompt_path = os.path.join(AGENTS_DIR, agent_type, "system_prompt.md")
        try:
            with open(agent_prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Prompt não encontrado para '{agent_type}', usando padrão")
    
    # Carrega prompt global padrão
    try:
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError as e:
        print(f"Aviso: {e}")
        return "Você é um assistente de IA prestativo."

# Configurações globais - prompt padrão
SYSTEM_PROMPT = load_system_prompt()

# Dicionário de prompts por agente (em cache)
AGENT_PROMPTS = {}

def get_system_prompt_for_agent(agent_type: str) -> str:
    """Retorna o system prompt em cache para um agente específico."""
    if agent_type not in AGENT_PROMPTS:
        AGENT_PROMPTS[agent_type] = load_system_prompt(agent_type)
    return AGENT_PROMPTS[agent_type]


@asynccontextmanager
async def async_lifespan() -> AsyncGenerator[None, None]:
    print("Async Abri")
    yield
    print("Async Fechei")