from dotenv import load_dotenv
load_dotenv()

from src.llm.get_env import get_env

DB_DSN = get_env("DB_DSN", strict=False) or "data/database.db"