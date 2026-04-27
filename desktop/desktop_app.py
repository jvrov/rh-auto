"""
Janela desktop do aplicativo.

Tenta pywebview (GTK/Qt do sistema); se falhar, usa PyQt6 (pip install).
Cria uma janela na área de trabalho e carrega o dashboard. Nenhum navegador é aberto.
"""
WINDOW_TITLE = "Contract Risk Analyzer AI"
DEFAULT_URL = "http://127.0.0.1:8050"


def _create_window_pywebview(url: str):
    """Janela com pywebview (requer GTK ou Qt no sistema)."""
    import webview
    webview.create_window(
        WINDOW_TITLE,
        url,
        width=1280,
        height=800,
        min_size=(800, 600),
        fullscreen=True,
    )
    webview.start()


def _create_window_pyqt6(url: str):
    """Janela com PyQt6 + WebEngine (pip install PyQt6 PyQt6-WebEngine)."""
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle(WINDOW_TITLE)
    view = QWebEngineView()
    view.load(QUrl(url))
    window.setCentralWidget(view)
    window.showMaximized()
    sys.exit(app.exec())


def create_window(url: str = DEFAULT_URL):
    """
    Abre a janela gráfica do aplicativo e exibe o dashboard.
    O servidor Dash deve já estar rodando em url.
    Tenta PyQt6 primeiro (pip); se não estiver instalado, tenta pywebview (GTK/Qt do sistema).
    """
    # PyQt6 primeiro para evitar mensagens de erro do pywebview quando GTK/Qt não estão instalados
    try:
        _create_window_pyqt6(url)
    except ImportError:
        try:
            _create_window_pywebview(url)
        except Exception as e:
            raise RuntimeError(
                "Para abrir a janela, use uma das opções:\n"
                "  1) pip install PyQt6 PyQt6-WebEngine\n"
                "  2) Ou instalar GTK no sistema:\n"
                "     sudo apt install python3-gi python3-gi-cairo gir1.2-webkit2-4.1"
            ) from e
