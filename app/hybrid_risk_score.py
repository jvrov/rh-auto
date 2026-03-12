"""
Score de risco híbrido: combina regras objetivas com o score da IA.
Fatores que aumentam o risco: multas >5%, retenções >10%, responsabilidade ilimitada,
rescisão unilateral, penalidades acumulativas.
Escala: 0-3 baixo, 4-6 moderado, 7-10 alto.
"""
import re


# Padrões que indicam risco (case insensitive)
PATTERNS_ALTO_RISCO = [
    (r"responsabilidade\s+(n[aã]o\s+)?(estar\s+)?limitada|ilimitada|ilimitado", 2.0),
    (r"rescis[aã]o\s+unilateral|rescindir\s+unilateralmente", 1.5),
    (r"penalidade(s)?\s+acumulativa(s)?|multas?\s+acumulativa(s)?", 1.0),
    (r"reten[cç][aã]o\s+integral|reten[cç][aã]o\s+dos\s+valores", 1.0),
]


def _max_percentage_in_texts(texts):
    """Dado uma lista de strings, retorna o maior percentual encontrado (0 se nenhum)."""
    if not texts:
        return 0.0
    combined = " ".join(str(t) for t in texts)
    found = re.findall(r"(\d+)\s*%|(\d+)\s*(?:por\s+cento|percento)", combined, re.I)
    if not found:
        return 0.0
    return max(float(a or b) for a, b in found)


def compute_hybrid_score(analysis: dict) -> float:
    """
    Calcula um score de 0 a 10 com base em regras objetivas sobre a análise.
    - Multas com percentual > 5%: +1.5
    - Retenções > 10%: +1.5
    - Responsabilidade ilimitada (texto): +2
    - Rescisão unilateral: +1.5
    - Penalidades acumulativas: +1
    Depois normaliza para 0-10 (cap nos pontos somados).
    """
    points = 0.0
    texts_to_scan = []

    multas = analysis.get("multas", [])
    retencoes = analysis.get("retencoes", []) or analysis.get("retencoes_financeiras", [])

    # Multas > 5%
    pct_multa = _max_percentage_in_texts(multas)
    if pct_multa > 5:
        points += 1.5
    texts_to_scan.extend(multas)

    # Retenções > 10%
    pct_ret = _max_percentage_in_texts(retencoes)
    if pct_ret > 10:
        points += 1.5
    texts_to_scan.extend(retencoes)

    # Cláusulas perigosas (trecho + motivo)
    clausulas = analysis.get("clausulas_perigosas", [])
    for item in clausulas:
        if isinstance(item, dict):
            texts_to_scan.append(item.get("trecho", "") + " " + item.get("motivo", ""))
        else:
            texts_to_scan.append(str(item))

    # Riscos jurídicos/financeiros (texto)
    for key in ["riscos_financeiros", "riscos_juridicos", "riscos_operacionais"]:
        texts_to_scan.extend(analysis.get(key, []))

    combined = " ".join(str(t) for t in texts_to_scan).lower()

    for pattern, add in PATTERNS_ALTO_RISCO:
        if re.search(pattern, combined, re.I):
            points += add
            break  # cada padrão só conta uma vez

    # Converter pontos (máximo ~8) para escala 0-10
    score = min(10.0, points * 1.4)  # 8*1.4 = 11.2 -> cap 10
    print("[IDI] hybrid_risk_score: pontos=%.1f -> score=%.1f" % (points, score))
    return round(score, 1)


def get_nivel_risco(score: float) -> str:
    """Retorna 'baixo', 'moderado' ou 'alto' conforme a escala 0-3, 4-6, 7-10."""
    if score <= 3:
        return "baixo"
    if score <= 6:
        return "moderado"
    return "alto"


def combine_scores(score_ia: float, score_hibrido: float, peso_ia: float = 0.5) -> float:
    """Combina score da IA e score híbrido. Default: média simples (0.5 cada)."""
    final = peso_ia * score_ia + (1 - peso_ia) * score_hibrido
    return max(0.0, min(10.0, round(final, 1)))
