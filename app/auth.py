"""Autenticação simples por senha para acesso à aplicação."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from config import APP_PASSWORD
except ImportError:
    APP_PASSWORD = os.environ.get("APP_PASSWORD", "XXXX")


def check_password(password: str) -> bool:
    """Retorna True se a senha informada for a senha configurada."""
    try:
        p = (password or "").strip()
        expected = str(APP_PASSWORD or "").strip()
        return bool(p and p == expected)
    except Exception as e:
        return False
