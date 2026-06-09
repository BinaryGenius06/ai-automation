import re
import pdfplumber
from typing import List
import httpx
import tempfile
import os


def load_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
# Max PDF size: 10MB — prevents loading huge files on free tier
MAX_PDF_BYTES = 10 * 1024 * 1024

# Block internal/private URLs — basic SSRF protection
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254"}

def load_from_url(url: str) -> str:
    """
    Download PDF from public URL and extract text.
    Blocks private IPs. Enforces 10MB size limit.
    """
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ""
    if host in BLOCKED_HOSTS or host.startswith("192.168") or host.startswith("10."):
        raise ValueError("Private/internal URLs not allowed")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()

            if len(response.content) > MAX_PDF_BYTES:
                raise ValueError(f"PDF too large ({len(response.content)//1024//1024}MB). Max 10MB.")

            content_type = response.headers.get("content-type", "")
            allowed_types = {"pdf", "octet-stream"}
            if not any(t in content_type for t in allowed_types) and not url.endswith(".pdf"):
                raise ValueError(f"URL does not point to a PDF. Content-Type: {content_type}")

            with open(tmp_path, "wb") as f:
                f.write(response.content)

        return load_pdf(tmp_path)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_break = max(chunk.rfind(". "), chunk.rfind("\n"))
            if last_break > chunk_size // 2:
                chunk = chunk[:last_break + 1]
        chunks.append(chunk.strip())
        start += max(1, len(chunk) - overlap)
    return [c for c in chunks if len(c) > 50]


def search_chunks(query: str, chunks: List[str], top_k: int = 3) -> List[str]:
    """Keyword-based chunk search — returns top_k most relevant chunks."""
    query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
    stop_words = {"the", "and", "for", "are", "was", "what", "how",
                  "when", "where", "who", "which", "this", "that",
                  "with", "have", "from", "they", "will", "your"}
    query_words -= stop_words
    if not query_words:
        return chunks[:top_k]
    scored = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower)
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0] or chunks[:top_k]


if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    print(f"Loading: {pdf_path}")
    text = load_pdf(pdf_path)
    print(f"Extracted {len(text)} characters")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks\n")
    query = "what are the fees"
    results = search_chunks(query, chunks)
    print(f"Top chunks for '{query}':")
    for i, chunk in enumerate(results):
        print(f"\n--- Chunk {i+1} ---\n{chunk}")