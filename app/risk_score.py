"""Cálculo do score de risco contratual (0 a 10) com OpenAI."""
from openai import OpenAI


def calculate_risk_score(
    analysis: dict,
    contract_text: str,
    api_key: str,
) -> float:
    """
    Usa a OpenAI para calcular um score de risco de 0 a 10 com base na análise
    e no texto do contrato. Retorna valor entre 0 e 10.
    """
    if not api_key:
        print("[IDI] risk_score: OPENAI_API_KEY não configurada, retornando 5.0")
        return 5.0

    print("[IDI] risk_score: calculando score com OpenAI...")
    client = OpenAI(api_key=api_key)
    multas = analysis.get("multas", [])
    retencoes = analysis.get("retencoes_financeiras", [])
    responsabilidades = analysis.get("responsabilidades", [])
    clausulas = analysis.get("clausulas_perigosas", [])

    prompt = f"""Com base na análise do contrato, calcule um SCORE DE RISCO de 0 a 10.
- 0 = risco muito baixo; 10 = risco muito alto.
Considere:
- Multas encontradas: {len(multas)} itens. {multas[:3] if multas else 'Nenhuma'}
- Retenções financeiras: {len(retencoes)} itens. {retencoes[:3] if retencoes else 'Nenhuma'}
- Responsabilidades: {len(responsabilidades)} itens.
- Cláusulas perigosas: {len(clausulas)} itens. {clausulas[:3] if clausulas else 'Nenhuma'}

Responda com UM ÚNICO NÚMERO entre 0 e 10 (pode ser decimal, ex: 6.5), sem texto adicional."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você retorna apenas um número de 0 a 10."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    raw = (response.choices[0].message.content or "").strip()
    try:
        score = float(raw.replace(",", ".").strip())
    except (ValueError, TypeError):
        score = 5.0
    score = max(0.0, min(10.0, score))
    print("[IDI] risk_score: score = %.1f" % score)
    return score
