from __future__ import annotations

from typing import Any

from domain.schema import new_project


DEFAULT_NOT_FOUND = "não identificado"


def _as_str(x: Any) -> str:
    if x is None:
        return ""
    return str(x)


def _as_list_str(x: Any) -> list[str]:
    if isinstance(x, list):
        out: list[str] = []
        for i in x:
            s = _as_str(i).strip()
            if s:
                out.append(s)
        return out
    return []


def normalize_project(data: Any) -> dict[str, Any]:
    """
    Normaliza qualquer dict parcial para o schema canônico.
    - Garante chaves
    - Garante tipos
    - Preenche vazios com valores padrão (strings vazias/listas vazias/números 0)
    """
    result = new_project()
    if not isinstance(data, dict):
        return result

    # Identidade / meta
    for k in ("cliente", "projeto", "local_planta", "objetivo", "tipo_sistema", "prazo_estimado"):
        if k in data:
            result[k] = _as_str(data.get(k)).strip()
    if "status_projeto" in data and _as_str(data.get("status_projeto")).strip():
        result["status_projeto"] = _as_str(data.get("status_projeto")).strip()

    # Seções listas
    for k in ("escopo_solicitado", "normas_tecnicas", "ensaios_documentacao"):
        if k in data:
            result[k] = _as_list_str(data.get(k))

    # Objetos
    co = data.get("condicoes_operacionais")
    if isinstance(co, dict):
        for kk in result["condicoes_operacionais"].keys():
            result["condicoes_operacionais"][kk] = _as_str(co.get(kk)).strip()

    et = data.get("escopo_tecnico")
    if isinstance(et, dict):
        for kk in result["escopo_tecnico"].keys():
            result["escopo_tecnico"][kk] = _as_list_str(et.get(kk))

    cc = data.get("condicoes_comerciais")
    if isinstance(cc, dict):
        result["condicoes_comerciais"]["prazo_entrega"] = _as_str(cc.get("prazo_entrega")).strip()
        result["condicoes_comerciais"]["forma_pagamento"] = _as_list_str(cc.get("forma_pagamento"))
        for kk in ("retencao_contratual", "multa_atraso", "garantia", "valor_contrato"):
            result["condicoes_comerciais"][kk] = _as_str(cc.get(kk)).strip()

    ac = data.get("analise_contratual")
    if isinstance(ac, dict):
        result["analise_contratual"]["multas"] = _as_list_str(ac.get("multas"))
        result["analise_contratual"]["retencoes"] = _as_list_str(ac.get("retencoes"))
        result["analise_contratual"]["responsabilidades"] = _as_list_str(ac.get("responsabilidades"))
        # cláusulas relevantes (dicts)
        cr = ac.get("clausulas_relevantes")
        if isinstance(cr, list):
            norm_cr = []
            for c in cr:
                if isinstance(c, dict):
                    norm_cr.append({"trecho": _as_str(c.get("trecho")).strip(), "motivo": _as_str(c.get("motivo")).strip()})
                else:
                    s = _as_str(c).strip()
                    if s:
                        norm_cr.append({"trecho": s, "motivo": ""})
            result["analise_contratual"]["clausulas_relevantes"] = norm_cr
        try:
            result["analise_contratual"]["score_risco"] = float(ac.get("score_risco", 0) or 0)
        except (TypeError, ValueError):
            result["analise_contratual"]["score_risco"] = 0
        result["analise_contratual"]["sugestoes_negociacao"] = _as_list_str(ac.get("sugestoes_negociacao"))

    # BOM
    bom = data.get("bom")
    if isinstance(bom, list):
        norm = []
        for it in bom:
            if isinstance(it, dict):
                norm.append(
                    {
                        "item": _as_str(it.get("item")).strip(),
                        "tag": _as_str(it.get("tag")).strip(),
                        "descricao": _as_str(it.get("descricao")).strip(),
                        "quantidade": _as_str(it.get("quantidade")).strip(),
                        "material": _as_str(it.get("material")).strip(),
                        "especificacao": _as_str(it.get("especificacao")).strip(),
                        "custo_unitario": _as_str(it.get("custo_unitario")).strip(),
                        "custo_total": _as_str(it.get("custo_total")).strip(),
                    }
                )
            else:
                s = _as_str(it).strip()
                if s:
                    norm.append({"item": s, "tag": "", "descricao": "", "quantidade": "", "material": "", "especificacao": "", "custo_unitario": "", "custo_total": ""})
        result["bom"] = norm

    # CAPEX
    capex = data.get("capex")
    if isinstance(capex, dict):
        for kk in result["capex"].keys():
            try:
                result["capex"][kk] = float(capex.get(kk, 0) or 0)
            except (TypeError, ValueError):
                result["capex"][kk] = 0

    # Precificação / riscos
    prec = data.get("precificacao")
    if isinstance(prec, dict):
        for kk in result["precificacao"].keys():
            try:
                result["precificacao"][kk] = float(prec.get(kk, 0) or 0)
            except (TypeError, ValueError):
                result["precificacao"][kk] = 0

    riscos = data.get("riscos")
    if isinstance(riscos, dict):
        for kk in ("score_geral", "risco_comercial", "risco_financeiro", "risco_contratual", "risco_tecnico", "risco_prazo", "risco_margem"):
            try:
                result["riscos"][kk] = float(riscos.get(kk, 0) or 0)
            except (TypeError, ValueError):
                result["riscos"][kk] = 0
        result["riscos"]["motivos"] = _as_list_str(riscos.get("motivos"))

    # Resumo executivo
    re_ = data.get("resumo_executivo")
    if isinstance(re_, dict):
        result["resumo_executivo"]["texto"] = _as_str(re_.get("texto")).strip()
        result["resumo_executivo"]["recomendacao"] = _as_str(re_.get("recomendacao")).strip()
        result["resumo_executivo"]["principais_pontos"] = _as_list_str(re_.get("principais_pontos"))
    elif isinstance(re_, str):
        result["resumo_executivo"]["texto"] = re_.strip()

    # Alertas críticos
    acs = data.get("alertas_criticos")
    if isinstance(acs, list):
        norm_alerts = []
        for a in acs:
            if isinstance(a, dict):
                norm_alerts.append(
                    {
                        "id": _as_str(a.get("id")).strip(),
                        "severidade": _as_str(a.get("severidade")).strip() or "atencao",
                        "categoria": _as_str(a.get("categoria")).strip(),
                        "titulo": _as_str(a.get("titulo")).strip(),
                        "mensagem": _as_str(a.get("mensagem")).strip(),
                        "evidencia": _as_str(a.get("evidencia")).strip(),
                        "acao_sugerida": _as_str(a.get("acao_sugerida")).strip(),
                        "origem": _as_str(a.get("origem")).strip() or "regras",
                    }
                )
            else:
                s = _as_str(a).strip()
                if s:
                    norm_alerts.append({"id": "", "severidade": "atencao", "categoria": "", "titulo": "Alerta", "mensagem": s, "evidencia": "", "acao_sugerida": "", "origem": "regras"})
        result["alertas_criticos"] = norm_alerts

    # Data quality (permitir que engines preencham)
    dq = data.get("data_quality")
    if isinstance(dq, dict):
        result["data_quality"]["faltantes"] = _as_list_str(dq.get("faltantes"))
        result["data_quality"]["pendencias"] = _as_list_str(dq.get("pendencias"))

    return result


def display_value(value: Any, *, placeholder: str = DEFAULT_NOT_FOUND) -> str:
    """
    Utilitário de UI: converte vazio em placeholder elegante.
    """
    s = _as_str(value).strip()
    return s if s else placeholder

