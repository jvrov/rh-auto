from __future__ import annotations

import re
from typing import Any


def _norm_pct(value: str) -> float | None:
    if not value:
        return None
    s = str(value).strip().lower()
    s = s.replace("%", "").replace(",", ".")
    m = re.search(r"(\\d{1,3}(?:\\.\\d{1,2})?)", s)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _alert(
    *,
    id: str,
    severidade: str,
    categoria: str,
    titulo: str,
    mensagem: str,
    evidencia: str = "",
    acao_sugerida: str = "",
    origem: str = "regras",
) -> dict[str, Any]:
    return {
        "id": id,
        "severidade": severidade,
        "categoria": categoria,
        "titulo": titulo,
        "mensagem": mensagem,
        "evidencia": evidencia,
        "acao_sugerida": acao_sugerida,
        "origem": origem,
    }


def generate_critical_alerts(project: dict[str, Any], raw_text: str = "") -> list[dict[str, Any]]:
    """
    Gera alertas críticos determinísticos a partir do schema canônico.
    Saída: lista de dicts compatíveis com domain.schema.CriticalAlert.
    """
    alerts: list[dict[str, Any]] = []

    cc = project.get("condicoes_comerciais") or {}
    ret = str(cc.get("retencao_contratual") or "")
    multa = str(cc.get("multa_atraso") or "")
    prazo = str(cc.get("prazo_entrega") or "")

    ret_pct = _norm_pct(ret)
    if ret_pct is not None:
        sev = "critico" if ret_pct >= 10 else "atencao" if ret_pct >= 5 else "info"
        alerts.append(
            _alert(
                id="retencao_alta",
                severidade=sev,
                categoria="comercial",
                titulo="Retenção contratual",
                mensagem=f"Retenção contratual de aproximadamente {ret_pct:.1f}%. Isso afeta caixa e pode exigir ajuste de preço/margem.",
                evidencia=ret,
                acao_sugerida="Negociar redução da retenção ou compensar no preço/prazo de recebimento.",
            )
        )
    elif ret.strip():
        alerts.append(
            _alert(
                id="retencao_identificada",
                severidade="atencao",
                categoria="comercial",
                titulo="Retenção contratual identificada",
                mensagem="O documento menciona retenção contratual. Verifique percentual, gatilhos e prazos de liberação.",
                evidencia=ret,
                acao_sugerida="Validar percentual e condições; considerar impacto no fluxo de caixa.",
            )
        )

    multa_pct = _norm_pct(multa)
    if multa_pct is not None:
        sev = "critico" if multa_pct >= 1.0 else "atencao" if multa_pct >= 0.5 else "info"
        alerts.append(
            _alert(
                id="multa_atraso",
                severidade=sev,
                categoria="contratual",
                titulo="Multa por atraso",
                mensagem=f"Multa por atraso de aproximadamente {multa_pct:.2f}%. Risco de margem/prazo.",
                evidencia=multa,
                acao_sugerida="Negociar teto de multa, grace period, e alinhar cronograma com FAT/documentação.",
            )
        )
    elif multa.strip():
        alerts.append(
            _alert(
                id="multa_atraso_identificada",
                severidade="atencao",
                categoria="contratual",
                titulo="Multa por atraso identificada",
                mensagem="O documento menciona multa por atraso. Confirmar percentual, base de cálculo e teto.",
                evidencia=multa,
                acao_sugerida="Confirmar teto e base de cálculo; avaliar contingência no preço.",
            )
        )

    # Prazo agressivo
    if prazo.strip():
        m = re.search(r"(\\d{1,3})\\s*(semanas|semana|weeks|week)", prazo, re.I)
        if m:
            w = int(m.group(1))
            if w <= 14:
                alerts.append(
                    _alert(
                        id="prazo_agressivo",
                        severidade="critico",
                        categoria="prazo",
                        titulo="Prazo agressivo",
                        mensagem=f"Prazo de {w} semanas parece agressivo para escopo industrial com documentação e possíveis FAT.",
                        evidencia=prazo,
                        acao_sugerida="Revisar caminho crítico (engenharia, compras, fabricação, FAT, documentação) e renegociar prazo se necessário.",
                    )
                )
            elif w <= 20:
                alerts.append(
                    _alert(
                        id="prazo_atencao",
                        severidade="atencao",
                        categoria="prazo",
                        titulo="Prazo apertado",
                        mensagem=f"Prazo de {w} semanas pode exigir execução paralela e maior risco operacional.",
                        evidencia=prazo,
                        acao_sugerida="Confirmar lead times críticos e criar plano de mitigação.",
                    )
                )

    # FAT / documentação extensa
    ensaios = project.get("ensaios_documentacao") or []
    if isinstance(ensaios, list) and len(ensaios) >= 8:
        alerts.append(
            _alert(
                id="documentacao_extensa",
                severidade="atencao",
                categoria="tecnico",
                titulo="Documentação/ensaios extensos",
                mensagem="Há muitos requisitos de documentação/ensaios. Isso impacta prazo e custo indireto.",
                evidencia=f"{len(ensaios)} itens em ensaios/documentação",
                acao_sugerida="Detalhar entregáveis, esforço de engenharia e incluir no CAPEX/cronograma.",
            )
        )
    if re.search(r"\\bFAT\\b|factory acceptance test", raw_text, re.I):
        alerts.append(
            _alert(
                id="fat_obrigatorio",
                severidade="atencao",
                categoria="tecnico",
                titulo="FAT identificado",
                mensagem="O texto menciona FAT/Factory Acceptance Test. Isso adiciona custo, agenda e risco de retrabalho.",
                evidencia="FAT mencionado no documento",
                acao_sugerida="Confirmar escopo do FAT, critérios de aceite e janelas de cliente.",
            )
        )

    # Risco alto
    riscos = project.get("riscos") or {}
    try:
        score = float(riscos.get("score_geral", 0) or 0)
    except (TypeError, ValueError):
        score = 0
    if score >= 7:
        alerts.append(
            _alert(
                id="risco_geral_alto",
                severidade="critico",
                categoria="risco",
                titulo="Risco geral alto",
                mensagem=f"Score geral de risco {score:.1f}/10. Recomenda-se revisão executiva e mitigação antes de fechar preço/prazo.",
                evidencia="Riscos > 7/10",
                acao_sugerida="Rever cláusulas comerciais, contingências e plano técnico; ajustar margem/condições.",
            )
        )

    # BOM grande / crítica
    bom = project.get("bom") or []
    if isinstance(bom, list) and len(bom) >= 120:
        alerts.append(
            _alert(
                id="bom_grande",
                severidade="atencao",
                categoria="custos",
                titulo="BOM extensa",
                mensagem="A BOM aparenta ser extensa. Isso aumenta risco de integração, compras e variação de custo.",
                evidencia=f"{len(bom)} itens (aprox.)",
                acao_sugerida="Priorizar itens críticos e lead times; validar custos unitários.",
            )
        )

    # Deduplicação por id (mantém o mais severo se repetir)
    severity_rank = {"info": 0, "atencao": 1, "critico": 2}
    by_id: dict[str, dict[str, Any]] = {}
    for a in alerts:
        aid = str(a.get("id") or "")
        if not aid:
            continue
        if aid not in by_id:
            by_id[aid] = a
        else:
            if severity_rank.get(str(a.get("severidade")), 0) > severity_rank.get(str(by_id[aid].get("severidade")), 0):
                by_id[aid] = a
    return list(by_id.values())


def suggest_status(project: dict[str, Any]) -> str:
    """
    Sugere status automaticamente (parte 'híbrida').
    O usuário pode sobrescrever em persistência/UI.
    """
    riscos = project.get("riscos") or {}
    prec = project.get("precificacao") or {}
    has_analysis = bool(project.get("escopo_solicitado") or project.get("escopo_tecnico") or project.get("condicoes_comerciais"))
    has_pricing = float(prec.get("preco_recomendado", 0) or 0) > 0
    has_risk = float(riscos.get("score_geral", 0) or 0) > 0

    if not has_analysis:
        return "novo"
    if has_pricing and has_risk:
        return "precificado"
    return "em_analise"

