"""
AI Contract Risk Analyzer - Dashboard Dash.
Inicializa o servidor e o layout. Rode: python app.py (em dash_app) ou python -m dash_app.app (em idi_project).
"""
import sys
from pathlib import Path

# Garante que o projeto pai está no path (para importar app.contract_analyzer, etc.)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import dash
from dash import Dash
import dash_bootstrap_components as dbc

from .database import init_db
from .layout import build_layout
from .callbacks import register_callbacks

# Banco SQLite na pasta do projeto principal
DB_PATH = ROOT / "idi.db"
init_db(str(DB_PATH))

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=False,
)
app.title = "AI Contract Risk Analyzer"
app.layout = build_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
