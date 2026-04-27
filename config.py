"""Configurações do projeto IDI."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Carrega variáveis do arquivo .env (não versionado) para não precisar exportar no terminal
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv opcional; pode usar só variáveis de ambiente

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
# Chave da API OpenAI: coloque em .env como OPENAI_API_KEY=sua-chave (arquivo .env está no .gitignore)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Chave secreta do Flask (sessions, flash) - em produção use variável de ambiente
SECRET_KEY = os.environ.get("SECRET_KEY", "idi-dev-secret-change-in-production")

# SQLite (banco principal)
# Padrão: idi_project/data/app.db
DATABASE_PATH = (BASE_DIR / "data" / "app.db")

# Limite de upload (16 MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {"pdf"}

# Senha de acesso à aplicação (tela de login simples)
# Altere aqui para mudar a senha. Exemplo: "XXXX" ou "MinhaSenha123"
APP_PASSWORD = os.environ.get("APP_PASSWORD", "XXXX")
