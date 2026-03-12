"""
Gráficos Plotly para o dashboard: radar de risco, barras por categoria, radar comparativo.
"""
import plotly.graph_objects as go
import plotly.express as px


def _scores_radar_from_result(r: dict):
    """Deriva scores 0-10 para Financeiro, Jurídico, Operacional a partir das listas de riscos."""
    labels = ["Financeiro", "Jurídico", "Operacional"]
    counts = [
        len(r.get("riscos_financeiros", [])),
        len(r.get("riscos_juridicos", [])),
        len(r.get("riscos_operacionais", [])),
    ]
    # Escala: 0 itens = 0, 4+ itens = 10
    scores = [min(10.0, c * 2.5) for c in counts]
    return labels, scores


def create_radar_chart(result: dict) -> go.Figure:
    """Gráfico radar com eixos Financeiro, Jurídico, Operacional (0-10)."""
    labels, scores = _scores_radar_from_result(result)
    # Fechar o polígono
    labels_closed = labels + [labels[0]]
    scores_closed = scores + [scores[0]]
    fig = go.Figure(
        data=go.Scatterpolar(
            r=scores_closed,
            theta=labels_closed,
            fill="toself",
            line=dict(color="rgb(14, 165, 233)"),
            fillcolor="rgba(14, 165, 233, 0.3)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
    )
    return fig


def create_bar_chart(result: dict) -> go.Figure:
    """Gráfico de barras: quantidade por categoria (Multas, Retenções, Responsabilidades, Cláusulas)."""
    categorias = ["Multas", "Retenções", "Respons. Contratada", "Respons. Contratante", "Cláusulas perigosas"]
    valores = [
        len(result.get("multas", [])),
        len(result.get("retencoes", [])),
        len(result.get("responsabilidades_contratada", [])),
        len(result.get("responsabilidades_contratante", [])),
        len(result.get("clausulas_perigosas", [])),
    ]
    fig = go.Figure(
        data=[go.Bar(x=categorias, y=valores, marker_color="rgb(14, 165, 233)")]
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        margin=dict(l=60, r=40, t=40, b=100),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Quantidade",
    )
    return fig


def create_radar_comparison(result1: dict, result2: dict, name1: str = "Contrato 1", name2: str = "Contrato 2") -> go.Figure:
    """Radar comparativo entre dois contratos."""
    labels, scores1 = _scores_radar_from_result(result1)
    _, scores2 = _scores_radar_from_result(result2)
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
            line=dict(color="rgb(14, 165, 233)"),
            fillcolor="rgba(14, 165, 233, 0.25)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=scores2_closed,
            theta=labels_closed,
            fill="toself",
            name=name2,
            line=dict(color="rgb(234, 179, 8)"),
            fillcolor="rgba(234, 179, 8, 0.25)",
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig
