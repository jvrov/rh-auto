"""
Motor de chat com IA (OpenAI).
Permite conversa livre e, se houver contrato carregado, respostas contextualizadas.
"""
import os
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(ROOT))

from openai import OpenAI

logger = logging.getLogger(__name__)


def _build_contract_context(result: dict) -> str:
    """Monta um resumo do contrato para contexto da IA."""
    if not result or not isinstance(result, dict):
        return ""
    riscos = result.get("riscos") or {}
    prec = result.get("precificacao") or {}
    resumo = result.get("resumo_executivo") or {}
    parts = [
        f"Projeto: {result.get('projeto') or result.get('nome_contrato') or 'N/A'}",
        f"Cliente: {result.get('cliente') or 'N/A'}",
        f"Status: {result.get('status_projeto') or 'N/A'}",
        f"Score de risco: {riscos.get('score_geral', result.get('score', 'N/A'))}/10 — Nível: {riscos.get('nivel_risco', result.get('nivel', 'N/A'))}",
        f"Custo estimado: {((result.get('capex') or {}).get('custo_total') or result.get('custo_total_estimado') or 0)}",
        f"Preço recomendado: {prec.get('preco_recomendado') or result.get('preco_sugerido') or 0}",
        f"Resumo executivo: {(resumo.get('texto') if isinstance(resumo, dict) else resumo) or 'N/A'}",
    ]
    for key, label in [
        ("multas", "Multas"),
        ("retencoes", "Retenções financeiras"),
        ("responsabilidades_contratada", "Responsabilidades da contratada"),
        ("responsabilidades_contratante", "Responsabilidades da contratante"),
        ("clausulas_perigosas", "Cláusulas perigosas"),
        ("sugestoes", "Sugestões de negociação"),
        ("alertas_criticos", "Alertas críticos"),
    ]:
        items = result.get(key, [])
        if items:
            if isinstance(items[0], dict):
                texts = [f"- {x.get('texto', x.get('trecho', ''))[:200]} | {x.get('motivo', '')[:150]}" for x in items[:15]]
            else:
                texts = [f"- {str(x)[:200]}" for x in items[:15]]
            parts.append(f"{label}:\n" + "\n".join(texts))
    return "\n\n".join(parts)


def get_chat_response(
    message: str,
    history: list,
    contract_result: dict = None,
    api_key: str = None,
) -> str:
    """
    Envia a mensagem do usuário à IA e retorna a resposta.
    history: lista de {role: "user"|"assistant", content: "..."}
    contract_result: resultado da análise do contrato (opcional); se presente, a IA pode responder sobre o contrato.
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return "Configure OPENAI_API_KEY para usar o chat."

    client = OpenAI(api_key=api_key)
    system = (
        "Você é um assistente especializado em contratos e análise de riscos. "
        "Responda de forma clara e profissional. Se o usuário fizer perguntas sobre um contrato analisado, use o contexto fornecido."
    )
    context = _build_contract_context(contract_result) if contract_result else ""
    if context:
        system += "\n\nContexto do contrato atualmente carregado:\n" + context

    messages = [{"role": "system", "content": system}]
    for h in history[-20:]:  # últimas 20 trocas
        role = h.get("role", "user")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.6,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        logger.exception("Falha ao obter resposta do chat")
        return f"Erro ao obter resposta: {e}"
