from __future__ import annotations

import copy
from typing import Any, Literal, TypedDict


ProjectStatus = Literal["novo", "em_analise", "precificado", "em_revisao", "concluido"]


class CriticalAlert(TypedDict, total=False):
    id: str
    severidade: Literal["info", "atencao", "critico"]
    categoria: str
    titulo: str
    mensagem: str
    evidencia: str
    acao_sugerida: str
    origem: Literal["regras", "ia", "usuario"]


# Schema canônico do produto (industrial + contrato + decisão executiva)
CANONICAL_SCHEMA: dict[str, Any] = {
    # Identidade / metadados do projeto
    "cliente": "",
    "projeto": "",
    "local_planta": "",
    "objetivo": "",
    "tipo_sistema": "",
    "status_projeto": "novo",
    "prazo_estimado": "",  # ex.: "14 semanas" / "120 dias"
    # Seções base
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
    "analise_contratual": {
        "multas": [],
        "retencoes": [],
        "responsabilidades": [],
        "clausulas_relevantes": [],  # lista de dicts: {"trecho","motivo"}
        "score_risco": 0,
        "sugestoes_negociacao": [],
    },
    # BOM/CAPEX
    "bom": [],
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
    # Decisão: precificação, riscos, resumo, alertas
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
    "resumo_executivo": {
        "texto": "",
        "recomendacao": "",
        "principais_pontos": [],
    },
    "alertas_criticos": [],
    # Qualidade/faltantes para UI (evitar blocos vazios)
    "data_quality": {
        "faltantes": [],
        "pendencias": [],
    },
}


def new_project() -> dict[str, Any]:
    """Cria uma instância nova (deep copy) do schema canônico."""
    return copy.deepcopy(CANONICAL_SCHEMA)

