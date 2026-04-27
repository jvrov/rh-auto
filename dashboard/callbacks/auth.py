from __future__ import annotations

from dash import Dash, Input, Output, State, no_update
import dash_bootstrap_components as dbc

from dashboard import components as comp
from app.auth import check_password


def register(app: Dash) -> None:
    @app.callback(
        [Output(comp.ID_LOGIN_CONTAINER, "style"), Output(comp.ID_MAIN_CONTAINER, "style")],
        Input(comp.ID_AUTH_STORE, "data"),
    )
    def toggle_login_main(is_auth):
        if is_auth:
            return {"display": "none"}, {"display": "block"}
        return {"display": "block"}, {"display": "none"}

    @app.callback(
        [Output(comp.ID_AUTH_STORE, "data"), Output(comp.ID_LOGIN_ERROR, "children"), Output(comp.ID_PASSWORD_INPUT, "value")],
        [
            Input(comp.ID_LOGIN_BTN, "n_clicks"),
            Input(comp.ID_PASSWORD_INPUT, "n_submit"),
        ],
        State(comp.ID_PASSWORD_INPUT, "value"),
        prevent_initial_call=True,
    )
    def on_login(n_clicks, n_submit, password):
        try:
            if not (password or "").strip():
                return no_update, no_update, no_update
            if check_password(password):
                return True, "", ""
            return no_update, dbc.Alert("Senha incorreta. Tente novamente.", color="danger", className="mb-0"), ""
        except Exception as e:
            return no_update, dbc.Alert(f"Erro ao entrar: {e}", color="danger", className="mb-0"), no_update

