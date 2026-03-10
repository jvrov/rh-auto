"""Modelos do banco de dados."""
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

# Caminho do banco (será definido pelo app)
_db_path = None


def init_db(db_path: str) -> None:
    """Inicializa o banco e cria a tabela contracts."""
    global _db_path
    _db_path = db_path
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                risk_score REAL NOT NULL,
                analysis_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


@contextmanager
def _get_connection():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_contract(filename: str, risk_score: float, analysis_text: str) -> int:
    """Salva resultado da análise e retorna o id."""
    with _get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO contracts (filename, risk_score, analysis_text) VALUES (?, ?, ?)",
            (filename, risk_score, analysis_text),
        )
        conn.commit()
        return cur.lastrowid


def get_contract(contract_id: int) -> dict | None:
    """Retorna um contrato por id."""
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
        if row is None:
            return None
        return dict(row)
