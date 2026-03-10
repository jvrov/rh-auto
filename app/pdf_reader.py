"""Leitura e extração de texto de PDFs."""
import pdfplumber
from pathlib import Path


def extract_text_from_pdf(filepath: str | Path) -> str:
    """
    Extrai todo o texto de um arquivo PDF.
    Retorna string com o conteúdo ou levanta exceção em caso de erro.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("O arquivo deve ser um PDF.")

    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text_parts.append(content)

    if not text_parts:
        raise ValueError("Nenhum texto foi extraído do PDF.")
    return "\n\n".join(text_parts)
