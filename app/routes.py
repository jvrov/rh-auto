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
        if "contract" not in request.files:
            flash("Nenhum arquivo enviado.", "error")
            return redirect(url_for("index"))
        file = request.files["contract"]
        if not file or file.filename == "":
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("index"))
        if not allowed_file(file.filename):
            flash("Apenas arquivos PDF são permitidos.", "error")
            return redirect(url_for("index"))

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        try:
            text = extract_text_from_pdf(filepath)
        except Exception as e:
            flash(f"Erro ao ler o PDF: {e}", "error")
            return redirect(url_for("index"))

        api_key = current_app.config.get("OPENAI_API_KEY", "")
        try:
            analysis = analyze_contract(text, api_key)
            risk_score = calculate_risk_score(analysis, text, api_key)
        except Exception as e:
            flash(f"Erro na análise com IA: {e}", "error")
            return redirect(url_for("index"))

        analysis_text = json.dumps(analysis, ensure_ascii=False)
        contract_id = models.save_contract(filename, risk_score, analysis_text)

        return redirect(url_for("result", contract_id=contract_id))

    @app.route("/result/<int:contract_id>")
    def result(contract_id):
        contract = models.get_contract(contract_id)
        if not contract:
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
