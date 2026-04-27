"""
Dashboard: análise de contratos + chat com IA.
Tela de login, abas (Análise / Chat), callbacks.
"""
import sys
from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import base64
import logging
from dash import Dash, Input, Output, State, html, no_update, ctx
import dash_bootstrap_components as dbc

from dashboard import components as comp
from dashboard.charts import create_radar_chart, create_bar_chart, create_radar_comparison
from app.pdf_parser import extract_text_from_pdf
from app.project_intelligence import analyze_industrial_project
from app.auth import check_password
from app.chat_engine import get_chat_response
from config import DATABASE_PATH
from app.database import (
    init_db as init_sqlite_db,
    create_project,
    list_projects,
    get_project,
    add_chat_message,
    list_chat_history,
    add_uploaded_document,
    upsert_project_alerts,
)
from app.pricing_engine import estimate_cost_total, simulate_pricing
from app.risk_engine_v2 import compute_project_risks
from domain.normalize import normalize_project

logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


def _parse_upload(contents):
    if not contents:
        return None, None
    try:
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        tmp = ROOT / "uploads" / "_tmp_upload.pdf"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(decoded)
        nome = "contrato.pdf"
        text = extract_text_from_pdf(tmp)
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        return nome, text
    except Exception as e:
        return None, str(e)


def _build_main_content(result):
    radar_fig = create_radar_chart(result)
    bar_fig = create_bar_chart(result)
    return comp.main_content(result, radar_fig, bar_fig)


def _history_options():
    return [
        {
            "label": f"{(p.get('nome_projeto') or 'Projeto')} — Score {p.get('score_risco', '-') } ({(p.get('data_analise') or '')[:10]})",
            "value": p["id"],
        }
        for p in list_projects()
    ]


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    # IMPORTANTE: carregar assets do projeto (idi_project/assets)
    assets_folder=str(ROOT / "assets"),
)
app.title = "Contract Risk Analyzer AI"
app.layout = comp.build_layout()

# Banco principal (SQLite)
init_sqlite_db(DATABASE_PATH)


# --- Login: mostrar/ocultar tela e validar senha ---
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
    trigger = ctx.trigger_id if hasattr(ctx, "trigger_id") else "?"
    try:
        # não tentar autenticar se o campo estiver vazio
        if not (password or "").strip():
            logger.debug("Senha vazia, ignorando.")
            return no_update, no_update, no_update

        if check_password(password):
            logger.info("Senha OK, autenticando.")
            return True, "", ""
        logger.warning("Senha incorreta.")
        return no_update, dbc.Alert("Senha incorreta. Tente novamente.", color="danger", className="mb-0"), ""
    except Exception as e:
        logger.exception("Erro no login")
        return no_update, dbc.Alert(f"Erro ao entrar: {e}", color="danger", className="mb-0"), no_update


# --- Abas: mostrar painel correto ---
@app.callback(
    [
        Output(comp.ID_ANALYSIS_PANEL, "style"),
        Output(comp.ID_TECH_PANEL, "style"),
        Output(comp.ID_COMMERCIAL_PANEL, "style"),
        Output(comp.ID_BOM_PANEL, "style"),
        Output(comp.ID_PRICING_PANEL, "style"),
        Output(comp.ID_RISKS_PANEL, "style"),
        Output(comp.ID_EXEC_PANEL, "style"),
    ],
    Input(comp.ID_TABS, "active_tab"),
)
def switch_tab(active_tab):
    hidden = {"display": "none"}
    shown = {"display": "block"}
    if active_tab == "tab-tech":
        return hidden, shown, hidden, hidden, hidden, hidden, hidden
    if active_tab == "tab-commercial":
        return hidden, hidden, shown, hidden, hidden, hidden, hidden
    if active_tab == "tab-bom":
        return hidden, hidden, hidden, shown, hidden, hidden, hidden
    if active_tab == "tab-pricing":
        return hidden, hidden, hidden, hidden, shown, hidden, hidden
    if active_tab == "tab-risks":
        return hidden, hidden, hidden, hidden, hidden, shown, hidden
    if active_tab == "tab-exec":
        return hidden, hidden, hidden, hidden, hidden, hidden, shown
    # overview / default
    return shown, hidden, hidden, hidden, hidden, hidden, hidden


@app.callback(
    [
        Output(comp.ID_NAV_OVERVIEW, "className"),
        Output(comp.ID_NAV_TECH, "className"),
        Output(comp.ID_NAV_COMMERCIAL, "className"),
        Output(comp.ID_NAV_BOM, "className"),
        Output(comp.ID_NAV_PRICING, "className"),
        Output(comp.ID_NAV_RISKS, "className"),
        Output(comp.ID_NAV_EXEC, "className"),
    ],
    Input(comp.ID_TABS, "active_tab"),
)
def highlight_nav(active_tab):
    def cls(is_active: bool) -> str:
        return "nav-item active" if is_active else "nav-item"
    return (
        cls(active_tab == "tab-overview"),
        cls(active_tab == "tab-tech"),
        cls(active_tab == "tab-commercial"),
        cls(active_tab == "tab-bom"),
        cls(active_tab == "tab-pricing"),
        cls(active_tab == "tab-risks"),
        cls(active_tab == "tab-exec"),
    )


# Sidebar navigation -> Tabs active_tab
@app.callback(
    Output(comp.ID_TABS, "active_tab"),
    [
        Input(comp.ID_NAV_OVERVIEW, "n_clicks"),
        Input(comp.ID_NAV_TECH, "n_clicks"),
        Input(comp.ID_NAV_COMMERCIAL, "n_clicks"),
        Input(comp.ID_NAV_BOM, "n_clicks"),
        Input(comp.ID_NAV_PRICING, "n_clicks"),
        Input(comp.ID_NAV_RISKS, "n_clicks"),
        Input(comp.ID_NAV_EXEC, "n_clicks"),
    ],
    prevent_initial_call=True,
)
def nav_to_tab(n_overview, n_tech, n_commercial, n_bom, n_pricing, n_risks, n_exec):
    from dash import callback_context
    if not callback_context.triggered:
        return no_update
    tid = callback_context.triggered[0]["prop_id"].split(".")[0]
    if tid == comp.ID_NAV_TECH:
        return "tab-tech"
    if tid == comp.ID_NAV_COMMERCIAL:
        return "tab-commercial"
    if tid == comp.ID_NAV_BOM:
        return "tab-bom"
    if tid == comp.ID_NAV_PRICING:
        return "tab-pricing"
    if tid == comp.ID_NAV_RISKS:
        return "tab-risks"
    if tid == comp.ID_NAV_EXEC:
        return "tab-exec"
    return "tab-overview"


# --- Histórico e dropdowns ---
@app.callback(
    [
        Output(comp.ID_HISTORY_DROPDOWN, "options"),
        Output(comp.ID_COMPARE_A, "options"),
        Output(comp.ID_COMPARE_B, "options"),
        Output(comp.ID_HISTORY_TABLE, "children"),
    ],
    [
        Input(comp.ID_INTERVAL_LOAD_HISTORY, "n_intervals"),
        Input(comp.ID_HISTORY_REFRESH_TRIGGER, "data"),
    ],
    prevent_initial_call=False,
)
def refresh_history_and_table(n_intervals, _trigger):
    opts = _history_options()
    projects = list_projects()
    # Adaptar para o componente legado de tabela (contratos)
    contracts_like = [
        {
            "id": p["id"],
            "nome_contrato": p.get("nome_projeto") or "Projeto",
            "score": p.get("score_risco"),
            "nivel": p.get("nivel_risco") or "moderado",
            "data_analise": p.get("data_analise") or "",
        }
        for p in projects
    ]
    table = comp.history_table(contracts_like)
    return opts, opts, opts, table


# --- Precificação e Riscos: derivar a partir do resultado atual (legado contrato) ---
@app.callback(
    [Output(comp.ID_PRICING_PANEL, "children"), Output(comp.ID_RISKS_PANEL, "children")],
    Input(comp.ID_RESULTADO_STORE, "data"),
)
def update_pricing_and_risks(current_result):
    if not current_result:
        return comp.pricing_panel(None), comp.risks_panel(None)
    # Novo schema já inclui precificação/riscos
    capex_total = float((current_result.get("capex") or {}).get("custo_total", 0) or 0)
    prec = current_result.get("precificacao") or {}
    pricing_dict = {
        "custo_total_estimado": capex_total,
        "margem_minima_segura": prec.get("margem_minima_segura", 18),
        "margem_alvo": prec.get("margem_sugerida", 25),
        "preco_minimo": prec.get("preco_minimo", 0),
        "preco_recomendado": prec.get("preco_recomendado", 0),
        "faixa_preco": (prec.get("preco_minimo", 0), prec.get("preco_recomendado", 0)),
    }
    r = current_result.get("riscos") or {}
    risks_dict = {
        "score_geral": r.get("score_geral", 0),
        "nivel_risco": "alto" if float(r.get("score_geral", 0) or 0) >= 7 else "moderado" if float(r.get("score_geral", 0) or 0) >= 4 else "baixo",
        "risco_comercial": r.get("risco_comercial", 0),
        "risco_financeiro": r.get("risco_financeiro", 0),
        "risco_contratual": r.get("risco_contratual", 0),
        "risco_tecnico": r.get("risco_tecnico", 0),
        "risco_prazo": r.get("risco_prazo", 0),
        "risco_margem": r.get("risco_margem", 0),
        "motivos": r.get("motivos", []),
    }
    return comp.pricing_panel(pricing_dict), comp.risks_panel(risks_dict)


@app.callback(
    [
        Output(comp.ID_MAIN_CONTENT, "children"),
        Output(comp.ID_TECH_PANEL, "children"),
        Output(comp.ID_COMMERCIAL_PANEL, "children"),
        Output(comp.ID_BOM_PANEL, "children"),
        Output(comp.ID_EXEC_PANEL, "children"),
    ],
    Input(comp.ID_RESULTADO_STORE, "data"),
)
def update_project_sections(project):
    if not project:
        return comp._overview_executive(None), comp.technical_sections(None), comp.commercial_contract_sections(None), comp.bom_capex_sections(None), comp.executive_section(None)
    return (
        comp._overview_executive(project),
        comp.technical_sections(project),
        comp.commercial_contract_sections(project),
        comp.bom_capex_sections(project),
        comp.executive_section(project),
    )


# --- Upload e análise ---
@app.callback(
    [
        Output(comp.ID_RESULTADO_STORE, "data"),
        Output(comp.ID_CONTRACT_ID_STORE, "data"),
        Output(comp.ID_HISTORY_REFRESH_TRIGGER, "data"),
    ],
    Input(comp.ID_UPLOAD, "contents"),
    State(comp.ID_UPLOAD, "filename"),
    prevent_initial_call=True,
)
def on_upload(contents, filename):
    if not contents:
        return no_update, no_update, no_update
    nome_arquivo = filename or "contrato.pdf"
    nome, text = _parse_upload(contents)
    if text is None and nome is None:
        return no_update, no_update, no_update
    if nome is None:
        return no_update, no_update, no_update
    try:
        result = normalize_project(analyze_industrial_project(text, filename=nome_arquivo))
    except Exception as e:
        return no_update, no_update, no_update
    # Persistir como projeto (legado contrato) no SQLite
    project_id = create_project(
        nome_projeto=result.get("projeto") or nome_arquivo,
        cliente=result.get("cliente") or None,
        score_risco=float((result.get("riscos") or {}).get("score_geral")) if result.get("riscos") else None,
        nivel_risco=None,
        custo_total_estimado=float((result.get("capex") or {}).get("custo_total", 0) or 0) if isinstance(result.get("capex"), dict) else None,
        margem_sugerida=float((result.get("precificacao") or {}).get("margem_sugerida")) if result.get("precificacao") else None,
        preco_sugerido=float((result.get("precificacao") or {}).get("preco_recomendado")) if result.get("precificacao") else None,
        resumo=result,
    )
    # Persistir documento + alertas críticos
    try:
        add_uploaded_document(
            project_id=project_id,
            nome_arquivo=nome_arquivo,
            tipo_documento="pdf",
            caminho_arquivo=None,
            texto_extraido=text,
        )
    except Exception:
        pass
    try:
        upsert_project_alerts(project_id, result.get("alertas_criticos") or [])
    except Exception:
        pass
    # A UI (main-content e painéis) é derivada do ID_RESULTADO_STORE via update_project_sections.
    return result, project_id, project_id


# --- Histórico: selecionar contrato ---
@app.callback(
    [
        Output(comp.ID_RESULTADO_STORE, "data", allow_duplicate=True),
        Output(comp.ID_CONTRACT_ID_STORE, "data", allow_duplicate=True),
        Output(comp.ID_CHAT_HISTORY_STORE, "data", allow_duplicate=True),
        Output(comp.ID_CHAT_MESSAGES, "children", allow_duplicate=True),
    ],
    Input(comp.ID_HISTORY_DROPDOWN, "value"),
    prevent_initial_call=True,
)
def on_history_select(contract_id):
    if not contract_id:
        return no_update, no_update, no_update, no_update
    row = get_project(int(contract_id))
    if not row:
        return no_update, no_update, no_update, no_update
    result = row.get("resumo") or {}
    hist = list_chat_history(int(contract_id), limit=200)
    chat_data = [{"role": h.get("role"), "content": h.get("mensagem")} for h in hist]
    return result, contract_id, chat_data, comp.render_chat_messages(chat_data)


# --- Comparação ---
@app.callback(
    Output(comp.ID_COMPARE_CONTAINER, "children"),
    [Input(comp.ID_COMPARE_A, "value"), Input(comp.ID_COMPARE_B, "value")],
)
def on_compare(ida, idb):
    if not ida or not idb or ida == idb:
        return html.Div()
    c1 = get_project(int(ida))
    c2 = get_project(int(idb))
    if not c1 or not c2:
        return html.Div()
    s1 = c1.get("resumo") or {}
    s2 = c2.get("resumo") or {}
    r1, r2 = (s1.get("resultado") or {}), (s2.get("resultado") or {})
    fig = create_radar_comparison(r1, r2, c1.get("nome_projeto") or "Projeto A", c2.get("nome_projeto") or "Projeto B")
    return html.Div(
        [
            html.H6("Comparação de riscos", className="mt-2 mb-2", style={"color": comp.TEXT_PRIMARY}),
            dbc.Row(
                [
                    dbc.Col(html.Div([html.Small(f"Score: {r1.get('score', '-')}"), html.Br(), html.Small(f"Nível: {r1.get('nivel', '-')}")], style={"color": comp.TEXT_SECONDARY}), width=6),
                    dbc.Col(html.Div([html.Small(f"Score: {r2.get('score', '-')}"), html.Br(), html.Small(f"Nível: {r2.get('nivel', '-')}")], style={"color": comp.TEXT_SECONDARY}), width=6),
                ]
            ),
            dcc.Graph(figure=fig, config={"displayModeBar": False}),
        ]
    )


# --- Chat: enviar mensagem e atualizar histórico ---
@app.callback(
    [
        Output(comp.ID_CHAT_HISTORY_STORE, "data"),
        Output(comp.ID_CHAT_MESSAGES, "children"),
        Output(comp.ID_CHAT_INPUT, "value"),
    ],
    [
        Input(comp.ID_CHAT_SEND, "n_clicks"),
        Input(comp.ID_CHAT_INPUT, "n_submit"),
        Input(comp.ID_QUICK_PROMPT_1, "n_clicks"),
        Input(comp.ID_QUICK_PROMPT_2, "n_clicks"),
        Input(comp.ID_QUICK_PROMPT_3, "n_clicks"),
        Input(comp.ID_QUICK_PROMPT_4, "n_clicks"),
        Input(comp.ID_QUICK_PROMPT_5, "n_clicks"),
    ],
    [
        State(comp.ID_CHAT_INPUT, "value"),
        State(comp.ID_CHAT_HISTORY_STORE, "data"),
        State(comp.ID_RESULTADO_STORE, "data"),
        State(comp.ID_CONTRACT_ID_STORE, "data"),
    ],
    prevent_initial_call=True,
)
def on_chat_send(n_clicks, n_submit, qp1, qp2, qp3, qp4, qp5, value, history, contract_result, project_id):
    # Quick prompts
    trig = ctx.trigger_id if hasattr(ctx, "trigger_id") else None
    quick_map = {
        comp.ID_QUICK_PROMPT_1: "Resuma este projeto.",
        comp.ID_QUICK_PROMPT_2: "Quais são os maiores riscos? Liste os 5 principais e justifique.",
        comp.ID_QUICK_PROMPT_3: "Sugira um preço de venda com base no custo, risco e margem recomendada.",
        comp.ID_QUICK_PROMPT_4: "Quais itens e fatores mais impactam a margem? O que devo validar primeiro?",
        comp.ID_QUICK_PROMPT_5: "Esse prazo é agressivo? O que pode dar errado e como mitigar?",
    }
    if trig in quick_map:
        value = quick_map[trig]

    if not value or not (value := (value or "").strip()):
        return no_update, no_update, no_update
    history = list(history or [])
    history.append({"role": "user", "content": value})
    # Persistir conversa (projeto atual se existir no store de contract_id)
    pid = int(project_id) if project_id else None
    add_chat_message(project_id=pid, role="user", mensagem=value)
    reply = get_chat_response(value, history, contract_result)
    history.append({"role": "assistant", "content": reply})
    add_chat_message(project_id=pid, role="assistant", mensagem=reply)
    return history, comp.render_chat_messages(history), ""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
