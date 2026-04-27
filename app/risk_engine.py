"""
Motor de risco híbrido: combina regras objetivas com score da IA.
Escala: 0-3 baixo, 4-6 moderado, 7-10 alto.
"""
from app.hybrid_risk_score import (
    compute_hybrid_score,
    get_nivel_risco,
    combine_scores,
)

__all__ = ["compute_hybrid_score", "get_nivel_risco", "combine_scores"]
