"""
Contract Risk Analyzer AI — aplicativo desktop com janela própria.

Fluxo:
  1. Servidor Dash inicia em segundo plano (sem abrir navegador).
  2. Janela gráfica abre na área de trabalho (pywebview).
  3. O dashboard é exibido dentro da janela.
  4. Nenhum navegador abre. Nenhuma interface no terminal.

Execute: python main.py  (ou .venv/bin/python main.py)
Defina antes: export OPENAI_API_KEY="sua-chave"
"""
import sys
import socket
import threading
import time
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

from dashboard.app import create_dash_app
from dashboard.callbacks import auth, navigation, history, analysis, chat
from desktop.desktop_app import create_window

PORT_RANGE = (8050, 8060)


def find_free_port(start: int, end: int) -> int:
    """Retorna a primeira porta livre entre start e end (inclusive)."""
    for port in range(start, end + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Nenhuma porta livre entre {start} e {end}")


def run_dash_server(port: int):
    """Roda o servidor Dash em segundo plano (apenas localhost)."""
    app = create_dash_app()
    auth.register(app)
    navigation.register(app)
    history.register(app)
    analysis.register(app)
    chat.register(app)
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def wait_for_server(url: str, timeout=15, interval=0.3) -> bool:
    """Aguarda o servidor responder antes de abrir a janela."""
    import urllib.request
    import urllib.error
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(interval)
    return False


def main():
    port = find_free_port(PORT_RANGE[0], PORT_RANGE[1])
    logger.info("Iniciando servidor Dash na porta %s", port)
    # Cache-bust para o WebEngine recarregar CSS/JS do Dash
    dash_url = f"http://127.0.0.1:{port}/?v={int(time.time())}"

    server_thread = threading.Thread(target=run_dash_server, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(dash_url):
        logger.error("Servidor Dash não respondeu a tempo.")
        sys.exit(1)

    try:
        create_window(url=dash_url)
    except RuntimeError as e:
        logger.error("%s", e)
        sys.exit(1)
    except Exception as e:
        err = str(e).lower()
        if "qt" in err or "gtk" in err or "gi" in err or "webview" in err:
            logger.error(
                "Para abrir a janela do aplicativo, instale as dependências:\n"
                "  sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.1\n"
                "Ou (sem sudo): pip install PyQt6 PyQt6-WebEngine"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
