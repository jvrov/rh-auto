"""Configurações do projeto IDI."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
# Chave da API OpenAI - definir via variável de ambiente (export OPENAI_API_KEY="sua-chave")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# SQLite
DATABASE_PATH = BASE_DIR / "idi.db"

# Limite de upload (16 MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}
