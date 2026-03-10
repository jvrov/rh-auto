"""Rotas da aplicação IDI."""
import json
import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, current_app

from . import models
from .pdf_reader import extract_text_from_pdf
from .contract_analyzer import analyze_contract
from .risk_score import calculate_risk_score


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
            risk_score = calculate_risk_score(analysis, text, api_key)
            print("[IDI] Análise concluída. Score de risco: %.1f" % risk_score)
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
        return render_template(
            "result.html",
            filename=contract["filename"],
            risk_score=contract["risk_score"],
            multas=analysis.get("multas", []),
            retencoes=analysis.get("retencoes_financeiras", []),
            responsabilidades=analysis.get("responsabilidades", []),
            clausulas_perigosas=analysis.get("clausulas_perigosas", []),
            sugestoes=analysis.get("sugestoes_negociacao", []),
        )
