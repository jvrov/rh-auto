"""Configurações do projeto IDI."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
# Chave da API OpenAI - definir via variável de ambiente (export OPENAI_API_KEY="sua-chave")
# Use: export OPENAI_API_KEY="sua-chave" no terminal (não coloque a chave aqui)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Chave secreta do Flask (sessions, flash) - em produção use variável de ambiente
SECRET_KEY = os.environ.get("SECRET_KEY", "idi-dev-secret-change-in-production")

# SQLite
DATABASE_PATH = BASE_DIR / "idi.db"

# Limite de upload (16 MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}
