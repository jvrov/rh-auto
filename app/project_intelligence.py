"""
Orquestrador de análise industrial:
- extrai estrutura do projeto (RFP/escopo/BOM/CAPEX) via analyzer_proposal
- extrai análise contratual via contract_analyzer (quando existir minuta no mesmo PDF)
- calcula precificação e riscos (engines)
"""

from __future__ import annotations

import os
from typing import Any

from app.analyzer_proposal import analyze_project_documents
from app.contract_analyzer import analyze_contract
from app.pricing_engine import estimate_cost_total, simulate_pricing
from app.risk_engine_v2 import compute_project_risks
from domain.normalize import normalize_project
from engines.alerts_engine import generate_critical_alerts, suggest_status


def analyze_industrial_project(text: str, *, filename: str = "") -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada.")

    # 1) Estrutura do projeto (industrial)
    project = analyze_project_documents(text, api_key=api_key)

    # 2) Análise contratual (se houver minuta / cláusulas comerciais no PDF)
    contract_raw = analyze_contract(text, api_key=api_key)
    analise_contratual = {
        "multas": contract_raw.get("multas", []),
        "retencoes": contract_raw.get("retencoes", []) or contract_raw.get("retencoes_financeiras", []),
        "responsabilidades": (
            (contract_raw.get("responsabilidades_contratada", []) or [])
            + (contract_raw.get("responsabilidades_contratante", []) or [])
        ),
        "clausulas_relevantes": [
            {"trecho": c.get("trecho", ""), "motivo": c.get("motivo", "")}
            for c in (contract_raw.get("clausulas_perigosas", []) or [])
            if isinstance(c, dict)
        ],
        "score_risco": float(contract_raw.get("score_risco", 0) or 0),
        "sugestoes_negociacao": contract_raw.get("sugestoes_negociacao", []),
    }
    project["analise_contratual"] = analise_contratual

    # 3) CAPEX/custo total: usar capex.custo_total se vier, senão estimar pelo texto
    custo_total = float(project.get("capex", {}).get("custo_total", 0) or 0)
    if custo_total <= 0:
        custo_total = estimate_cost_total({"capex_estimado": {"total": 0}}, raw_text=text)
        project["capex"]["custo_total"] = custo_total

    # 4) Precificação
    pricing = simulate_pricing(custo_total=custo_total, margem_minima_segura=18.0, margem_alvo=25.0)
    project["precificacao"] = {
        "margem_minima_segura": pricing.margem_minima_segura,
        "margem_sugerida": pricing.margem_alvo,
        "preco_minimo": round(pricing.preco_minimo, 2),
        "preco_recomendado": round(pricing.preco_recomendado, 2),
        "ajuste_por_risco": 0,
    }

    # 5) Riscos (industrial)
    # Adaptar para o schema do risk_engine_v2
    rs = compute_project_risks(
        {
            "documentacao_exigida": project.get("ensaios_documentacao", []) or [],
            "normas_tecnicas": project.get("normas_tecnicas", []) or [],
            "lista_materiais": project.get("bom", []) or [],
            "automacao": (project.get("escopo_tecnico", {}) or {}).get("automacao", []) or [],
            "condicoes_pagamento": (project.get("condicoes_comerciais", {}) or {}).get("forma_pagamento", []) or [],
            "retencao_contratual": (project.get("condicoes_comerciais", {}) or {}).get("retencao_contratual", ""),
            "multa_atraso": (project.get("condicoes_comerciais", {}) or {}).get("multa_atraso", ""),
            "prazo_entrega": (project.get("condicoes_comerciais", {}) or {}).get("prazo_entrega", ""),
        },
        raw_text=text,
    )
    project["riscos"] = {
        "score_geral": rs.score_geral,
        "risco_comercial": rs.risco_comercial,
        "risco_financeiro": rs.risco_financeiro,
        "risco_contratual": rs.risco_contratual,
        "risco_tecnico": rs.risco_tecnico,
        "risco_prazo": rs.risco_prazo,
        "risco_margem": rs.risco_margem,
        "motivos": rs.motivos,
    }

    # Metadados úteis
    if filename and not project.get("projeto"):
        project["projeto"] = filename

    # Normaliza para schema canônico (fallbacks, tipos e chaves)
    project_n = normalize_project(project)

    # Alertas críticos e status sugerido (determinístico)
    project_n["alertas_criticos"] = generate_critical_alerts(project_n, raw_text=text)
    # Só preenche se estiver no default/novo (híbrido: usuário pode sobrescrever depois)
    if not str(project_n.get("status_projeto") or "").strip() or project_n.get("status_projeto") == "novo":
        project_n["status_projeto"] = suggest_status(project_n)

    # Resumo executivo estruturado mínimo (determinístico) se vier vazio
    re_ = project_n.get("resumo_executivo") or {}
    if isinstance(re_, dict) and not (re_.get("texto") or "").strip():
        riscos = project_n.get("riscos") or {}
        prec = project_n.get("precificacao") or {}
        project_n["resumo_executivo"]["texto"] = (
            f"Projeto: {project_n.get('projeto') or 'não identificado'}\n"
            f"Cliente: {project_n.get('cliente') or 'não identificado'}\n"
            f"Risco geral: {float(riscos.get('score_geral', 0) or 0):.1f}/10\n"
            f"Custo estimado: {float((project_n.get('capex') or {}).get('custo_total', 0) or 0):.2f}\n"
            f"Preço recomendado: {float(prec.get('preco_recomendado', 0) or 0):.2f}\n"
        )
        project_n["resumo_executivo"]["recomendacao"] = "Revisar alertas críticos e validar premissas antes de fechar proposta."

    return project_n

