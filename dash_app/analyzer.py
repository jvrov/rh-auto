"""
Analisador de risco contratual com IA.
Chama a análise do projeto principal e devolve o dicionário no formato do dashboard:
nome_contrato, score, nivel, multas, retencoes, responsabilidades_*, riscos_*, clausulas_perigosas, sugestoes.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.contract_analyzer import analyze_contract
from app.hybrid_risk_score import compute_hybrid_score, get_nivel_risco, combine_scores


def analyze_contract_for_dashboard(text: str, nome_contrato: str = "", api_key: str = None) -> dict:
    """
    Executa análise do contrato e retorna dicionário no formato do dashboard.
    api_key: se None, usa os.environ["OPENAI_API_KEY"].
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada. Defina a variável de ambiente.")

    raw = analyze_contract(text, api_key)
    score_ia = raw.get("score_risco", 5.0)
    score_hibrido = compute_hybrid_score(raw)
    score_final = combine_scores(score_ia, score_hibrido)
    nivel = get_nivel_risco(score_final)

    # Normalizar cláusulas: trecho -> texto (formato esperado pelo dashboard)
    clausulas = raw.get("clausulas_perigosas", [])
    clausulas_norm = []
    for c in clausulas:
        if isinstance(c, dict):
            clausulas_norm.append({
                "texto": c.get("trecho", c.get("texto", "")),
                "motivo": c.get("motivo", ""),
            })
        else:
            clausulas_norm.append({"texto": str(c), "motivo": ""})

    return {
        "nome_contrato": nome_contrato or "Contrato",
        "score": round(score_final, 1),
        "nivel": nivel,
        "multas": raw.get("multas", []),
        "retencoes": raw.get("retencoes", []) or raw.get("retencoes_financeiras", []),
        "responsabilidades_contratada": raw.get("responsabilidades_contratada", []),
        "responsabilidades_contratante": raw.get("responsabilidades_contratante", []),
        "riscos_financeiros": raw.get("riscos_financeiros", []),
        "riscos_juridicos": raw.get("riscos_juridicos", []),
        "riscos_operacionais": raw.get("riscos_operacionais", []),
        "clausulas_perigosas": clausulas_norm,
        "sugestoes": raw.get("sugestoes_negociacao", []),
    }
