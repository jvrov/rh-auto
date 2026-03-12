"""Rotas da aplicação IDI."""
import json
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, current_app

from . import models
from .pdf_reader import extract_text_from_pdf
from .contract_analyzer import analyze_contract
from .hybrid_risk_score import compute_hybrid_score, get_nivel_risco, combine_scores


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"pdf"})


def register_routes(app):
    """Registra as rotas no app Flask."""

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/analyze", methods=["POST"])
    def analyze():
        print("[IDI] === Início da análise ===")
        if "contract" not in request.files:
            print("[IDI] ERRO: Nenhum arquivo enviado no request.")
            flash("Nenhum arquivo enviado.", "error")
            return redirect(url_for("index"))
        file = request.files["contract"]
        if not file or file.filename == "":
            print("[IDI] ERRO: Nenhum arquivo selecionado.")
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("index"))
        if not allowed_file(file.filename):
            print("[IDI] ERRO: Arquivo não é PDF:", file.filename)
            flash("Apenas arquivos PDF são permitidos.", "error")
            return redirect(url_for("index"))

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        print("[IDI] PDF salvo em:", filepath)

        try:
            text = extract_text_from_pdf(filepath)
            print("[IDI] Texto extraído do PDF: %d caracteres" % len(text))
        except Exception as e:
            print("[IDI] ERRO ao ler PDF:", type(e).__name__, str(e))
            flash(f"Erro ao ler o PDF: {e}", "error")
            return redirect(url_for("index"))

        api_key = current_app.config.get("OPENAI_API_KEY", "")
        if not api_key:
            print("[IDI] AVISO: OPENAI_API_KEY não está configurada.")
        else:
            print("[IDI] OPENAI_API_KEY configurada (len=%d)" % len(api_key))
        try:
            print("[IDI] Enviando texto para análise com OpenAI...")
            analysis = analyze_contract(text, api_key)
            score_ia = analysis.get("score_risco", 5.0)
            score_hibrido = compute_hybrid_score(analysis)
            risk_score = combine_scores(score_ia, score_hibrido)
            analysis["score_risco"] = risk_score
            analysis["nivel_risco"] = get_nivel_risco(risk_score)
            print("[IDI] Análise concluída. Score IA=%.1f, Híbrido=%.1f, Final=%.1f (%s)" % (score_ia, score_hibrido, risk_score, analysis["nivel_risco"]))
        except Exception as e:
            print("[IDI] ERRO na análise com IA:", type(e).__name__, str(e))
            import traceback
            traceback.print_exc()
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "insufficient_quota" in msg.lower():
                flash(
                    "Cota da API excedida ou sem créditos. Adicione forma de pagamento e créditos em: platform.openai.com/account/billing",
                    "error",
                )
            else:
                flash(f"Erro na análise com IA: {e}", "error")
            return redirect(url_for("index"))

        analysis_text = json.dumps(analysis, ensure_ascii=False)
        contract_id = models.save_contract(filename, risk_score, analysis_text)
        print("[IDI] Contrato salvo no banco. ID:", contract_id)
        print("[IDI] === Fim da análise (sucesso) ===\n")
        return redirect(url_for("result", contract_id=contract_id))

    @app.route("/result/<int:contract_id>")
    def result(contract_id):
        print("[IDI] Exibindo resultado do contrato ID:", contract_id)
        contract = models.get_contract(contract_id)
        if not contract:
            print("[IDI] ERRO: Contrato não encontrado. ID:", contract_id)
            flash("Contrato não encontrado.", "error")
            return redirect(url_for("index"))
        analysis = {}
        try:
            analysis = json.loads(contract["analysis_text"])
        except (json.JSONDecodeError, TypeError):
            pass
        risk_score = contract["risk_score"]
        return render_template(
            "result.html",
            filename=contract["filename"],
            risk_score=risk_score,
            nivel_risco=analysis.get("nivel_risco") or ("baixo" if risk_score <= 3 else ("moderado" if risk_score <= 6 else "alto")),
            multas=analysis.get("multas", []),
            retencoes=analysis.get("retencoes", []) or analysis.get("retencoes_financeiras", []),
            responsabilidades_contratada=analysis.get("responsabilidades_contratada", []),
            responsabilidades_contratante=analysis.get("responsabilidades_contratante", []),
            responsabilidades=analysis.get("responsabilidades", []),
            clausulas_perigosas=analysis.get("clausulas_perigosas", []),
            riscos_financeiros=analysis.get("riscos_financeiros", []),
            riscos_juridicos=analysis.get("riscos_juridicos", []),
            riscos_operacionais=analysis.get("riscos_operacionais", []),
            sugestoes=analysis.get("sugestoes_negociacao", []),
        )
