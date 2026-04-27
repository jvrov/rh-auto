from __future__ import annotations

import base64
import logging
from pathlib import Path

from dash import Dash, Input, Output, State, no_update, ctx

from dashboard import components as comp
from app.chat_engine import get_chat_response
from app.database import add_chat_message, create_project, add_uploaded_document, upsert_project_alerts
from app.pdf_parser import extract_text_from_pdf
from app.project_intelligence import analyze_industrial_project
from domain.normalize import normalize_project

ROOT = Path(__file__).resolve().parent.parent.parent
logger = logging.getLogger(__name__)


def _parse_upload(contents):
    if not contents:
        return None
    try:
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        tmp = ROOT / "uploads" / "_tmp_chat_upload.pdf"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(decoded)
        text = extract_text_from_pdf(tmp)
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        return text
    except Exception:
        logger.exception("Falha ao extrair texto do PDF no chat")
        return None


def register(app: Dash) -> None:
    @app.callback(
        [
            Output(comp.ID_CHAT_HISTORY_STORE, "data"),
            Output(comp.ID_CHAT_MESSAGES, "children"),
            Output(comp.ID_CHAT_INPUT, "value"),
            Output(comp.ID_RESULTADO_STORE, "data"),
            Output(comp.ID_CONTRACT_ID_STORE, "data"),
            Output(comp.ID_HISTORY_REFRESH_TRIGGER, "data"),
        ],
        [
            Input(comp.ID_CHAT_SEND, "n_clicks"),
            Input(comp.ID_CHAT_INPUT, "n_submit"),
            Input(comp.ID_QUICK_PROMPT_1, "n_clicks"),
            Input(comp.ID_QUICK_PROMPT_2, "n_clicks"),
            Input(comp.ID_QUICK_PROMPT_3, "n_clicks"),
            Input(comp.ID_QUICK_PROMPT_4, "n_clicks"),
            Input(comp.ID_QUICK_PROMPT_5, "n_clicks"),
        ],
        [
            State(comp.ID_CHAT_INPUT, "value"),
            State(comp.ID_CHAT_HISTORY_STORE, "data"),
            State(comp.ID_RESULTADO_STORE, "data"),
            State(comp.ID_CONTRACT_ID_STORE, "data"),
            State(comp.ID_CHAT_UPLOAD, "contents"),
            State(comp.ID_CHAT_UPLOAD, "filename"),
        ],
        prevent_initial_call=True,
    )
    def on_chat_send(
        n_clicks,
        n_submit,
        qp1,
        qp2,
        qp3,
        qp4,
        qp5,
        value,
        history,
        contract_result,
        project_id,
        upload_contents,
        upload_filename,
    ):
        trig = ctx.trigger_id if hasattr(ctx, "trigger_id") else None
        quick_map = {
            comp.ID_QUICK_PROMPT_1: "Resuma este projeto.",
            comp.ID_QUICK_PROMPT_2: "Quais são os maiores riscos? Liste os 5 principais e justifique.",
            comp.ID_QUICK_PROMPT_3: "Sugira um preço de venda com base no custo, risco e margem recomendada.",
            comp.ID_QUICK_PROMPT_4: "Quais itens e fatores mais impactam a margem? O que devo validar primeiro?",
            comp.ID_QUICK_PROMPT_5: "Esse prazo é agressivo? O que pode dar errado e como mitigar?",
        }
        if trig in quick_map:
            value = quick_map[trig]

        if not value or not (value := (value or "").strip()):
            return no_update, no_update, no_update, no_update, no_update, no_update

        history = list(history or [])
        history.append({"role": "user", "content": value})
        pid = int(project_id) if project_id else None

        # Se veio PDF junto, analisa e cria/atualiza o projeto antes de responder
        new_project = None
        new_project_id = None
        if upload_contents:
            text = _parse_upload(upload_contents)
            if text:
                nome_arquivo = upload_filename or "documento.pdf"
                try:
                    result = normalize_project(analyze_industrial_project(text, filename=nome_arquivo))
                    new_project = result
                    new_project_id = create_project(
                        nome_projeto=result.get("projeto") or nome_arquivo,
                        cliente=result.get("cliente") or None,
                        score_risco=float((result.get("riscos") or {}).get("score_geral")) if result.get("riscos") else None,
                        nivel_risco=None,
                        custo_total_estimado=float((result.get("capex") or {}).get("custo_total", 0) or 0) if isinstance(result.get("capex"), dict) else None,
                        margem_sugerida=float((result.get("precificacao") or {}).get("margem_sugerida")) if result.get("precificacao") else None,
                        preco_sugerido=float((result.get("precificacao") or {}).get("preco_recomendado")) if result.get("precificacao") else None,
                        resumo=result,
                    )
                    try:
                        add_uploaded_document(
                            project_id=new_project_id,
                            nome_arquivo=nome_arquivo,
                            tipo_documento="pdf",
                            caminho_arquivo=None,
                            texto_extraido=text,
                        )
                    except Exception:
                        logger.exception("Falha ao persistir documento do chat")
                    try:
                        upsert_project_alerts(new_project_id, result.get("alertas_criticos") or [])
                    except Exception:
                        logger.exception("Falha ao persistir alertas do chat")
                    pid = int(new_project_id)
                except Exception:
                    logger.exception("Falha na análise do PDF enviado no chat")

        add_chat_message(project_id=pid, role="user", mensagem=value)

        # Contexto do chat deve ser o projeto analisado mais recente
        ctx_project = new_project or contract_result
        reply = get_chat_response(value, history, ctx_project)
        history.append({"role": "assistant", "content": reply})
        add_chat_message(project_id=pid, role="assistant", mensagem=reply)
        return (
            history,
            comp.render_chat_messages(history),
            "",
            new_project if new_project is not None else no_update,
            pid if pid is not None else no_update,
            pid if pid is not None else no_update,
        )

