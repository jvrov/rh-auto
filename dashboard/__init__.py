"""Pacote `dashboard`.

O app Dash principal é criado em `dashboard/app.py`.
Este arquivo evita importar `dashboard/dashboard.py` (legado), que pode quebrar
IDs/callbacks quando o layout evolui.
"""

__all__ = []
