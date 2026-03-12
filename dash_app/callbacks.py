"""
Callbacks do dashboard: upload → análise → exibição; histórico; comparação entre contratos.
"""
import base64
import io
import os
from pathlib import Path

from dash import Input, Output, State, html, no_update
import dash_bootstrap_components as dbc

from . import layout
from .database import save_contract, get_all_contracts, get_contract_by_id
from .pdf_reader import extract_text_from_pdf
from .analyzer import analyze_contract_for_dashboard
from .charts import create_radar_chart, create_bar_chart, create_radar_comparison


def _parse_upload(contents):
    """Decodifica conteúdo do upload e retorna (nome_arquivo, texto_extraido) ou (None, erro)."""
    if not contents:
        return None, None
    try:
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        # Salvar em temp para pdfplumber
        tmp = Path(__file__).resolve().parent / "_tmp_upload.pdf"
        tmp.write_bytes(decoded)
        nome = "contrato.pdf"
        text = extract_text_from_pdf(tmp)
        if tmp.exists():
            tmp.unlink()
        return nome, text
    except Exception as e:
        return None, str(e)


def _build_main_content(result):
    """Monta o bloco principal (cards, gráficos, seções) a partir do resultado."""
    radar_fig = create_radar_chart(result)
    bar_fig = create_bar_chart(result)
    return layout.build_main_from_result(result, radar_fig, bar_fig)


def _history_options():
    """Lista de opções para o dropdown de histórico."""
    contracts = get_all_contracts()
    return [{"label": f"{c['nome_contrato']} — Score {c['score']} ({c['data_analise'][:10]})", "value": c["id"]} for c in contracts]


def register_callbacks(app):
    """Registra todos os callbacks no app Dash."""

    # Único callback que atualiza as opções do histórico/comparação (evita Duplicate callback outputs)
    @app.callback(
        [
            Output(layout.ID_HISTORY_DROPDOWN, "options"),
            Output(layout.ID_COMPARE_A, "options"),
            Output(layout.ID_COMPARE_B, "options"),
        ],
        [
            Input(layout.ID_INTERVAL_LOAD_HISTORY, "n_intervals"),
            Input(layout.ID_HISTORY_REFRESH_TRIGGER, "data"),
        ],
        prevent_initial_call=False,
    )
    def refresh_history_options(n_intervals, _trigger):
        opts = _history_options()
        return opts, opts, opts

    # Upload: extrai texto, analisa, salva no banco; dispara refresh do histórico via trigger
    @app.callback(
        [
            Output(layout.ID_RESULTADO_STORE, "data"),
            Output(layout.ID_CONTRACT_ID_STORE, "data"),
            Output(layout.ID_MAIN_CONTENT, "children"),
            Output(layout.ID_HISTORY_REFRESH_TRIGGER, "data"),
        ],
        Input(layout.ID_UPLOAD, "contents"),
        State(layout.ID_UPLOAD, "filename"),
        prevent_initial_call=True,
    )
    def on_upload(contents, filename):
        if not contents:
            return no_update, no_update, no_update, no_update
        nome_arquivo = filename or "contrato.pdf"
        nome, text = _parse_upload(contents)
        if text is None and nome is None:
            return no_update, no_update, dbc.Alert("Erro no upload: não foi possível processar o arquivo.", color="danger"), no_update
        if nome is None:
            return no_update, no_update, dbc.Alert(f"Erro: {text}", color="danger"), no_update
        try:
            result = analyze_contract_for_dashboard(text, nome_contrato=nome_arquivo)
        except Exception as e:
            return no_update, no_update, dbc.Alert(f"Erro na análise: {e}", color="danger"), no_update
        contract_id = save_contract(
            result["nome_contrato"],
            result["score"],
            result["nivel"],
            result,
        )
        main = _build_main_content(result)
        return result, contract_id, main, contract_id


    # Histórico: ao selecionar um contrato no dropdown, carrega e exibe
    @app.callback(
        [
            Output(layout.ID_RESULTADO_STORE, "data", allow_duplicate=True),
            Output(layout.ID_CONTRACT_ID_STORE, "data", allow_duplicate=True),
            Output(layout.ID_MAIN_CONTENT, "children", allow_duplicate=True),
        ],
        Input(layout.ID_HISTORY_DROPDOWN, "value"),
        prevent_initial_call=True,
    )
    def on_history_select(contract_id):
        if not contract_id:
            return no_update, no_update, no_update
        row = get_contract_by_id(contract_id)
        if not row:
            return no_update, no_update, layout.build_main_placeholder()
        result = row["resultado"]
        main = _build_main_content(result)
        return result, contract_id, main

    # Comparação: ao selecionar dois contratos, exibe radar comparativo
    @app.callback(
        Output(layout.ID_COMPARE_CONTAINER, "children"),
        [Input(layout.ID_COMPARE_A, "value"), Input(layout.ID_COMPARE_B, "value")],
    )
    def on_compare(ida, idb):
        if not ida or not idb or ida == idb:
            return html.Div()
        c1 = get_contract_by_id(ida)
        c2 = get_contract_by_id(idb)
        if not c1 or not c2:
            return html.Div()
        r1, r2 = c1["resultado"], c2["resultado"]
        fig = create_radar_comparison(r1, r2, c1["nome_contrato"], c2["nome_contrato"])
        return html.Div([
            html.H6("Comparação de riscos", className="mt-2 mb-2"),
            dbc.Row([
                dbc.Col(html.Div([
                    html.Small("Score: " + str(r1.get("score", "-"))),
                    html.Br(),
                    html.Small("Nível: " + str(r1.get("nivel", "-"))),
                ]), width=6),
                dbc.Col(html.Div([
                    html.Small("Score: " + str(r2.get("score", "-"))),
                    html.Br(),
                    html.Small("Nível: " + str(r2.get("nivel", "-"))),
                ]), width=6),
            ]),
            dcc.Graph(figure=fig, config={"displayModeBar": False}),
        ])
