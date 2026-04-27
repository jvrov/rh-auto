"""
SQLite database layer (projetos industriais / documentos / chat / precificação).

Banco principal do sistema (substitui o JSON como fonte de verdade).
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DBConfig:
    path: Path


_DB: DBConfig | None = None


def init_db(db_path: str | Path) -> None:
    """Inicializa o DB e cria tabelas se necessário."""
    global _DB
    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    _DB = DBConfig(path=path)

    with _conn() as c:
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA foreign_keys=ON;")

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_projeto TEXT,
                cliente TEXT,
                data_analise TEXT NOT NULL,
                updated_at TEXT,
                status TEXT,
                prazo_estimado TEXT,
                score_risco REAL,
                nivel_risco TEXT,
                custo_total_estimado REAL,
                margem_sugerida REAL,
                preco_sugerido REAL,
                resumo_executivo_text TEXT,
                resumo_json TEXT NOT NULL
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS uploaded_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                nome_arquivo TEXT NOT NULL,
                tipo_documento TEXT,
                caminho_arquivo TEXT,
                texto_extraido TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                role TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                data_hora TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS pricing_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                margem_percentual REAL NOT NULL,
                preco_minimo REAL,
                preco_recomendado REAL,
                observacoes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS project_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                alert_id TEXT,
                severidade TEXT NOT NULL,
                categoria TEXT,
                titulo TEXT,
                mensagem TEXT NOT NULL,
                evidencia TEXT,
                acao_sugerida TEXT,
                origem TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resolved_at TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            """
        )

        _ensure_columns(c)
        c.commit()


def _ensure_columns(conn: sqlite3.Connection) -> None:
    """
    Migrações leves: adiciona colunas novas sem destruir dados.
    (SQLite: ALTER TABLE ADD COLUMN)
    """
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(projects)").fetchall()}
    wanted = {
        "updated_at": "TEXT",
        "status": "TEXT",
        "prazo_estimado": "TEXT",
        "resumo_executivo_text": "TEXT",
    }
    for name, typ in wanted.items():
        if name not in cols:
            conn.execute(f"ALTER TABLE projects ADD COLUMN {name} {typ}")


@contextmanager
def _conn():
    if _DB is None:
        raise RuntimeError("DB não inicializado. Chame init_db() primeiro.")
    conn = sqlite3.connect(str(_DB.path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_project(
    *,
    nome_projeto: str | None,
    cliente: str | None,
    score_risco: float | None,
    nivel_risco: str | None,
    custo_total_estimado: float | None,
    margem_sugerida: float | None,
    preco_sugerido: float | None,
    resumo: dict,
) -> int:
    """Cria um projeto e retorna project_id."""
    with _conn() as c:
        now = _utc_now_iso()
        # Campos novos (se existirem no schema)
        status = (resumo or {}).get("status_projeto") if isinstance(resumo, dict) else None
        prazo_estimado = (resumo or {}).get("prazo_estimado") if isinstance(resumo, dict) else None
        re_ = (resumo or {}).get("resumo_executivo") if isinstance(resumo, dict) else None
        resumo_executivo_text = ""
        if isinstance(re_, dict):
            resumo_executivo_text = str(re_.get("texto") or "")
        elif isinstance(re_, str):
            resumo_executivo_text = re_
        cur = c.execute(
            """
            INSERT INTO projects
                (nome_projeto, cliente, data_analise, updated_at, status, prazo_estimado,
                 score_risco, nivel_risco, custo_total_estimado, margem_sugerida, preco_sugerido,
                 resumo_executivo_text, resumo_json)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nome_projeto,
                cliente,
                now,
                now,
                status,
                prazo_estimado,
                score_risco,
                nivel_risco,
                custo_total_estimado,
                margem_sugerida,
                preco_sugerido,
                resumo_executivo_text,
                json.dumps(resumo, ensure_ascii=False),
            ),
        )
        c.commit()
        return int(cur.lastrowid)


def upsert_project_alerts(project_id: int, alerts: list[dict[str, Any]]) -> None:
    """
    Persiste snapshot de alertas críticos.
    Estratégia simples: limpa alertas 'open' anteriores e re-insere.
    """
    with _conn() as c:
        c.execute("DELETE FROM project_alerts WHERE project_id = ? AND status = 'open'", (project_id,))
        for a in alerts or []:
            c.execute(
                """
                INSERT INTO project_alerts
                    (project_id, alert_id, severidade, categoria, titulo, mensagem, evidencia, acao_sugerida, origem, status, created_at, resolved_at)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, NULL)
                """,
                (
                    project_id,
                    str(a.get("id") or ""),
                    str(a.get("severidade") or "atencao"),
                    str(a.get("categoria") or ""),
                    str(a.get("titulo") or ""),
                    str(a.get("mensagem") or ""),
                    str(a.get("evidencia") or ""),
                    str(a.get("acao_sugerida") or ""),
                    str(a.get("origem") or "regras"),
                    _utc_now_iso(),
                ),
            )
        c.commit()


def list_project_alerts(project_id: int, status: str = "open", limit: int = 100) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id, project_id, alert_id, severidade, categoria, titulo, mensagem, evidencia, acao_sugerida, origem,
                   status, created_at, resolved_at
            FROM project_alerts
            WHERE project_id = ? AND status = ?
            ORDER BY CASE severidade WHEN 'critico' THEN 2 WHEN 'atencao' THEN 1 ELSE 0 END DESC,
                     datetime(created_at) DESC
            LIMIT ?
            """,
            (project_id, status, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def list_projects(limit: int = 200) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id, nome_projeto, cliente, data_analise, score_risco, nivel_risco,
                   custo_total_estimado, margem_sugerida, preco_sugerido
            FROM projects
            ORDER BY datetime(data_analise) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_project(project_id: int) -> dict[str, Any] | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["resumo"] = json.loads(d.get("resumo_json") or "{}")
        except json.JSONDecodeError:
            d["resumo"] = {}
        return d


def add_uploaded_document(
    *,
    project_id: int,
    nome_arquivo: str,
    tipo_documento: str | None,
    caminho_arquivo: str | None,
    texto_extraido: str | None,
) -> int:
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO uploaded_documents
                (project_id, nome_arquivo, tipo_documento, caminho_arquivo, texto_extraido, created_at)
            VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (project_id, nome_arquivo, tipo_documento, caminho_arquivo, texto_extraido, _utc_now_iso()),
        )
        c.commit()
        return int(cur.lastrowid)


def list_project_documents(project_id: int) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id, project_id, nome_arquivo, tipo_documento, caminho_arquivo, created_at
            FROM uploaded_documents
            WHERE project_id = ?
            ORDER BY datetime(created_at) DESC
            """,
            (project_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def add_chat_message(*, project_id: int | None, role: str, mensagem: str) -> int:
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO chat_history (project_id, role, mensagem, data_hora)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, role, mensagem, _utc_now_iso()),
        )
        c.commit()
        return int(cur.lastrowid)


def list_chat_history(project_id: int | None, limit: int = 100) -> list[dict[str, Any]]:
    with _conn() as c:
        if project_id is None:
            rows = c.execute(
                """
                SELECT id, project_id, role, mensagem, data_hora
                FROM chat_history
                WHERE project_id IS NULL
                ORDER BY datetime(data_hora) ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = c.execute(
                """
                SELECT id, project_id, role, mensagem, data_hora
                FROM chat_history
                WHERE project_id = ?
                ORDER BY datetime(data_hora) ASC
                LIMIT ?
                """,
                (project_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]


def add_pricing_scenario(
    *,
    project_id: int,
    margem_percentual: float,
    preco_minimo: float | None,
    preco_recomendado: float | None,
    observacoes: str | None,
) -> int:
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO pricing_scenarios
                (project_id, margem_percentual, preco_minimo, preco_recomendado, observacoes, created_at)
            VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (project_id, margem_percentual, preco_minimo, preco_recomendado, observacoes, _utc_now_iso()),
        )
        c.commit()
        return int(cur.lastrowid)


def list_pricing_scenarios(project_id: int, limit: int = 50) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            """
            SELECT id, project_id, margem_percentual, preco_minimo, preco_recomendado, observacoes, created_at
            FROM pricing_scenarios
            WHERE project_id = ?
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

