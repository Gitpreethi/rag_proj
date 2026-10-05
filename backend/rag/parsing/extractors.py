from pathlib import Path


def extract_text(path: Path) -> tuple[str, dict]:
    suffix = path.suffix.lower()
    meta: dict = {"page_count": None}
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore"), meta
    if suffix in {".html", ".htm"}:
        from bs4 import BeautifulSoup

        html = path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text("\n"), meta
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        meta["page_count"] = len(reader.pages)
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(f"\n--- Page {i} ---\n{text}")
        return "\n".join(pages), meta
    if suffix == ".docx":
        import docx

        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs), meta
    if suffix == ".json":
        return path.read_text(encoding="utf-8"), meta
    if suffix == ".csv":
        return path.read_text(encoding="utf-8-sig"), meta
    raise ValueError(f"Unsupported document type: {suffix}")
