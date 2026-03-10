"""Análise de contrato com IA (OpenAI)."""
import json
import re
from openai import OpenAI

# Estrutura esperada da resposta da IA (para parsing)
ANALYSIS_KEYS = [
    "multas",
    "retencoes_financeiras",
    "responsabilidades",
    "clausulas_perigosas",
    "sugestoes_negociacao",
]


def analyze_contract(text: str, api_key: str) -> dict:
    """
    Envia o texto do contrato para a OpenAI e retorna um dicionário
    com multas, retenções, responsabilidades, cláusulas perigosas e sugestões.
    """
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada.")

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(text)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um analista jurídico especializado em contratos industriais. "
                    "Responda SEMPRE em JSON válido, com as chaves exatas: "
                    "multas (lista de strings), retencoes_financeiras (lista), "
                    "responsabilidades (lista), clausulas_perigosas (lista), "
                    "sugestoes_negociacao (lista de strings). "
                    "Use apenas listas; se não houver item, use lista vazia []."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    return _parse_analysis_response(raw)


def _build_prompt(text: str) -> str:
    """Monta o prompt com o texto do contrato (limitado para caber no contexto)."""
    max_chars = 120_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... texto truncado ...]"
    return f"""Analise o contrato abaixo e extraia as informações no formato JSON.

Contrato:
---
{text}
---

Retorne um único objeto JSON com estas chaves:
- "multas": lista de multas identificadas (ex.: multa por atraso, valores, condições)
- "retencoes_financeiras": lista de retenções financeiras (garantias, percentuais, prazos)
- "responsabilidades": lista de obrigações e responsabilidades das partes
- "clausulas_perigosas": lista de cláusulas que representam risco (indenizações ilimitadas, renúncias, etc.)
- "sugestoes_negociacao": lista de sugestões para reduzir risco (ex.: reduzir multa por atraso, limitar responsabilidade técnica, reduzir retenções)

Responda apenas com o JSON, sem markdown ou texto adicional."""


def _parse_analysis_response(raw: str) -> dict:
    """Extrai JSON da resposta e normaliza as chaves."""
    # Tenta extrair bloco JSON se vier dentro de markdown
    raw = raw.strip()
    if raw.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    result = {}
    for key in ANALYSIS_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            result[key] = [str(item) for item in value]
        else:
            result[key] = []
    return result
