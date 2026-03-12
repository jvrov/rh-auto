"""Extrai texto de arquivos PDF."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from app.pdf_reader import extract_text_from_pdf
except ImportError:
    import pdfplumber

    def extract_text_from_pdf(filepath):
        path = Path(filepath)
        if not path.exists() or path.suffix.lower() != ".pdf":
            raise ValueError("Arquivo PDF inválido.")
        parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        if not parts:
            raise ValueError("Nenhum texto extraído do PDF.")
        return "\n\n".join(parts)
