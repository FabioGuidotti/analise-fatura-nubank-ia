"""Extração de texto de PDFs de fatura usando pdfplumber."""
import pdfplumber


def extract_text(file_bytes: bytes) -> str:
    """Extrai todo o texto de um PDF a partir de seus bytes."""
    import io

    chunks: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def chunk_text(text: str, max_chars: int = 14000) -> list[str]:
    """Divide o texto em blocos preservando linhas inteiras."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.split("\n"):
        if current_len + len(line) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(line) + 1
        else:
            current.append(line)
            current_len += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks
