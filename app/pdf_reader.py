"""Leitura e extração de texto de PDFs."""
import pdfplumber
from pathlib import Path


def extract_text_from_pdf(filepath: str | Path) -> str:
    """
    Extrai todo o texto de um arquivo PDF.
    Retorna string com o conteúdo ou levanta exceção em caso de erro.
    """
    path = Path(filepath)
    print("[IDI] pdf_reader: extraindo texto de", path.name)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("O arquivo deve ser um PDF.")

    text_parts = []
    with pdfplumber.open(path) as pdf:
        num_pages = len(pdf.pages)
        print("[IDI] pdf_reader: PDF tem %d página(s)" % num_pages)
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text_parts.append(content)

    if not text_parts:
        print("[IDI] pdf_reader: ERRO - Nenhum texto extraído.")
        raise ValueError("Nenhum texto foi extraído do PDF.")
    text = "\n\n".join(text_parts)
    print("[IDI] pdf_reader: extração ok, total %d caracteres" % len(text))
    return text
