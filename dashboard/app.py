from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dash import Dash
import dash_bootstrap_components as dbc

from config import DATABASE_PATH
from app.database import init_db as init_sqlite_db
from dashboard import components as comp


def create_dash_app() -> Dash:
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder=str(ROOT / "assets"),
    )
    app.title = "Contract Risk Analyzer AI"
    app.layout = comp.build_layout()
    init_sqlite_db(DATABASE_PATH)
    return app

