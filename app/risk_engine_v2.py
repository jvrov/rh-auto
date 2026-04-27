"""
Riscos para projetos industriais (além do jurídico):
- comercial, financeiro, contratual, técnico, prazo, margem

Versão inicial: heurísticas baseadas no JSON do projeto + algumas regras de texto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RiskScores:
    score_geral: float
    nivel_risco: str
    risco_comercial: float
    risco_financeiro: float
    risco_contratual: float
    risco_tecnico: float
    risco_prazo: float
    risco_margem: float
    motivos: list[str]


def _nivel(score: float) -> str:
    if score <= 3:
        return "baixo"
    if score <= 6:
        return "moderado"
    return "alto"


def _count_list(d: dict[str, Any], key: str) -> int:
    v = d.get(key)
    return len(v) if isinstance(v, list) else 0


def compute_project_risks(project_summary: dict[str, Any], raw_text: str = "") -> RiskScores:
    motivos: list[str] = []

    # Heurísticas por módulo
    doc_extensa = _count_list(project_summary, "documentacao_exigida")
    normas = _count_list(project_summary, "normas_tecnicas")
    bom = _count_list(project_summary, "lista_materiais")
    automacao = _count_list(project_summary, "automacao")
    fat = 1 if re.search(r"\\bFAT\\b|factory acceptance test|ensaio", raw_text, re.I) else 0

    # Comercial/contratual
    ret = str(project_summary.get("retencao_contratual", "") or "")
    multa = str(project_summary.get("multa_atraso", "") or "")
    pagamento = _count_list(project_summary, "condicoes_pagamento")

    risco_contratual = min(10.0, 1.5 * (1 if ret else 0) + 2.0 * (1 if multa else 0) + 0.5 * pagamento)
    if ret:
        motivos.append("Retenção contratual identificada.")
    if multa:
        motivos.append("Multa por atraso identificada.")

    risco_comercial = min(10.0, 0.8 * pagamento + 1.2 * (1 if "reajuste" in raw_text.lower() else 0))

    # Financeiro/margem
    risco_financeiro = min(10.0, 0.8 * (1 if ret else 0) + 0.8 * (1 if multa else 0) + 0.15 * bom)
    risco_margem = min(10.0, 0.25 * bom + 1.0 * (1 if ret else 0) + 1.0 * (1 if multa else 0))

    # Técnico
    risco_tecnico = min(10.0, 0.2 * bom + 0.6 * automacao + 0.6 * doc_extensa + 1.2 * fat)
    if automacao:
        motivos.append("Integração/automação presente no escopo.")
    if fat:
        motivos.append("Ensaios/FAT parecem ser exigidos.")

    # Prazo
    prazo = str(project_summary.get("prazo_entrega", "") or "")
    risco_prazo = 3.0
    if prazo:
        # Tenta achar semanas/dias
        m = re.search(r"(\\d{1,3})\\s*(semanas|semana|weeks|week)", prazo, re.I)
        if m:
            w = int(m.group(1))
            if w <= 14:
                risco_prazo = 7.0
                motivos.append("Prazo parece agressivo (≤14 semanas).")
            elif w <= 20:
                risco_prazo = 5.5
        else:
            # Sem parse: risco médio
            risco_prazo = 5.0
    risco_prazo = min(10.0, risco_prazo + 0.05 * doc_extensa + 0.03 * bom)

    # Score geral: média ponderada
    score_geral = (
        0.18 * risco_financeiro
        + 0.18 * risco_tecnico
        + 0.18 * risco_contratual
        + 0.16 * risco_prazo
        + 0.16 * risco_margem
        + 0.14 * risco_comercial
    )
    score_geral = round(min(10.0, max(0.0, score_geral)), 1)

    return RiskScores(
        score_geral=score_geral,
        nivel_risco=_nivel(score_geral),
        risco_comercial=round(risco_comercial, 1),
        risco_financeiro=round(risco_financeiro, 1),
        risco_contratual=round(risco_contratual, 1),
        risco_tecnico=round(risco_tecnico, 1),
        risco_prazo=round(risco_prazo, 1),
        risco_margem=round(risco_margem, 1),
        motivos=motivos[:20],
    )

