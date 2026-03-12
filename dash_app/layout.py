"""
Layout do dashboard: barra lateral (upload, histórico, comparação) e área principal (cards, gráficos, seções).
"""
from dash import html, dcc
import dash_bootstrap_components as dbc

try:
    from .database import get_all_contracts
except ImportError:
    get_all_contracts = lambda: []

# IDs para callbacks
ID_UPLOAD = "upload-contract"
ID_MAIN_CONTENT = "main-content"
ID_RESULTADO_STORE = "resultado-store"
ID_CONTRACT_ID_STORE = "contract-id-store"
ID_HISTORY_DROPDOWN = "history-dropdown"
ID_COMPARE_A = "compare-contract-a"
ID_COMPARE_B = "compare-contract-b"
ID_COMPARE_CONTAINER = "compare-container"
ID_LOADING = "loading-analysis"
ID_INTERVAL_LOAD_HISTORY = "interval-load-history"
ID_HISTORY_REFRESH_TRIGGER = "history-refresh-trigger"


def _risk_color(nivel):
    if nivel == "baixo":
        return "success"
    if nivel == "moderado":
        return "warning"
    return "danger"


def _card_metric(title, value, color="primary"):
    return dbc.Card(
        [dbc.CardBody([html.H5(title, className="card-title"), html.H3(value, className="text-" + color)])],
        className="mb-2",
    )


def build_cards(result):
    """Cards de métricas: score, nível, nº cláusulas perigosas, nº multas."""
    nivel = result.get("nivel", "moderado")
    color = _risk_color(nivel)
    return dbc.Row(
        [
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Score de risco", className="text-muted"),
                    html.H2(result.get("score", 0), className="text-" + color),
                ])
            ], className="shadow-sm"), md=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Nível", className="text-muted"),
                    html.H2(nivel.capitalize(), className="text-" + color),
                ])
            ], className="shadow-sm"), md=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Cláusulas perigosas", className="text-muted"),
                    html.H2(len(result.get("clausulas_perigosas", [])), className="text-danger"),
                ])
            ], className="shadow-sm"), md=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H6("Multas detectadas", className="text-muted"),
                    html.H2(len(result.get("multas", [])), className="text-warning"),
                ])
            ], className="shadow-sm"), md=3),
        ],
        className="mb-4 g-3",
    )


def build_sections(result):
    """Seções: multas, retenções, responsabilidades, cláusulas (cards), sugestões."""
    multas = result.get("multas", [])
    retencoes = result.get("retencoes", [])
    resp_contrada = result.get("responsabilidades_contratada", [])
    resp_contante = result.get("responsabilidades_contratante", [])
    clausulas = result.get("clausulas_perigosas", [])
    sugestoes = result.get("sugestoes", [])

    def _list_card(title, items):
        lis = [html.Li(x) for x in items] if items else [html.Li("Nenhum item.", className="text-muted")]
        return dbc.Card([
            dbc.CardHeader(title),
            dbc.CardBody(html.Ul(lis, className="mb-0")),
        ], className="mb-3 shadow-sm")

    def _clausula_card(c):
        texto = c.get("texto", c.get("trecho", ""))
        motivo = c.get("motivo", "")
        return dbc.Card([
            dbc.CardBody([
                html.P(texto, className="fst-italic text-secondary mb-2"),
                html.P(motivo, className="text-danger small mb-0"),
            ])
        ], className="mb-2 border-danger")

    sections = [
        _list_card("Multas detectadas", multas),
        _list_card("Retenções financeiras", retencoes),
        _list_card("Responsabilidades da contratada", resp_contrada),
        _list_card("Responsabilidades da contratante", resp_contante),
        html.H5("Cláusulas perigosas", className="mt-3 mb-2"),
    ]
    for c in clausulas:
        sections.append(_clausula_card(c) if isinstance(c, dict) else dbc.Card(dbc.CardBody(str(c)), className="mb-2"))
    if not clausulas:
        sections.append(html.P("Nenhuma cláusula perigosa identificada.", className="text-muted"))
    sections.append(html.H5("Sugestões de negociação", className="mt-3 mb-2"))
    sections.append(_list_card("", sugestoes) if sugestoes else html.P("Nenhuma sugestão.", className="text-muted"))

    return html.Div(sections)


def build_sidebar():
    """Barra lateral: upload, histórico, comparação."""
    return dbc.Col(
        [
            html.H5("Upload de contrato", className="mb-2"),
            dcc.Upload(
                id=ID_UPLOAD,
                children=dbc.Button("Selecionar PDF", color="primary", className="w-100 mb-3"),
                multiple=False,
            ),
            html.Hr(),
            html.H5("Histórico", className="mb-2"),
            dcc.Dropdown(
                id=ID_HISTORY_DROPDOWN,
                placeholder="Selecione um contrato",
                clearable=True,
                options=[{"label": f"{c['nome_contrato']} — Score {c['score']}", "value": c["id"]} for c in get_all_contracts()],
            ),
            html.Hr(),
            html.H5("Comparar contratos", className="mb-2"),
            dcc.Dropdown(
                id=ID_COMPARE_A,
                placeholder="Contrato A",
                clearable=True,
                className="mb-2",
                options=[{"label": f"{c['nome_contrato']} — {c['score']}", "value": c["id"]} for c in get_all_contracts()],
            ),
            dcc.Dropdown(
                id=ID_COMPARE_B,
                placeholder="Contrato B",
                clearable=True,
                className="mb-2",
                options=[{"label": f"{c['nome_contrato']} — {c['score']}", "value": c["id"]} for c in get_all_contracts()],
            ),
            html.Div(id=ID_COMPARE_CONTAINER),
        ],
        md=3,
        className="bg-light rounded p-3",
    )


def build_main_placeholder():
    """Área principal quando não há análise carregada."""
    return dbc.Alert(
        "Faça upload de um contrato em PDF na barra lateral para ver a análise de risco.",
        color="info",
        className="text-center py-5",
    )


def build_main_from_result(result, radar_fig, bar_fig):
    """Área principal com cards, gráficos e seções a partir do resultado."""
    return html.Div([
        html.H4(result.get("nome_contrato", "Análise"), className="mb-3"),
        build_cards(result),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=radar_fig, config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(figure=bar_fig, config={"displayModeBar": False}), md=6),
        ], className="mb-4"),
        html.Hr(),
        build_sections(result),
    ])


def build_layout():
    """Layout completo: header, sidebar, área principal."""
    return dbc.Container(
        fluid=True,
        children=[
            dcc.Store(id=ID_RESULTADO_STORE, data=None),
            dcc.Store(id=ID_CONTRACT_ID_STORE, data=None),
            dcc.Store(id=ID_HISTORY_REFRESH_TRIGGER, data=None),
            dcc.Interval(id=ID_INTERVAL_LOAD_HISTORY, interval=300, max_intervals=1),
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("AI Contract Risk Analyzer", className="display-5 mb-1"),
                        html.P("Análise inteligente de riscos contratuais", className="text-muted lead"),
                    ],
                    width=12,
                ),
                className="mb-4 mt-3",
            ),
            dbc.Row(
                [
                    build_sidebar(),
                    dbc.Col(
                        [
                            dcc.Loading(
                                id=ID_LOADING,
                                type="default",
                                children=html.Div(id=ID_MAIN_CONTENT, children=build_main_placeholder()),
                            ),
                        ],
                        md=9,
                    ),
                ],
                className="g-3",
            ),
        ],
        className="py-3",
    )
