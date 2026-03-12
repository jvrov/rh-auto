"""Análise de contrato com IA (OpenAI) - estrutura completa."""
import json
import re
from openai import OpenAI

# Chaves do JSON de resposta (nova estrutura)
RESPONSE_KEYS = [
    "multas",
    "retencoes",
    "responsabilidades_contratada",
    "responsabilidades_contratante",
    "clausulas_perigosas",
    "riscos_financeiros",
    "riscos_juridicos",
    "riscos_operacionais",
    "sugestoes_negociacao",
    "score_risco",
    "nivel_risco",
]


def analyze_contract(text: str, api_key: str) -> dict:
    """
    Envia o texto do contrato para a OpenAI e retorna análise estruturada:
    responsabilidades separadas (contratada/contratante), classificação de riscos,
    cláusulas perigosas com trecho e motivo, sugestões e score.
    """
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada.")

    print("[IDI] contract_analyzer: configurando OpenAI...")
    client = OpenAI(api_key=api_key)
    print("[IDI] contract_analyzer: modelo gpt-4o-mini")

    prompt = _build_prompt(text)
    print("[IDI] contract_analyzer: prompt montado, %d caracteres. Chamando API..." % len(prompt))

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip() if response.choices else ""
    print("[IDI] contract_analyzer: resposta recebida, %d caracteres" % len(raw))
    if raw and len(raw) <= 500:
        print("[IDI] contract_analyzer: preview:", raw[:500])
    elif raw:
        print("[IDI] contract_analyzer: preview (200 chars):", raw[:200], "...")
    result = _parse_analysis_response(raw)
    print("[IDI] contract_analyzer: parse concluído.")
    return result


def _system_prompt() -> str:
    return """Você é um analista jurídico especializado em contratos industriais.
Sua resposta deve ser SEMPRE um único objeto JSON válido, com as chaves exatas abaixo.
Para listas de strings, use []. Para cláusulas perigosas, cada item é um objeto com "trecho" e "motivo".

Chaves obrigatórias do JSON:
- "multas": lista de strings (multas identificadas, com valores/percentuais quando houver)
- "retencoes": lista de strings (retenções financeiras, garantias, percentuais, prazos)
- "responsabilidades_contratada": lista de strings (obrigações da CONTRATADA)
- "responsabilidades_contratante": lista de strings (obrigações da CONTRATANTE)
- "clausulas_perigosas": lista de objetos, cada um com "trecho" (citação do contrato) e "motivo" (explicação do risco). Detectar especialmente: responsabilidade ilimitada, rescisão unilateral, retenções >10%%, multas >5%%, penalidades acumulativas
- "riscos_financeiros": lista de strings (ex.: multas elevadas, retenções altas)
- "riscos_juridicos": lista de strings (ex.: responsabilidade ilimitada, rescisão unilateral)
- "riscos_operacionais": lista de strings (ex.: obrigações técnicas críticas, dependência de acesso)
- "sugestoes_negociacao": lista de strings. Gerar com base nos riscos: ex. se responsabilidade ilimitada → sugerir limitar ao valor do contrato; se retenção >10%% → sugerir reduzir para 5%%; se multa >10%% → sugerir renegociar percentual
- "score_risco": número de 0 a 10 (0=baixo, 10=alto)
- "nivel_risco": exatamente "baixo" (0-3), "moderado" (4-6) ou "alto" (7-10)

Responda apenas com o JSON, sem markdown ou texto antes/depois."""


def _build_prompt(text: str) -> str:
    max_chars = 100_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... texto truncado ...]"
    return f"""Analise o contrato abaixo e extraia as informações no formato JSON com todas as chaves obrigatórias.

Contrato:
---
{text}
---

Retorne o objeto JSON completo com: multas, retencoes, responsabilidades_contratada, responsabilidades_contratante, clausulas_perigosas (lista de {{"trecho","motivo"}}), riscos_financeiros, riscos_juridicos, riscos_operacionais, sugestoes_negociacao, score_risco, nivel_risco."""


def _parse_analysis_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        if match:
            raw = match.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("[IDI] contract_analyzer: AVISO - JSON inválido:", e)
        data = {}

    result = {}
    # Listas de strings
    for key in ["multas", "retencoes", "responsabilidades_contratada", "responsabilidades_contratante",
                "riscos_financeiros", "riscos_juridicos", "riscos_operacionais", "sugestoes_negociacao"]:
        val = data.get(key)
        if isinstance(val, list):
            result[key] = [str(x) for x in val]
        else:
            result[key] = []

    # Clausulas perigosas: lista de { trecho, motivo }
    cp = data.get("clausulas_perigosas", [])
    if isinstance(cp, list):
        normalized = []
        for item in cp:
            if isinstance(item, dict):
                normalized.append({
                    "trecho": str(item.get("trecho", "")),
                    "motivo": str(item.get("motivo", "")),
                })
            else:
                normalized.append({"trecho": str(item), "motivo": ""})
        result["clausulas_perigosas"] = normalized
    else:
        result["clausulas_perigosas"] = []

    # Score e nível
    try:
        result["score_risco"] = max(0.0, min(10.0, float(data.get("score_risco", 5.0))))
    except (TypeError, ValueError):
        result["score_risco"] = 5.0
    result["nivel_risco"] = (data.get("nivel_risco") or "moderado").strip().lower()
    if result["nivel_risco"] not in ("baixo", "moderado", "alto"):
        result["nivel_risco"] = "moderado"

    # Compatibilidade: retencoes_financeiras como alias
    result["retencoes_financeiras"] = result.get("retencoes", [])
    return result
