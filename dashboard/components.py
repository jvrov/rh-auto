"""
Componentes do dashboard: login, abas (Análise / Chat), cards, tabela, chat.
Visual moderno, grid estável, paleta refinada.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dash import html, dcc
import dash_bootstrap_components as dbc

# --- IDs ---
ID_AUTH_STORE = "auth-store"
ID_LOGIN_CONTAINER = "login-container"
ID_MAIN_CONTAINER = "main-container"
ID_PASSWORD_INPUT = "password-input"
ID_LOGIN_BTN = "login-btn"
ID_LOGIN_ERROR = "login-error"
ID_TABS = "main-tabs"
ID_TAB_CHAT = "tab-chat"
ID_TAB_DASHBOARD = "tab-dashboard"
ID_TAB_HISTORY = "tab-history"
ID_TAB_COMPARE = "tab-compare"
ID_TAB_SETTINGS = "tab-settings"
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
ID_HISTORY_TABLE = "history-table"
ID_CHAT_HISTORY_STORE = "chat-history-store"
ID_CHAT_MESSAGES = "chat-messages"
ID_CHAT_INPUT = "chat-input"
ID_CHAT_SEND = "chat-send"
ID_CHAT_LOADING = "chat-loading"
ID_QUICK_PROMPT_1 = "quick-prompt-1"
ID_QUICK_PROMPT_2 = "quick-prompt-2"
ID_QUICK_PROMPT_3 = "quick-prompt-3"
ID_QUICK_PROMPT_4 = "quick-prompt-4"
ID_QUICK_PROMPT_5 = "quick-prompt-5"
ID_PRICING_PANEL = "pricing-panel"
ID_RISKS_PANEL = "risks-panel"
ID_NAV_OVERVIEW = "nav-overview"
ID_NAV_CHAT = "nav-chat"
ID_NAV_DASHBOARD = "nav-dashboard"
ID_NAV_HISTORY = "nav-history"
ID_NAV_COMPARE = "nav-compare"
ID_NAV_SETTINGS = "nav-settings"
ID_NAV_STORE = "nav-store"

ID_DASHBOARD_PANEL = "dashboard-panel"
ID_HISTORY_PANEL = "history-panel"
ID_COMPARE_PANEL = "compare-panel"
ID_SETTINGS_PANEL = "settings-panel"

ID_CHAT_UPLOAD = "chat-upload"

# Estilo global: replicado do industrial-intelligence-hub (via CSS variables em assets/custom.css)
BG_DARK = "hsl(var(--background))"
BG_CARD = "hsl(var(--card))"
BG_SIDEBAR = "hsl(var(--sidebar-background))"
BORDER_RADIUS = "var(--radius)"
ACCENT = "hsl(var(--primary))"
ACCENT_HOVER = "hsl(var(--primary))"
TEXT_PRIMARY = "hsl(var(--foreground))"
TEXT_SECONDARY = "hsl(var(--muted-foreground))"
SIDEBAR_WIDTH = "240px"
CONTENT_MAX_WIDTH = "1200px"


def _risk_color(nivel: str) -> str:
    if nivel == "baixo":
        return "hsl(var(--risk-low))"
    if nivel == "moderado":
        return "hsl(var(--risk-medium))"
    return "hsl(var(--risk-high))"


# --- Tela de login ---
def login_screen():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Contract Risk Analyzer AI", className="mb-2", style={"color": TEXT_PRIMARY, "fontWeight": "700", "fontSize": "1.75rem"}),
                            html.P("Plataforma de IA para análise de contratos e assistente inteligente", style={"color": TEXT_SECONDARY, "marginBottom": "1.5rem"}),
                            html.Div(
                                [
                                    dcc.Input(
                                        id=ID_PASSWORD_INPUT,
                                        type="password",
                                        placeholder="Digite a senha de acesso",
                                        className="form-control form-control-lg",
                                        style={"borderRadius": "10px", "padding": "12px 16px", "maxWidth": "320px", "margin": "0 auto"},
                                        autoComplete="current-password",
                                        n_submit=0,
                                        debounce=True,
                                    ),
                                    html.Div("Senha padrão: XXXX", className="mt-2 small", style={"color": TEXT_SECONDARY}),
                                    html.Div(id=ID_LOGIN_ERROR, className="mt-2"),
                                    dbc.Button(
                                        "Entrar",
                                        id=ID_LOGIN_BTN,
                                        color="primary",
                                        size="lg",
                                        className="mt-3 px-4",
                                        style={"borderRadius": "10px", "background": ACCENT, "border": "none"},
                                        n_clicks=0,
                                    ),
                                ],
                                style={"maxWidth": "320px", "margin": "0 auto"},
                            ),
                        ],
                        style={
                            "background": BG_CARD,
                            "padding": "2.5rem",
                            "borderRadius": "16px",
                            "boxShadow": "0 25px 50px -12px rgba(0,0,0,0.4)",
                            "border": "1px solid rgba(255,255,255,0.06)",
                            "textAlign": "center",
                        },
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "justifyContent": "center", "minHeight": "100vh", "padding": "2rem"},
            ),
        ],
        id=ID_LOGIN_CONTAINER,
        style={"background": BG_DARK},
    )


# --- Análise: score e cards ---
def score_card(result: dict):
    score = result.get("score", 0)
    nivel = result.get("nivel", "moderado")
    nivel_label = {"baixo": "Baixo", "moderado": "Médio", "alto": "Alto"}.get(nivel, "Médio")
    color = _risk_color(nivel)
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Score de risco", className="text-uppercase small", style={"color": TEXT_SECONDARY}),
                        html.Div(str(score), className="display-4 fw-bold", style={"color": color}),
                        html.Div("de 0 a 10", className="small", style={"color": TEXT_SECONDARY}),
                    ]),
                    className="border-0 shadow-sm",
                    style={"borderRadius": BORDER_RADIUS, "background": BG_CARD},
                ),
                width=6, md=6, style={"maxWidth": "300px"},
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div("Nível de risco", className="text-uppercase small", style={"color": TEXT_SECONDARY}),
                        html.Div(nivel_label, className="display-5 fw-bold", style={"color": color}),
                    ]),
                    className="border-0 shadow-sm",
                    style={"borderRadius": BORDER_RADIUS, "background": BG_CARD},
                ),
                width=6, md=6, style={"maxWidth": "300px"},
            ),
        ],
        className="g-3 mb-4",
        style={"maxWidth": "100%"},
    )


def section_cards(result: dict):
    multas = result.get("multas", [])
    retencoes = result.get("retencoes", [])
    resp_contratada = result.get("responsabilidades_contratada", [])
    resp_contratante = result.get("responsabilidades_contratante", [])
    clausulas = result.get("clausulas_perigosas", [])
    sugestoes = result.get("sugestoes", [])

    def _list_card(title: str, items: list):
        lis = [html.Li(x, className="mb-1") for x in items] if items else [html.Li("Nenhum item.", style={"color": TEXT_SECONDARY})]
        return dbc.Card(
            [
                dbc.CardHeader(title, className="fw-semibold", style={"background": "rgba(0,0,0,0.2)", "color": TEXT_PRIMARY, "borderRadius": "10px 10px 0 0"}),
                dbc.CardBody(html.Ul(lis, className="mb-0 ps-3"), style={"background": BG_CARD, "color": TEXT_SECONDARY}),
            ],
            className="mb-3 border-0 shadow-sm",
            style={"borderRadius": BORDER_RADIUS},
        )

    def _clausula_card(c: dict):
        texto = c.get("texto", c.get("trecho", ""))
        motivo = c.get("motivo", "")
        return dbc.Card(
            dbc.CardBody([
                html.P(texto, className="fst-italic small mb-2", style={"color": TEXT_SECONDARY}),
                html.P(motivo, className="small mb-0", style={"color": "#f87171"}),
            ]),
            className="mb-2 border border-danger",
            style={"borderRadius": "10px", "background": BG_CARD},
        )

    cards = [
        _list_card("Multas", multas),
        _list_card("Retenções financeiras", retencoes),
        _list_card("Responsabilidades da contratada", resp_contratada),
        _list_card("Responsabilidades da contratante", resp_contratante),
        html.H5("Cláusulas perigosas", className="mt-3 mb-2", style={"color": TEXT_PRIMARY}),
    ]
    for c in clausulas:
        cards.append(_clausula_card(c) if isinstance(c, dict) else dbc.Card(dbc.CardBody(str(c)), className="mb-2"))
    if not clausulas:
        cards.append(html.P("Nenhuma cláusula perigosa identificada.", style={"color": TEXT_SECONDARY}))
    cards.append(html.H5("Sugestões de negociação", className="mt-3 mb-2", style={"color": TEXT_PRIMARY}))
    cards.append(_list_card("", sugestoes) if sugestoes else html.P("Nenhuma sugestão.", style={"color": TEXT_SECONDARY}))
    return html.Div(cards)


def main_content(result, radar_fig, bar_fig):
    return html.Div([
        html.H4(result.get("nome_contrato", "Análise"), className="mb-3", style={"color": TEXT_PRIMARY}),
        score_card(result),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=radar_fig, config={"displayModeBar": False}), width=12, lg=6, className="mb-3"),
            dbc.Col(dcc.Graph(figure=bar_fig, config={"displayModeBar": False}), width=12, lg=6, className="mb-3"),
        ], className="g-3 mb-4"),
        html.Hr(style={"borderColor": "rgba(255,255,255,0.1)"}),
        section_cards(result),
    ], style={"maxWidth": CONTENT_MAX_WIDTH})


def main_placeholder():
    return dbc.Alert(
        "Envie um PDF na barra lateral para analisar o contrato e ver score, radar de riscos e cláusulas.",
        color="info",
        className="text-center py-5 border-0",
        style={"background": BG_CARD, "color": TEXT_PRIMARY, "borderRadius": BORDER_RADIUS},
    )


def _history_dropdown_options():
    try:
        from app.database import list_projects

        projects = list_projects()
        return [
            {
                "label": f"{p.get('nome_projeto') or 'Projeto'} — Score {p.get('score_risco', '-') } ({(p.get('data_analise') or '')[:10]})",
                "value": p["id"],
            }
            for p in projects
        ]
    except Exception:
        return []


def sidebar_analysis():
    opts = _history_dropdown_options()
    return html.Div(
        [
            html.H6("Projetos analisados", className="mb-2", style={"color": TEXT_PRIMARY}),
            dcc.Dropdown(id=ID_HISTORY_DROPDOWN, placeholder="Selecione um projeto", clearable=True, options=opts, className="mb-3"),
            html.Hr(style={"borderColor": "rgba(255,255,255,0.15)"}),
            html.H6("Comparar projetos", className="mb-2", style={"color": TEXT_PRIMARY}),
            dcc.Dropdown(id=ID_COMPARE_A, placeholder="Contrato A", clearable=True, className="mb-2", options=opts),
            dcc.Dropdown(id=ID_COMPARE_B, placeholder="Contrato B", clearable=True, className="mb-2", options=opts),
            html.Div(id=ID_COMPARE_CONTAINER, className="mt-3"),
        ],
        className="industrial-card",
        style={
            "width": "100%",
            "minWidth": "100%",
            "padding": "1.25rem",
            "borderRadius": BORDER_RADIUS,
            "height": "fit-content",
        },
    )


def chat_home_screen():
    """Home: experiência estilo ChatGPT/Ollama (mensagem + PDF)."""
    return html.Div(
        [
            html.Div(
                [
                    html.Div("Assistente IA para Projetos Industriais", className="project-title", style={"fontSize": "1.5rem"}),
                    html.Div(
                        "Envie uma mensagem e, se quiser, anexe um PDF na mesma interação.",
                        className="project-sub",
                        style={"marginTop": "6px"},
                    ),
                ],
                className="industrial-card",
                style={"marginBottom": "14px"},
            ),
            html.Div(
                [
                    dcc.Loading(
                        id=ID_CHAT_LOADING,
                        type="dot",
                        children=html.Div(
                            render_chat_messages([]),
                            id=ID_CHAT_MESSAGES,
                            className="chat-messages",
                        ),
                    ),
                    html.Div(
                        [
                            dcc.Upload(
                                id=ID_CHAT_UPLOAD,
                                children=dbc.Button("Anexar PDF", color="secondary", className="btn-soft"),
                                multiple=False,
                            ),
                            dcc.Input(
                                id=ID_CHAT_INPUT,
                                type="text",
                                placeholder="Escreva sua pergunta... (ex.: “Analise o PDF e me diga riscos e custos”)",
                                className="form-control chat-input",
                                debounce=False,
                                n_submit=0,
                            ),
                            dbc.Button(
                                "Enviar",
                                id=ID_CHAT_SEND,
                                color="primary",
                                style={"borderRadius": "12px", "background": ACCENT, "border": "none", "height": "48px"},
                            ),
                        ],
                        className="chat-input-row",
                    ),
                ],
                className="industrial-card chat-home",
            ),
            html.Div(
                [
                    html.Div("Sugestões rápidas", className="section-heading", style={"marginBottom": "8px"}),
                    html.Div(
                        [
                            dbc.Button("Resuma este projeto", id=ID_QUICK_PROMPT_1, className="chip"),
                            dbc.Button("Quais são os maiores riscos?", id=ID_QUICK_PROMPT_2, className="chip"),
                            dbc.Button("Sugira um preço de venda", id=ID_QUICK_PROMPT_3, className="chip"),
                            dbc.Button("Quais itens afetam a margem?", id=ID_QUICK_PROMPT_4, className="chip"),
                            dbc.Button("Explique o escopo de forma simples", id=ID_QUICK_PROMPT_5, className="chip"),
                        ],
                        className="chip-row",
                    ),
                ],
                className="industrial-card",
                style={"marginTop": "14px"},
            ),
        ],
        style={"maxWidth": "1100px"},
    )


def history_table(contracts: list):
    if not contracts:
        return html.P("Nenhum contrato analisado ainda.", style={"color": TEXT_SECONDARY})
    header = [html.Thead(html.Tr([html.Th("Contrato"), html.Th("Data"), html.Th("Score")], style={"color": TEXT_SECONDARY}))]
    rows = [
        html.Tr([
            html.Td(c["nome_contrato"], style={"color": TEXT_PRIMARY}),
            html.Td(c["data_analise"][:10] if isinstance(c.get("data_analise"), str) else "-", style={"color": TEXT_SECONDARY}),
            html.Td(c["score"], style={"color": _risk_color(c.get("nivel", "moderado"))}),
        ])
        for c in contracts
    ]
    return html.Div(
        dbc.Table(
            header + [html.Tbody(rows)],
            bordered=False,
            hover=True,
            responsive=True,
            className="mb-0 history-table",
            style={"background": "transparent", "color": TEXT_PRIMARY},
        ),
        className="industrial-card",
        style={"padding": "0", "overflow": "hidden"},
    )


def pricing_panel(pricing: dict | None):
    """Renderiza painel de precificação (custo, margens, faixa)."""
    if not pricing:
        return dbc.Alert(
            "Carregue um documento/projeto para ver a precificação sugerida.",
            color="info",
            className="border-0",
            style={"background": BG_CARD, "color": TEXT_PRIMARY, "borderRadius": BORDER_RADIUS},
        )
    def money(v):
        try:
            return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(v)

    cards = dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Custo total estimado", style={"color": TEXT_SECONDARY}), html.H3(money(pricing.get("custo_total_estimado", 0)), style={"color": TEXT_PRIMARY})]), style={"background": BG_CARD, "borderRadius": BORDER_RADIUS}, className="border-0 shadow-sm"), lg=4, md=6, xs=12),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Margem mínima segura", style={"color": TEXT_SECONDARY}), html.H3(f"{pricing.get('margem_minima_segura', 0)}%", style={"color": TEXT_PRIMARY})]), style={"background": BG_CARD, "borderRadius": BORDER_RADIUS}, className="border-0 shadow-sm"), lg=4, md=6, xs=12),
            dbc.Col(dbc.Card(dbc.CardBody([html.Div("Margem alvo", style={"color": TEXT_SECONDARY}), html.H3(f"{pricing.get('margem_alvo', 0)}%", style={"color": TEXT_PRIMARY})]), style={"background": BG_CARD, "borderRadius": BORDER_RADIUS}, className="border-0 shadow-sm"), lg=4, md=6, xs=12),
        ],
        className="g-3 mb-3",
    )
    faixa = pricing.get("faixa_preco") or [pricing.get("preco_minimo"), pricing.get("preco_recomendado")]
    faixa_txt = f"{money(faixa[0])} a {money(faixa[1])}" if isinstance(faixa, (list, tuple)) and len(faixa) == 2 else "-"
    rec = dbc.Card(
        dbc.CardBody(
            [
                html.Div("Faixa de preço recomendada", style={"color": TEXT_SECONDARY}),
                html.H2(faixa_txt, style={"color": ACCENT}),
                html.Div("Use este valor como referência inicial e ajuste conforme riscos, prazos e condições comerciais.", style={"color": TEXT_SECONDARY}),
            ]
        ),
        className="border-0 shadow-sm",
        style={"background": BG_CARD, "borderRadius": BORDER_RADIUS},
    )
    return html.Div([cards, rec], style={"maxWidth": CONTENT_MAX_WIDTH})


def risks_panel(risks: dict | None):
    """Renderiza painel de riscos por categoria + motivos."""
    if not risks:
        return dbc.Alert(
            "Carregue um documento/projeto para ver os riscos por categoria.",
            color="info",
            className="border-0",
            style={"background": BG_CARD, "color": TEXT_PRIMARY, "borderRadius": BORDER_RADIUS},
        )
    score = risks.get("score_geral", 0)
    nivel = risks.get("nivel_risco", "moderado")
    color = _risk_color(nivel)
    top = dbc.Card(
        dbc.CardBody(
            [
                html.Div("Score geral de risco", style={"color": TEXT_SECONDARY}),
                html.H2(f"{score}", style={"color": color, "fontWeight": "800"}),
                html.Div(f"Nível: {nivel}", style={"color": TEXT_SECONDARY}),
            ]
        ),
        className="border-0 shadow-sm mb-3",
        style={"background": BG_CARD, "borderRadius": BORDER_RADIUS},
    )
    cats = [
        ("Comercial", "risco_comercial"),
        ("Financeiro", "risco_financeiro"),
        ("Contratual", "risco_contratual"),
        ("Técnico", "risco_tecnico"),
        ("Prazo", "risco_prazo"),
        ("Margem", "risco_margem"),
    ]
    grid = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([html.Div(label, style={"color": TEXT_SECONDARY}), html.H3(str(risks.get(key, "-")), style={"color": TEXT_PRIMARY})]),
                    className="border-0 shadow-sm",
                    style={"background": BG_CARD, "borderRadius": BORDER_RADIUS},
                ),
                lg=4, md=6, xs=12,
            )
            for (label, key) in cats
        ],
        className="g-3 mb-3",
    )
    motivos = risks.get("motivos") or []
    motivos_card = dbc.Card(
        [
            dbc.CardHeader("Principais motivos", style={"background": "rgba(0,0,0,0.2)", "color": TEXT_PRIMARY}),
            dbc.CardBody(
                html.Ul([html.Li(m, style={"color": TEXT_SECONDARY}) for m in motivos] or [html.Li("Nenhum motivo registrado.", style={"color": TEXT_SECONDARY})]),
                style={"background": BG_CARD},
            ),
        ],
        className="border-0 shadow-sm",
        style={"borderRadius": BORDER_RADIUS},
    )
    return html.Div([top, grid, motivos_card], style={"maxWidth": CONTENT_MAX_WIDTH})


def _kv(label: str, value: str):
    return html.Div(
        [
            html.Div(label, className="section-heading", style={"marginBottom": "6px"}),
            html.Div(value or "-", style={"color": TEXT_PRIMARY, "fontSize": "14px"}),
        ],
        className="industrial-card",
    )


def overview_sections(project: dict | None):
    if not project:
        return html.Div([main_placeholder()])
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(_kv("Cliente", project.get("cliente", "")), lg=3, md=6, xs=12),
                    dbc.Col(_kv("Projeto", project.get("projeto", "")), lg=3, md=6, xs=12),
                    dbc.Col(_kv("Local da planta", project.get("local_planta", "")), lg=3, md=6, xs=12),
                    dbc.Col(_kv("Tipo do sistema", project.get("tipo_sistema", "")), lg=3, md=6, xs=12),
                ],
                className="g-3 mb-3",
            ),
            html.Div(
                [
                    html.Div("Objetivo do projeto", className="section-heading", style={"marginBottom": "8px"}),
                    html.Div(project.get("objetivo", "") or "-", style={"color": TEXT_PRIMARY, "whiteSpace": "pre-wrap"}),
                ],
                className="industrial-card",
            ),
            html.Div(style={"height": "12px"}),
            html.Div(
                [
                    html.Div("Escopo solicitado", className="section-heading", style={"marginBottom": "8px"}),
                    html.Ul([html.Li(x) for x in (project.get("escopo_solicitado") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                ],
                className="industrial-card",
            ),
        ]
    )


def technical_sections(project: dict | None):
    if not project:
        return html.Div([dbc.Alert("Carregue um PDF para ver o escopo técnico.", color="info", className="border-0")])
    et = project.get("escopo_tecnico") or {}
    def _list(title, items):
        return html.Div(
            [html.Div(title, className="section-heading", style={"marginBottom": "8px"}),
             html.Ul([html.Li(i) for i in (items or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})])],
            className="industrial-card",
        )
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(_list("Equipamentos principais", et.get("equipamentos_principais")), lg=6, xs=12),
                    dbc.Col(_list("Instrumentação", et.get("instrumentacao")), lg=6, xs=12),
                    dbc.Col(_list("Tubulação", et.get("tubulacao")), lg=6, xs=12),
                    dbc.Col(_list("Automação / CLP", (et.get("automacao") or []) + (et.get("clp") or [])), lg=6, xs=12),
                ],
                className="g-3",
            ),
            html.Div(style={"height": "12px"}),
            html.Div(
                [
                    html.Div("Normas técnicas", className="section-heading", style={"marginBottom": "8px"}),
                    html.Ul([html.Li(n) for n in (project.get("normas_tecnicas") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                ],
                className="industrial-card",
            ),
            html.Div(style={"height": "12px"}),
            html.Div(
                [
                    html.Div("Ensaios e documentação exigida", className="section-heading", style={"marginBottom": "8px"}),
                    html.Ul([html.Li(n) for n in (project.get("ensaios_documentacao") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                ],
                className="industrial-card",
            ),
        ]
    )


def commercial_contract_sections(project: dict | None):
    if not project:
        return html.Div([dbc.Alert("Carregue um PDF para ver condições comerciais e análise contratual.", color="info", className="border-0")])
    cc = project.get("condicoes_comerciais") or {}
    ac = project.get("analise_contratual") or {}
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(_kv("Prazo de entrega", cc.get("prazo_entrega", "")), lg=4, md=6, xs=12),
                    dbc.Col(_kv("Retenção contratual", cc.get("retencao_contratual", "")), lg=4, md=6, xs=12),
                    dbc.Col(_kv("Multa por atraso", cc.get("multa_atraso", "")), lg=4, md=6, xs=12),
                ],
                className="g-3 mb-3",
            ),
            html.Div(
                [
                    html.Div("Forma de pagamento", className="section-heading", style={"marginBottom": "8px"}),
                    html.Ul([html.Li(x) for x in (cc.get("forma_pagamento") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                ],
                className="industrial-card",
            ),
            html.Div(style={"height": "12px"}),
            html.Div(
                [
                    html.Div("Análise contratual (multas / retenções / responsabilidades)", className="section-heading", style={"marginBottom": "8px"}),
                    html.Div(f"Score de risco contratual: {ac.get('score_risco', 0)}", style={"color": TEXT_PRIMARY, "marginBottom": "8px"}),
                    html.Div("Multas:", style={"color": TEXT_SECONDARY}),
                    html.Ul([html.Li(x) for x in (ac.get("multas") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                    html.Div("Retenções:", style={"color": TEXT_SECONDARY}),
                    html.Ul([html.Li(x) for x in (ac.get("retencoes") or [])] or [html.Li("—", style={"color": TEXT_SECONDARY})]),
                ],
                className="industrial-card",
            ),
        ]
    )


def bom_capex_sections(project: dict | None):
    if not project:
        return html.Div([dbc.Alert("Carregue um PDF para ver BOM e CAPEX.", color="info", className="border-0")])
    bom = project.get("bom") or []
    capex = project.get("capex") or {}
    # tabela BOM (simplificada)
    if bom:
        header = html.Thead(html.Tr([html.Th("Item"), html.Th("Tag"), html.Th("Descrição"), html.Th("Qtd"), html.Th("Material"), html.Th("Custo total")]))
        rows = []
        for it in bom[:200]:
            rows.append(html.Tr([
                html.Td(it.get("item","")),
                html.Td(it.get("tag","")),
                html.Td(it.get("descricao","")),
                html.Td(it.get("quantidade","")),
                html.Td(it.get("material","")),
                html.Td(it.get("custo_total","")),
            ]))
        table = dbc.Table([header, html.Tbody(rows)], responsive=True, hover=True, className="mb-0 history-table")
        bom_block = html.Div(table, className="industrial-card", style={"padding": "0", "overflow": "hidden"})
    else:
        bom_block = dbc.Alert("BOM não identificada no documento.", color="info", className="border-0", style={"background": BG_CARD})

    capex_cards = dbc.Row(
        [
            dbc.Col(_kv("Materiais", str(capex.get("materiais", 0))), lg=3, md=6, xs=12),
            dbc.Col(_kv("Engenharia", str(capex.get("engenharia", 0))), lg=3, md=6, xs=12),
            dbc.Col(_kv("Montagem mecânica", str(capex.get("montagem_mecanica", 0))), lg=3, md=6, xs=12),
            dbc.Col(_kv("Custo total", str(capex.get("custo_total", 0))), lg=3, md=6, xs=12),
        ],
        className="g-3 mb-3",
    )
    return html.Div([capex_cards, bom_block])


def executive_section(project: dict | None):
    if not project:
        return html.Div([dbc.Alert("Carregue um PDF para ver o resumo executivo.", color="info", className="border-0")])
    re_ = project.get("resumo_executivo") or {}
    text = re_.get("texto") if isinstance(re_, dict) else (re_ or "")
    rec = re_.get("recomendacao") if isinstance(re_, dict) else ""
    bullets = re_.get("principais_pontos") if isinstance(re_, dict) else []
    return html.Div(
        [
            html.Div("Resumo executivo", className="section-heading", style={"marginBottom": "8px"}),
            html.Div(text or "—", style={"whiteSpace": "pre-wrap", "color": TEXT_PRIMARY}),
            html.Div(rec, className="summary-rec") if rec else html.Div(),
            html.Ul([html.Li(x) for x in (bullets or [])[:8]], className="summary-bullets") if bullets else html.Div(),
        ],
        className="industrial-card",
    )


def _metric_card(label: str, value: str, *, tone: str = "default"):
    tone_class = {
        "default": "metric-border-neutral",
        "primary": "metric-border-primary",
        "danger": "metric-border-danger",
        "success": "metric-border-success",
        "warning": "metric-border-warning",
    }.get(tone, "metric-border-neutral")
    return html.Div(
        [
            html.Div(label, className="metric-label"),
            html.Div(value, className="metric-value"),
        ],
        className=f"metric-card {tone_class}",
    )


def _status_badge(status: str):
    mapping = {
        "novo": ("Novo", "neutral"),
        "em_analise": ("Em análise", "warning"),
        "precificado": ("Precificado", "primary"),
        "em_revisao": ("Em revisão", "warning"),
        "concluido": ("Concluído", "success"),
    }
    label, tone = mapping.get(status, (status or "Novo", "neutral"))
    cls = f"status-badge status-{tone}"
    return html.Span(label, className=cls)


def _alerts_block(project: dict | None):
    if not project:
        return html.Div(
            [
                html.Div("Alertas críticos", className="section-heading", style={"marginBottom": "8px"}),
                html.Div("Carregue um PDF para ver alertas.", className="empty-muted"),
            ],
            className="industrial-card",
        )
    alerts = project.get("alertas_criticos") or []
    items = []
    if isinstance(alerts, list):
        for a in alerts[:8]:
            if not isinstance(a, dict):
                continue
            sev = (a.get("severidade") or "atencao").lower()
            sev_cls = {"critico": "alert-critical", "atencao": "alert-warning", "info": "alert-info"}.get(sev, "alert-warning")
            items.append(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(a.get("titulo") or "Alerta", className="alert-title"),
                                html.Span(sev.upper(), className=f"alert-pill {sev_cls}"),
                            ],
                            className="alert-head",
                        ),
                        html.Div(a.get("mensagem") or "", className="alert-msg"),
                    ],
                    className="alert-item",
                )
            )
    if not items:
        items = [html.Div("Nenhum alerta crítico identificado.", className="empty-muted")]
    return html.Div(
        [
            html.Div("Alertas críticos", className="section-heading", style={"marginBottom": "8px"}),
            html.Div(items, className="alerts-list"),
        ],
        className="industrial-card",
    )


def _executive_summary_block(project: dict | None):
    if not project:
        return html.Div(
            [
                html.Div("Resumo executivo", className="section-heading", style={"marginBottom": "8px"}),
                html.Div("Carregue um PDF para ver o resumo.", className="empty-muted"),
            ],
            className="industrial-card",
        )
    re_ = project.get("resumo_executivo") or {}
    text = re_.get("texto") if isinstance(re_, dict) else (re_ or "")
    rec = re_.get("recomendacao") if isinstance(re_, dict) else ""
    bullets = re_.get("principais_pontos") if isinstance(re_, dict) else []
    return html.Div(
        [
            html.Div("Resumo executivo", className="section-heading", style={"marginBottom": "8px"}),
            html.Div(text or "—", className="summary-text"),
            html.Div(rec, className="summary-rec") if rec else html.Div(),
            html.Ul([html.Li(x) for x in (bullets or [])[:6]], className="summary-bullets") if bullets else html.Div(),
        ],
        className="industrial-card",
    )


def _overview_executive(project: dict | None):
    # Header executivo
    nome = (project or {}).get("projeto") or "Nenhum projeto carregado"
    cliente = (project or {}).get("cliente") or "Cliente não identificado"
    status = (project or {}).get("status_projeto") or "novo"
    alertas = (project or {}).get("alertas_criticos") or []

    riscos = (project or {}).get("riscos") or {}
    prec = (project or {}).get("precificacao") or {}
    capex = (project or {}).get("capex") or {}
    score = float(riscos.get("score_geral", 0) or 0)
    custo = float(capex.get("custo_total", 0) or 0)
    preco = float(prec.get("preco_recomendado", 0) or 0)
    margem = float(prec.get("margem_sugerida", 0) or 0)
    prazo = ((project or {}).get("prazo_estimado") or ((project or {}).get("condicoes_comerciais") or {}).get("prazo_entrega") or "não identificado")

    # Tonalidade do risco
    risk_tone = "success" if score and score < 4 else "warning" if score and score < 7 else "danger" if score >= 7 else "default"

    header = html.Div(
        [
            html.Div(
                [
                    html.Div(nome, className="project-title"),
                    html.Div(
                        [
                            html.Span(cliente, className="project-sub"),
                            _status_badge(status),
                            html.Span(f"{len(alertas)} alertas", className="status-badge status-warning"),
                        ],
                        className="project-meta",
                    ),
                ],
                className="project-head-left",
            ),
            html.Div(
                [
                    dbc.Button("Exportar análise", id="btn-export", color="secondary", className="btn-soft"),
                    dbc.Button("Reanalisar", id="btn-reanalyze", color="secondary", className="btn-soft"),
                ],
                className="project-actions",
            ),
        ],
        className="project-header industrial-card",
    )

    metrics = html.Div(
        [
            _metric_card("Score de risco", f"{score:.1f}/10" if score else "—", tone=risk_tone),
            _metric_card("Status", str(status).replace("_", " ").title() if status else "Novo", tone="default"),
            _metric_card("Custo estimado", f"{custo:,.2f}" if custo else "—", tone="default"),
            _metric_card("Preço sugerido", f"{preco:,.2f}" if preco else "—", tone="primary"),
            _metric_card("Margem recomendada", f"{margem:.1f}%" if margem else "—", tone="default"),
            _metric_card("Prazo", str(prazo) if prazo else "—", tone="default"),
        ],
        className="metric-grid",
    )

    line3 = html.Div([_executive_summary_block(project), _alerts_block(project)], className="grid-2")

    # Escopo + comercial/contrato (resumo)
    escopo = (project or {}).get("escopo_solicitado") or []
    cc = (project or {}).get("condicoes_comerciais") or {}
    line4 = html.Div(
        [
            html.Div(
                [
                    html.Div("Escopo solicitado", className="section-heading", style={"marginBottom": "8px"}),
                    html.Ul([html.Li(x) for x in (escopo or [])[:12]], className="list-clean") if escopo else html.Div("não informado no documento", className="empty-muted"),
                ],
                className="industrial-card",
            ),
            html.Div(
                [
                    html.Div("Condições comerciais / contratuais", className="section-heading", style={"marginBottom": "8px"}),
                    html.Div(
                        [
                            _kv("Prazo de entrega", cc.get("prazo_entrega", "")),
                            _kv("Retenção", cc.get("retencao_contratual", "")),
                            _kv("Multa por atraso", cc.get("multa_atraso", "")),
                            _kv("Garantia", cc.get("garantia", "")),
                        ],
                        className="kv-grid",
                    ),
                ],
                className="industrial-card",
            ),
        ],
        className="grid-2",
    )
    return html.Div([header, metrics, line3, line4], className="overview-exec")


# --- Chat ---
def chat_context_header(project: dict | None):
    if not project:
        return html.Div("Carregue um projeto para ativar o contexto do chat.", className="empty-muted")
    riscos = project.get("riscos") or {}
    prec = project.get("precificacao") or {}
    return html.Div(
        [
            html.Div((project or {}).get("projeto") or "Projeto sem nome", className="chat-context-title"),
            html.Div(
                [
                    html.Span(f"Status: {project.get('status_projeto') or 'novo'}", className="chat-context-pill"),
                    html.Span(f"Risco: {float(riscos.get('score_geral', 0) or 0):.1f}/10", className="chat-context-pill"),
                    html.Span(
                        f"Preço: {float(prec.get('preco_recomendado', 0) or 0):,.2f}" if float(prec.get("preco_recomendado", 0) or 0) else "Preço: —",
                        className="chat-context-pill",
                    ),
                ],
                className="chat-context-row",
            ),
        ],
        className="chat-context-header",
    )


def chat_tab_content(project: dict | None = None):
    return html.Div(
        [
            chat_context_header(project),
            dcc.Loading(
                id=ID_CHAT_LOADING,
                type="dot",
                children=html.Div(
                    render_chat_messages([]),
                    id=ID_CHAT_MESSAGES,
                    style={
                        "minHeight": "360px",
                        "maxHeight": "56vh",
                        "overflowY": "auto",
                        "background": BG_CARD,
                        "borderRadius": BORDER_RADIUS,
                        "padding": "1rem",
                        "marginBottom": "1rem",
                    },
                ),
            ),
            html.Div(
                [
                    dcc.Input(
                        id=ID_CHAT_INPUT,
                        type="text",
                        placeholder="Digite sua mensagem...",
                        className="form-control chat-input",
                        style={
                            "flex": "1 1 auto",
                            "width": "100%",
                            "height": "48px",
                            "minHeight": "48px",
                            "borderRadius": "12px",
                            "marginRight": "8px",
                            "padding": "0 16px",
                            "boxSizing": "border-box",
                            "lineHeight": "48px",
                        },
                        debounce=False,
                        n_submit=0,
                    ),
                    dbc.Button(
                        "Enviar",
                        id=ID_CHAT_SEND,
                        color="primary",
                        style={"borderRadius": "10px", "background": ACCENT, "border": "none"},
                    ),
                ],
                style={"display": "flex", "alignItems": "stretch", "gap": "8px"},
            ),
        ],
        style={"width": "100%", "maxWidth": "100%"},
    )


def chat_side_panel():
    """Chat em painel lateral (junto da análise)."""
    return html.Div(
        [
            html.Div("Chat com IA", className="section-heading", style={"marginBottom": "10px"}),
            chat_tab_content(None),
        ],
        className="industrial-card",
        style={
            "height": "calc(100vh - 56px - 48px)",  # header + padding aproximado
            "position": "sticky",
            "top": "72px",
            "overflow": "hidden",
        },
    )


def render_chat_messages(history: list):
    """Gera a lista de mensagens para exibição."""
    if not history:
        return html.P("Nenhuma mensagem ainda. Envie uma pergunta ou comando.", style={"color": TEXT_SECONDARY})
    children = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if not content:
            continue
        is_user = role == "user"
        author = "Você" if is_user else "IA"
        inner_style = {
            "padding": "14px 16px",
            "borderRadius": "14px",
            "maxWidth": "88%",
            "whiteSpace": "pre-wrap",
            "wordBreak": "break-word",
            "boxShadow": "0 8px 24px rgba(0,0,0,0.16)",
        }
        if is_user:
            inner_style["background"] = ACCENT
            inner_style["color"] = "white"
            inner_style["marginLeft"] = "auto"
        else:
            inner_style["background"] = "rgba(255,255,255,0.07)"
            inner_style["color"] = TEXT_PRIMARY
        children.append(
            html.Div(
                [
                    html.Div(author, className="chat-author"),
                    html.Div(content, style=inner_style),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "flex-end" if is_user else "flex-start",
                    "marginBottom": "14px",
                },
            ),
        )
    return html.Div(children)


# --- Layout principal (abas) ---
def build_main_layout():
    """Compatibilidade: retorna só o container interno para tab-content."""
    return build_main_layout_with_panels()


def build_tab_analysis_content():
    """Conteúdo da aba Visão geral: upload + visão geral + histórico + comparação."""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(sidebar_analysis(), width=12, lg=3, style={"maxWidth": SIDEBAR_WIDTH}),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Loading(
                                            id=ID_LOADING,
                                            type="default",
                                            children=html.Div(id=ID_MAIN_CONTENT, children=_overview_executive(None)),
                                        ),
                                    ],
                                    lg=8,
                                    md=12,
                                    xs=12,
                                    style={"minWidth": 0},
                                ),
                            ],
                            className="g-3",
                        ),
                        width=12,
                        lg=9,
                        style={"minWidth": 0},
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.H5("Histórico de projetos", className="mt-4 mb-2", style={"color": TEXT_PRIMARY}),
                        html.Div(id=ID_HISTORY_TABLE),
                    ],
                    width=12,
                ),
                className="mt-3",
            ),
        ],
    )


ID_ANALYSIS_PANEL = "analysis-panel"


def build_layout():
    """Layout raiz: stores + login ou app principal."""
    return html.Div(
        [
            dcc.Store(id=ID_AUTH_STORE, data=False),
            dcc.Store(id=ID_RESULTADO_STORE, data=None),
            dcc.Store(id=ID_CONTRACT_ID_STORE, data=None),
            dcc.Store(id=ID_HISTORY_REFRESH_TRIGGER, data=None),
            dcc.Store(id=ID_CHAT_HISTORY_STORE, data=[]),
            dcc.Store(id=ID_NAV_STORE, data="tab-overview"),
            dcc.Interval(id=ID_INTERVAL_LOAD_HISTORY, interval=500, max_intervals=1),
            login_screen(),
            html.Div(
                id=ID_MAIN_CONTAINER,
                style={"display": "none"},
                children=[
                    build_main_layout_with_panels(),
                ],
            ),
        ],
        style={"minHeight": "100vh", "background": BG_DARK},
    )


def build_main_layout_with_panels():
    """App principal com abas; ambas as áreas no DOM."""
    # Mantemos dbc.Tabs (escondido) para reusar o callback de switch_tab
    hidden_tabs = dbc.Tabs(
        id=ID_TABS,
        active_tab=ID_TAB_CHAT,
        children=[
            dbc.Tab(label="Chat", tab_id=ID_TAB_CHAT),
            dbc.Tab(label="Dashboard", tab_id=ID_TAB_DASHBOARD),
            dbc.Tab(label="Histórico", tab_id=ID_TAB_HISTORY),
            dbc.Tab(label="Comparação", tab_id=ID_TAB_COMPARE),
            dbc.Tab(label="Configurações", tab_id=ID_TAB_SETTINGS),
        ],
        style={"display": "none"},
    )

    sidebar = html.Aside(
        [
            html.Div(
                [
                    html.Div("IIH", className="app-logo"),
                    html.Div(
                        [
                            html.Div("PrecificaIA", className="name"),
                            html.Div("Análise inteligente", className="tag"),
                        ],
                        className="sidebar-title",
                    ),
                ],
                className="sidebar-header",
            ),
            html.Div(
                [
                    html.Div("Navegação", className="section-heading", style={"padding": "0 10px", "marginBottom": "10px"}),
                    html.Div("Chat", id=ID_NAV_CHAT, className="nav-item active"),
                    html.Div("Dashboard", id=ID_NAV_DASHBOARD, className="nav-item"),
                    html.Div("Histórico", id=ID_NAV_HISTORY, className="nav-item"),
                    html.Div("Comparação", id=ID_NAV_COMPARE, className="nav-item"),
                    html.Div("Configurações", id=ID_NAV_SETTINGS, className="nav-item"),
                ],
                className="app-nav",
            ),
        ],
        className="app-sidebar",
    )

    header = html.Header(
        [
            html.Div(
                [
                    html.Span("Projetos"),
                    html.Span(" / ", style={"opacity": 0.5}),
                    html.Strong("Projeto atual"),
                    html.Span("  ", style={"marginLeft": "8px"}),
                    html.Span("ATIVO", className="status-badge", style={"borderColor": "color-mix(in oklab, hsl(var(--success)) 30%, transparent)", "color": "hsl(var(--success))"}),
                ],
                className="header-breadcrumb",
            ),
        ],
        className="app-header",
    )

    content = html.Div(
        [
            hidden_tabs,
            html.Div(chat_home_screen(), id=ID_ANALYSIS_PANEL),
            html.Div(_overview_executive(None), id=ID_DASHBOARD_PANEL, style={"display": "none"}),
            html.Div(
                [
                    html.Div("Histórico", className="section-heading", style={"marginBottom": "10px"}),
                    html.Div(id=ID_HISTORY_TABLE),
                ],
                id=ID_HISTORY_PANEL,
                style={"display": "none"},
            ),
            html.Div(
                [
                    html.Div("Comparação", className="section-heading", style={"marginBottom": "10px"}),
                    sidebar_analysis(),
                ],
                id=ID_COMPARE_PANEL,
                style={"display": "none"},
            ),
            html.Div(
                dbc.Alert("Configurações (em breve).", color="info", className="border-0"),
                id=ID_SETTINGS_PANEL,
                style={"display": "none"},
            ),
        ],
        className="app-content",
        id="tab-content",
    )

    main = html.Div([header, content], className="app-main")
    return html.Div([sidebar, main], className="app-shell")
