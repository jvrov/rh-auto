"""Inicia apenas o servidor do dashboard (porta 8050), sem abrir janela.
Para o aplicativo com JANELA, use: python main.py
Acesse: http://127.0.0.1:8050"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard.dashboard import app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
