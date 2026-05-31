import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


DEFAULT_PDF = "/Users/allenwang/Downloads/sat-practice-test-4-digital.pdf"


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"Unauthorized copying.*?CONTINUE", " ", text, flags=re.I | re.S)
    text = re.sub(r"\.{8,}", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pages(pdf_path: str):
    reader = PdfReader(pdf_path)
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        pages.append({"page": index, "text": text})
    return pages


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/seed/extracted-sat-practice-test-4.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pages = extract_pages(pdf_path)
    payload = {
        "source": pdf_path,
        "pageCount": len(pages),
        "note": "Raw private extraction for local study use. Add answer-key metadata before using extracted items for scoring.",
        "pages": pages,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output_path} with {len(pages)} pages")


if __name__ == "__main__":
    main()
