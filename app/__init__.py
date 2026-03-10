"""Aplicação Flask IDI - Industrial Deal Intelligence."""
import os
from flask import Flask

from . import models
from . import routes


def create_app(config_overrides=None):
    """Factory da aplicação Flask."""
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object("config")
    if config_overrides:
        app.config.update(config_overrides)
    # Garante UPLOAD_FOLDER como caminho absoluto em string
    uf = app.config["UPLOAD_FOLDER"]
    app.config["UPLOAD_FOLDER"] = os.path.abspath(str(uf))
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inicializa banco
    db_path = app.config.get("DATABASE_PATH")
    if db_path:
        models.init_db(str(db_path))

    routes.register_routes(app)
    return app
