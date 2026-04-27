from __future__ import annotations

from dash import Dash, Input, Output, html, dcc, no_update
import dash_bootstrap_components as dbc

from dashboard import components as comp
from app.database import list_projects, get_project, list_chat_history
from dashboard.charts import create_radar_comparison, create_executive_comparison_summary


def _history_options():
    return [
        {
            "label": f"{(p.get('nome_projeto') or 'Projeto')} — Score {p.get('score_risco', '-') } ({(p.get('data_analise') or '')[:10]})",
            "value": p["id"],
        }
        for p in list_projects()
    ]


def register(app: Dash) -> None:
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

    @app.callback(
        Output(comp.ID_COMPARE_CONTAINER, "children"),
        [Input(comp.ID_COMPARE_A, "value"), Input(comp.ID_COMPARE_B, "value")],
    )
    def on_compare(ida, idb):
        if not ida or not idb or ida == idb:
            return html.Div(
                "Selecione dois projetos diferentes para comparar.",
                className="empty-muted",
            )
        c1 = get_project(int(ida))
        c2 = get_project(int(idb))
        if not c1 or not c2:
            return html.Div("Não foi possível carregar os projetos selecionados.", className="empty-muted")

        p1 = c1.get("resumo") or {}
        p2 = c2.get("resumo") or {}
        name1 = c1.get("nome_projeto") or "Projeto A"
        name2 = c2.get("nome_projeto") or "Projeto B"
        summary = create_executive_comparison_summary(p1, p2, name1, name2)
        fig = create_radar_comparison(p1, p2, name1, name2)

        def _card(title, a, b, tone="default"):
            cls = "metric-border-primary" if tone == "primary" else "metric-border-warning" if tone == "warning" else "metric-border-neutral"
            return html.Div(
                [
                    html.Div(title, className="metric-label"),
                    html.Div(
                        [
                            html.Div(name1, className="small", style={"color": comp.TEXT_SECONDARY}),
                            html.Div(a, className="metric-value", style={"fontSize": "1rem"}),
                            html.Div(name2, className="small", style={"color": comp.TEXT_SECONDARY, "marginTop": "8px"}),
                            html.Div(b, className="metric-value", style={"fontSize": "1rem"}),
                        ]
                    ),
                ],
                className=f"metric-card {cls}",
            )

        score_a = float(summary["score_a"] or 0)
        score_b = float(summary["score_b"] or 0)
        top_tone = "warning" if score_a > score_b else "primary"
        best_score = name1 if score_a < score_b else name2 if score_b < score_a else "Empate"

        return html.Div(
            [
                html.Div("Comparação executiva", className="section-heading", style={"marginBottom": "10px"}),
                dbc.Row(
                    [
                        dbc.Col(_card("Score de risco", f"{score_a:.1f}/10", f"{score_b:.1f}/10", tone=top_tone), md=6, xs=12),
                        dbc.Col(_card("Margem sugerida", f"{summary['margem_a']:.1f}%", f"{summary['margem_b']:.1f}%", tone="primary"), md=6, xs=12),
                        dbc.Col(_card("Custo estimado", f"{summary['custo_a']:,.2f}", f"{summary['custo_b']:,.2f}", tone="default"), md=6, xs=12),
                        dbc.Col(_card("Preço sugerido", f"{summary['preco_a']:,.2f}", f"{summary['preco_b']:,.2f}", tone="default"), md=6, xs=12),
                    ],
                    className="g-2 mb-3",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("Radar comparativo", className="section-heading", style={"marginBottom": "8px"}),
                                dcc.Graph(figure=fig, config={"displayModeBar": False}),
                            ],
                            className="industrial-card",
                        ),
                        html.Div(
                            [
                                html.Div("Principais diferenças", className="section-heading", style={"marginBottom": "8px"}),
                                html.Ul(
                                    [
                                        html.Li(f"Maior risco geral: {summary['leader']}"),
                                        html.Li(f"Melhor margem: {summary['best_margin']}"),
                                        html.Li(f"Δ Score: {summary['delta_score']:.1f}"),
                                        html.Li(f"Δ Custo: {summary['delta_custo']:,.2f}"),
                                        html.Li(f"Δ Preço: {summary['delta_preco']:,.2f}"),
                                    ],
                                    className="list-clean",
                                ),
                                html.Div(
                                    f"Conclusão: {best_score} tende a ser o projeto mais eficiente em margem/risco.",
                                    className="summary-rec",
                                ),
                            ],
                            className="industrial-card",
                        ),
                    ],
                    className="grid-2",
                ),
            ]
        )

