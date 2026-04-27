"""
Gráficos Plotly: radar com 5 eixos (Financeiro, Jurídico, Operacional, Penalidades, Equilíbrio).
"""
import plotly.graph_objects as go


def _project_risk_block(result: dict) -> dict:
    """Normaliza a origem dos dados para suportar schema novo e legado."""
    if not isinstance(result, dict):
        return {}
    if "riscos" in result and isinstance(result.get("riscos"), dict):
        return result.get("riscos") or {}
    return result


def _radar_scores_5(result: dict) -> tuple[list[str], list[float]]:
    """Calcula scores 0-10 para os 5 eixos do radar."""
    result = _project_risk_block(result)
    riscos = result.get("riscos") if isinstance(result.get("riscos"), dict) else {}
    analise = result.get("analise_contratual") if isinstance(result.get("analise_contratual"), dict) else {}
    alertas = result.get("alertas_criticos") or []
    documentacao = result.get("ensaios_documentacao") or []
    automacao = (result.get("escopo_tecnico") or {}).get("automacao", []) if isinstance(result.get("escopo_tecnico"), dict) else []

    labels = [
        "Risco Financeiro",
        "Risco Jurídico",
        "Risco Operacional",
        "Risco de Penalidades",
        "Equilíbrio Contratual",
    ]
    # Financeiro, Jurídico, Operacional: usa o schema novo quando disponível,
    # com fallback heurístico para dados legados.
    penalty_alerts = [
        a for a in alertas
        if isinstance(a, dict) and any(k in f"{a.get('titulo', '')} {a.get('mensagem', '')} {a.get('categoria', '')}".lower() for k in ("multa", "retenc", "penal"))
    ]
    scores = [
        float(riscos.get("risco_financeiro", len(result.get("riscos_financeiros", [])) * 2.0 + len(result.get("retencoes", [])) * 0.6) or 0),
        float(riscos.get("risco_contratual", len(result.get("clausulas_perigosas", [])) * 1.8 + len(result.get("multas", [])) * 0.8) or 0),
        float(riscos.get("risco_tecnico", len(documentacao) * 0.6 + len(automacao) * 0.8) or 0),
    ]
    scores = [min(10.0, max(0.0, s)) for s in scores]

    # Penalidades: multas + cláusulas relacionadas a penalidades
    multas = len(result.get("multas", [])) or len(analise.get("multas", []))
    clausulas = result.get("clausulas_perigosas", []) if "clausulas_perigosas" in result else analise.get("clausulas_relevantes", [])
    penal_count = multas + len(penalty_alerts) + sum(
        1 for c in clausulas if isinstance(c, dict) and ("penalidade" in (c.get("motivo") or "").lower() or "multa" in (c.get("motivo") or "").lower())
    )
    scores.append(min(10.0, penal_count * 1.8))

    # Equilíbrio: desequilíbrio entre responsabilidades = risco (0 = equilibrado, 10 = muito desequilibrado)
    score_contract = float(riscos.get("risco_contratual", 0) or 0)
    score_fin = float(riscos.get("risco_financeiro", 0) or 0)
    equilibrio_risk = min(10.0, abs(score_contract - score_fin) + float(riscos.get("risco_margem", 0) or 0) * 0.3)
    scores.append(round(equilibrio_risk, 1))

    return labels, scores


def create_radar_chart(result: dict) -> go.Figure:
    """Gráfico radar com 5 eixos (tema escuro)."""
    labels, scores = _radar_scores_5(result)
    labels_closed = labels + [labels[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=scores_closed,
            theta=labels_closed,
            fill="toself",
            line=dict(color="rgb(56, 189, 248)"),
            fillcolor="rgba(56, 189, 248, 0.25)",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=100, r=100, t=50, b=50),
        font=dict(size=11, color="#e2e8f0"),
    )
    return fig


def create_executive_comparison_summary(project_a: dict, project_b: dict, name1: str, name2: str) -> dict:
    """Resumo comparativo para a tela executiva."""
    def _value(project, *keys, default=0.0):
        cur = project or {}
        for key in keys:
            if isinstance(cur, dict) and key in cur:
                cur = cur.get(key)
            else:
                return default
        try:
            return float(cur or default)
        except (TypeError, ValueError):
            return default

    def _status(project):
        if not isinstance(project, dict):
            return "—"
        return project.get("status_projeto") or project.get("nivel_risco") or "—"

    score_a = _value(project_a, "riscos", "score_geral", default=_value(project_a, "score", default=0))
    score_b = _value(project_b, "riscos", "score_geral", default=_value(project_b, "score", default=0))
    custo_a = _value(project_a, "capex", "custo_total", default=_value(project_a, "custo_total_estimado", default=0))
    custo_b = _value(project_b, "capex", "custo_total", default=_value(project_b, "custo_total_estimado", default=0))
    preco_a = _value(project_a, "precificacao", "preco_recomendado", default=_value(project_a, "preco_sugerido", default=0))
    preco_b = _value(project_b, "precificacao", "preco_recomendado", default=_value(project_b, "preco_sugerido", default=0))
    margem_a = _value(project_a, "precificacao", "margem_sugerida", default=_value(project_a, "margem_sugerida", default=0))
    margem_b = _value(project_b, "precificacao", "margem_sugerida", default=_value(project_b, "margem_sugerida", default=0))

    return {
        "name1": name1,
        "name2": name2,
        "score_a": score_a,
        "score_b": score_b,
        "custo_a": custo_a,
        "custo_b": custo_b,
        "preco_a": preco_a,
        "preco_b": preco_b,
        "margem_a": margem_a,
        "margem_b": margem_b,
        "status_a": _status(project_a),
        "status_b": _status(project_b),
        "leader": name1 if score_a > score_b else name2 if score_b > score_a else "Empate",
        "best_margin": name1 if margem_a > margem_b else name2 if margem_b > margem_a else "Empate",
        "delta_score": round(abs(score_a - score_b), 1),
        "delta_custo": round(abs(custo_a - custo_b), 2),
        "delta_preco": round(abs(preco_a - preco_b), 2),
        "delta_margem": round(abs(margem_a - margem_b), 1),
    }


def create_bar_chart(result: dict) -> go.Figure:
    """Gráfico de barras por categoria (tema escuro)."""
    categorias = [
        "Multas",
        "Retenções",
        "Respons. Contratada",
        "Respons. Contratante",
        "Cláusulas perigosas",
    ]
    valores = [
        len(result.get("multas", [])),
        len(result.get("retencoes", [])),
        len(result.get("responsabilidades_contratada", [])),
        len(result.get("responsabilidades_contratante", [])),
        len(result.get("clausulas_perigosas", [])),
    ]
    fig = go.Figure(
        data=[go.Bar(x=categorias, y=valores, marker_color="rgb(56, 189, 248)")]
    )
    fig.update_layout(
        xaxis_tickangle=-35,
        margin=dict(l=50, r=30, t=30, b=90),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="Quantidade", gridcolor="rgba(255,255,255,0.1)"),
    )
    return fig


def create_radar_comparison(
    result1: dict, result2: dict, name1: str = "Contrato A", name2: str = "Contrato B"
) -> go.Figure:
    """Radar comparativo entre dois contratos (5 eixos)."""
    labels, scores1 = _radar_scores_5(result1)
    _, scores2 = _radar_scores_5(result2)
    labels_closed = labels + [labels[0]]
    scores1_closed = scores1 + [scores1[0]]
    scores2_closed = scores2 + [scores2[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=scores1_closed,
            theta=labels_closed,
            fill="toself",
            name=name1,
            line=dict(color="rgb(56, 189, 248)"),
            fillcolor="rgba(56, 189, 248, 0.2)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=scores2_closed,
            theta=labels_closed,
            fill="toself",
            name=name2,
            line=dict(color="rgb(250, 204, 21)"),
            fillcolor="rgba(250, 204, 21, 0.2)",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.15)"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.15)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=100, r=100, t=50, b=50),
        font=dict(color="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#e2e8f0")),
    )
    return fig
