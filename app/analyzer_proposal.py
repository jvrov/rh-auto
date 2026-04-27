"""
Analisador de documentos industriais (RFP / escopo / CAPEX / BOM / condições comerciais + minuta).

Retorna JSON estruturado compatível com a interface industrial:
- visão geral, escopo, condições operacionais
- escopo técnico, normas, ensaios/documentação
- condições comerciais e análise contratual
- BOM, CAPEX, precificação, riscos, resumo executivo
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI


SCHEMA = {
    "cliente": "",
    "projeto": "",
    "local_planta": "",
    "objetivo": "",
    "tipo_sistema": "",
    "escopo_solicitado": [],
    "condicoes_operacionais": {
        "fluido": "",
        "temperatura": "",
        "pressao": "",
        "vazao": "",
        "outras": "",
    },
    "escopo_tecnico": {
        "fornecimento": [],
        "equipamentos_principais": [],
        "instrumentacao": [],
        "tubulacao": [],
        "valvulas": [],
        "estrutura": [],
        "skid": [],
        "automacao": [],
        "painel_controle": [],
        "clp": [],
        "comunicacao": [],
        "supervisorio": [],
    },
    "normas_tecnicas": [],
    "ensaios_documentacao": [],
    "condicoes_comerciais": {
        "prazo_entrega": "",
        "forma_pagamento": [],
        "retencao_contratual": "",
        "multa_atraso": "",
        "garantia": "",
        "valor_contrato": "",
    },
    # Campos contratuais serão preenchidos pelo orquestrador (contract_analyzer)
    "analise_contratual": {
        "multas": [],
        "retencoes": [],
        "responsabilidades": [],
        "clausulas_relevantes": [],
        "score_risco": 0,
        "sugestoes_negociacao": [],
    },
    # BOM: lista de itens estruturados
    "bom": [
        # {"item": "", "tag": "", "descricao": "", "quantidade": "", "material": "", "especificacao": "", "custo_unitario": "", "custo_total": ""}
    ],
    "capex": {
        "materiais": 0,
        "engenharia": 0,
        "montagem_mecanica": 0,
        "montagem_eletrica": 0,
        "testes_fat": 0,
        "logistica": 0,
        "documentacao": 0,
        "custo_total": 0,
    },
    # precificacao e riscos serão preenchidos pelo orquestrador (engines)
    "precificacao": {
        "margem_minima_segura": 0,
        "margem_sugerida": 0,
        "preco_minimo": 0,
        "preco_recomendado": 0,
        "ajuste_por_risco": 0,
    },
    "riscos": {
        "score_geral": 0,
        "risco_comercial": 0,
        "risco_financeiro": 0,
        "risco_contratual": 0,
        "risco_tecnico": 0,
        "risco_prazo": 0,
        "risco_margem": 0,
        "motivos": [],
    },
    "resumo_executivo": "",
}


def analyze_project_documents(text: str, api_key: str | None = None) -> dict[str, Any]:
    """
    Analisa texto agregado de documentos do projeto e retorna JSON estruturado.
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não configurada.")

    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(text)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    raw = response.choices[0].message.content.strip() if response.choices else ""
    return _parse_json(raw)


def _system_prompt() -> str:
    return (
        "Você é um analista sênior de projetos industriais e precificação. "
        "Extraia informações técnicas e comerciais de RFPs, escopos, CAPEX e minutas. "
        "Responda SEMPRE com um único JSON válido (sem markdown) e com as chaves exatas do schema. "
        "Quando não houver informação, use string vazia, lista vazia [] ou objeto {}."
    )


def _build_prompt(text: str) -> str:
    max_chars = 120_000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... texto truncado ...]"
    return (
        "Analise os documentos do projeto abaixo e retorne o JSON estruturado.\n\n"
        "Regras:\n"
        "- Retorne SOMENTE o JSON (sem markdown).\n"
        "- BOM: se encontrar uma lista de materiais, preencha 'bom' como lista de objetos.\n"
        "- CAPEX: se encontrar valores, preencha os campos numéricos (use número, sem 'R$').\n"
        "- Se não houver informação, use vazio.\n\n"
        "Schema:\n"
        f"{json.dumps(SCHEMA, ensure_ascii=False, indent=2)}\n\n"
        "Documentos (texto agregado):\n---\n"
        f"{text}\n---\n"
    )


def _parse_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        m = re.search(r"```(?:json)?\\s*([\\s\\S]*?)```", raw)
        if m:
            raw = m.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    # Normalização defensiva para o novo schema
    result = json.loads(json.dumps(SCHEMA))  # deep copy simples

    def _as_str(x) -> str:
        return str(x) if x is not None else ""

    def _as_list(x) -> list:
        return [str(i) for i in x] if isinstance(x, list) else []

    if isinstance(data, dict):
        for k in ("cliente", "projeto", "local_planta", "objetivo", "tipo_sistema", "resumo_executivo"):
            result[k] = _as_str(data.get(k))

        result["escopo_solicitado"] = _as_list(data.get("escopo_solicitado"))
        result["normas_tecnicas"] = _as_list(data.get("normas_tecnicas"))
        result["ensaios_documentacao"] = _as_list(data.get("ensaios_documentacao"))

        co = data.get("condicoes_operacionais")
        if isinstance(co, dict):
            for kk in ("fluido", "temperatura", "pressao", "vazao", "outras"):
                result["condicoes_operacionais"][kk] = _as_str(co.get(kk))

        et = data.get("escopo_tecnico")
        if isinstance(et, dict):
            for kk in result["escopo_tecnico"].keys():
                result["escopo_tecnico"][kk] = _as_list(et.get(kk))

        cc = data.get("condicoes_comerciais")
        if isinstance(cc, dict):
            result["condicoes_comerciais"]["prazo_entrega"] = _as_str(cc.get("prazo_entrega"))
            result["condicoes_comerciais"]["forma_pagamento"] = _as_list(cc.get("forma_pagamento"))
            for kk in ("retencao_contratual", "multa_atraso", "garantia", "valor_contrato"):
                result["condicoes_comerciais"][kk] = _as_str(cc.get(kk))

        # BOM: lista de dicts (normaliza chaves)
        bom = data.get("bom")
        if isinstance(bom, list):
            norm = []
            for it in bom:
                if isinstance(it, dict):
                    norm.append({
                        "item": _as_str(it.get("item")),
                        "tag": _as_str(it.get("tag")),
                        "descricao": _as_str(it.get("descricao")),
                        "quantidade": _as_str(it.get("quantidade")),
                        "material": _as_str(it.get("material")),
                        "especificacao": _as_str(it.get("especificacao")),
                        "custo_unitario": _as_str(it.get("custo_unitario")),
                        "custo_total": _as_str(it.get("custo_total")),
                    })
                else:
                    norm.append({"item": _as_str(it), "tag": "", "descricao": "", "quantidade": "", "material": "", "especificacao": "", "custo_unitario": "", "custo_total": ""})
            result["bom"] = norm

        capex = data.get("capex")
        if isinstance(capex, dict):
            for kk in result["capex"].keys():
                try:
                    result["capex"][kk] = float(capex.get(kk, 0) or 0)
                except (TypeError, ValueError):
                    result["capex"][kk] = 0

    return result

