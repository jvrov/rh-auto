from __future__ import annotations

import base64
import logging
from pathlib import Path

from dash import Dash, Input, Output, State, no_update

from dashboard import components as comp
from app.pdf_parser import extract_text_from_pdf
from app.project_intelligence import analyze_industrial_project
from app.database import create_project, add_uploaded_document, upsert_project_alerts
from domain.normalize import normalize_project


ROOT = Path(__file__).resolve().parent.parent.parent
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
        text = extract_text_from_pdf(tmp)
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        return decoded, text
    except Exception as e:
        logger.exception("Erro extraindo PDF")
        return None, None


def register(app: Dash) -> None:
    @app.callback(
        [Output(comp.ID_PRICING_PANEL, "children"), Output(comp.ID_RISKS_PANEL, "children")],
        Input(comp.ID_RESULTADO_STORE, "data"),
    )
    def update_pricing_and_risks(current_result):
        if not current_result:
            return comp.pricing_panel(None), comp.risks_panel(None)
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
            Output(comp.ID_DASHBOARD_PANEL, "children"),
        ],
        Input(comp.ID_RESULTADO_STORE, "data"),
    )
    def update_project_sections(project):
        if not project:
            return (comp._overview_executive(None),)
        return (comp._overview_executive(project),)

