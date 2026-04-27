"""
Precificação e simulação de cenários.

Primeira versão: cálculo simples a partir de um custo total estimado (se existir)
e/ou heurísticas do texto. O objetivo é ter uma base modular para evoluir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PricingResult:
    custo_total_estimado: float
    margem_minima_segura: float  # %
    margem_alvo: float  # %
    preco_minimo: float
    preco_recomendado: float
    faixa_preco: tuple[float, float]


def _extract_currency_values(text: str) -> list[float]:
    """
    Extrai valores monetários do texto (heurístico).
    Suporta 'R$ 297.000', '297.000,00', '297000'.
    """
    if not text:
        return []
    # Normaliza separadores comuns
    candidates = re.findall(r"(?:R\\$\\s*)?(\\d{1,3}(?:[\\.,]\\d{3})*(?:[\\.,]\\d{2})?|\\d+)", text)
    values: list[float] = []
    for c in candidates:
        s = c.strip()
        # Tentar BR: 297.000,00
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            # Se só vírgula, assume decimal
            if "," in s:
                s = s.replace(".", "").replace(",", ".")
            else:
                s = s.replace(",", "")
        try:
            v = float(s)
            if v > 1000:  # ignora valores pequenos não monetários
                values.append(v)
        except ValueError:
            continue
    return values


def estimate_cost_total(project_summary: dict[str, Any], raw_text: str = "") -> float:
    """
    Estima custo total. Preferência:
      1) capex_estimado.total (se vier no JSON)
      2) maior valor monetário encontrado no texto
      3) fallback: 0.0
    """
    capex = project_summary.get("capex_estimado") if isinstance(project_summary, dict) else None
    if isinstance(capex, dict):
        for k in ("total", "capex_total", "valor_total", "estimativa_total"):
            v = capex.get(k)
            try:
                if v is not None:
                    return float(v)
            except (TypeError, ValueError):
                pass
    values = _extract_currency_values(raw_text)
    return float(max(values)) if values else 0.0


def simulate_pricing(
    custo_total: float,
    margem_minima_segura: float = 18.0,
    margem_alvo: float = 25.0,
) -> PricingResult:
    """
    Cálculo simples de preço:
      preço = custo * (1 + margem/100)
    """
    custo_total = max(0.0, float(custo_total))
    min_m = float(margem_minima_segura)
    alvo = float(margem_alvo)
    preco_min = custo_total * (1.0 + min_m / 100.0)
    preco_rec = custo_total * (1.0 + alvo / 100.0)
    faixa = (preco_min, preco_rec)
    return PricingResult(
        custo_total_estimado=custo_total,
        margem_minima_segura=min_m,
        margem_alvo=alvo,
        preco_minimo=preco_min,
        preco_recomendado=preco_rec,
        faixa_preco=faixa,
    )

