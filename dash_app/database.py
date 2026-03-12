"""
Gerencia o banco SQLite para histórico de contratos analisados.
Tabela: contracts_history (id, nome_contrato, score, nivel, data_analise, resultado_json).
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

_DB_PATH = None


def init_db(db_path: str = None) -> None:
    """Inicializa o banco e cria a tabela se não existir."""
    global _DB_PATH
    _DB_PATH = db_path or str(Path(__file__).resolve().parent.parent / "idi.db")
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS contracts_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_contrato TEXT NOT NULL,
                score REAL NOT NULL,
                nivel TEXT NOT NULL,
                data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resultado_json TEXT NOT NULL
            )
        """)
        c.commit()


@contextmanager
def _conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_contract(nome_contrato: str, score: float, nivel: str, resultado: dict) -> int:
    """Salva resultado da análise. Retorna o id do registro."""
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO contracts_history (nome_contrato, score, nivel, resultado_json)
               VALUES (?, ?, ?, ?)""",
            (nome_contrato, score, nivel, json.dumps(resultado, ensure_ascii=False)),
        )
        c.commit()
        return cur.lastrowid


def get_all_contracts() -> list:
    """Lista todos os contratos: id, nome_contrato, score, data_analise."""
    with _conn() as c:
        rows = c.execute(
            """SELECT id, nome_contrato, score, nivel, data_analise
               FROM contracts_history ORDER BY data_analise DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


def clear_history() -> None:
    """Remove todos os registros do histórico de contratos."""
    with _conn() as c:
        c.execute("DELETE FROM contracts_history")
        c.commit()


def get_contract_by_id(contract_id: int) -> dict | None:
    """Retorna um contrato por id, com resultado_json parseado."""
    with _conn() as c:
        row = c.execute(
            "SELECT id, nome_contrato, score, nivel, data_analise, resultado_json FROM contracts_history WHERE id = ?",
            (contract_id,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["resultado"] = json.loads(d["resultado_json"])
        except (json.JSONDecodeError, TypeError):
            d["resultado"] = {}
        return d
