"""Ponto de entrada do IDI — inicia o dashboard Dash.
Execute: python run.py  (ou .venv/bin/python run.py)
Defina a chave no terminal antes: export OPENAI_API_KEY="sua-chave"
Acesse: http://127.0.0.1:8050"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dash_app.app import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
