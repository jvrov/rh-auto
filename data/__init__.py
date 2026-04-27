"""Dados do projeto: histórico de contratos em JSON."""
from pathlib import Path
import json
from datetime import datetime

_HISTORY_PATH = Path(__file__).resolve().parent / "contracts_history.json"


def _load() -> list:
    if not _HISTORY_PATH.exists():
        return []
    try:
        with open(_HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save(data: list) -> None:
    _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all_contracts() -> list:
    """Lista todos os contratos: id, nome_contrato, score, data_analise, nivel."""
    rows = _load()
    return [
        {
            "id": r["id"],
            "nome_contrato": r["nome_contrato"],
            "score": r["score"],
            "nivel": r.get("nivel", "moderado"),
            "data_analise": r["data_analise"],
        }
        for r in rows
    ]


def get_contract_by_id(contract_id: int) -> dict | None:
    """Retorna um contrato por id com resultado completo."""
    for r in _load():
        if r["id"] == contract_id:
            return {
                "id": r["id"],
                "nome_contrato": r["nome_contrato"],
                "score": r["score"],
                "nivel": r.get("nivel", "moderado"),
                "data_analise": r["data_analise"],
                "resultado": r.get("resultado", {}),
            }
    return None


def save_contract(nome_contrato: str, score: float, nivel: str, resultado: dict) -> int:
    """Salva resultado da análise. Retorna o id do registro."""
    data = _load()
    next_id = max([r["id"] for r in data], default=0) + 1
    data.append({
        "id": next_id,
        "nome_contrato": nome_contrato,
        "score": score,
        "nivel": nivel,
        "data_analise": datetime.now().isoformat(),
        "resultado": resultado,
    })
    _save(data)
    return next_id
