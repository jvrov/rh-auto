"""
Migra o histórico legado (JSON) para o SQLite (projects).

Uso:
  .venv/bin/python -m app.migrate_json_to_sqlite
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from config import DATABASE_PATH
from app.database import init_db, create_project

logger = logging.getLogger(__name__)


def _load_legacy_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    init_db(DATABASE_PATH)
    legacy_path = Path(__file__).resolve().parent.parent / "data" / "contracts_history.json"
    rows = _load_legacy_json(legacy_path)
    if not rows:
        logger.info("Nada para migrar.")
        return

    migrated = 0
    for r in rows:
        result = r.get("resultado") or {}
        nome = result.get("nome_contrato") or r.get("nome_contrato")
        score = result.get("score") if isinstance(result, dict) else r.get("score")
        nivel = result.get("nivel") if isinstance(result, dict) else r.get("nivel")
        resumo = {
            "tipo": "contrato_legado",
            "nome_contrato": nome,
            "resultado": result,
            "data_analise_legacy": r.get("data_analise"),
        }
        create_project(
            nome_projeto=nome,
            cliente=None,
            score_risco=float(score) if score is not None else None,
            nivel_risco=nivel,
            custo_total_estimado=None,
            margem_sugerida=None,
            preco_sugerido=None,
            resumo=resumo,
        )
        migrated += 1

    logger.info("Migrados %s registros para %s", migrated, DATABASE_PATH)


if __name__ == "__main__":
    main()

