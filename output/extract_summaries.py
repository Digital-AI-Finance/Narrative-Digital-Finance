"""Extract text and create summaries from all PDFs in output folder."""
import fitz  # PyMuPDF
from pathlib import Path
from collections import Counter
import re

# Base directory
BASE_DIR = Path(__file__).parent

# Find all PDFs recursively
def find_pdfs(folder: Path) -> list:
    """Find all PDF files in folder and subfolders."""
    return list(folder.rglob("*.pdf"))

def extract_text(pdf_path: Path) -> dict:
    """Extract text and metadata from a PDF."""
    try:
        doc = fitz.open(pdf_path)

        # Metadata
        metadata = doc.metadata
        page_count = len(doc)

        # Extract text page by page
        full_text = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            full_text.append(text)

        # Get TOC if available
        toc = doc.get_toc()

        doc.close()

        return {
            "path": pdf_path,
            "filename": pdf_path.name,
            "rel_path": pdf_path.relative_to(BASE_DIR),
            "metadata": metadata,
            "page_count": page_count,
            "toc": toc,
            "text": "\n\n".join(full_text),
            "text_pages": full_text
        }
    except Exception as e:
        return {
            "path": pdf_path,
            "filename": pdf_path.name,
            "error": str(e)
        }

def extract_keywords(text: str, top_n: int = 10) -> list:
    """Extract top keywords from text (simple frequency-based)."""
    # Common stopwords
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
        't', 'just', 'don', 'now', 'also', 'et', 'al', 'fig', 'figure', 'table'
    }

    # Extract words (3+ chars, alphabetic)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    words = [w for w in words if w not in stopwords]

    # Count and return top N
    counter = Counter(words)
    return counter.most_common(top_n)

def get_first_n_words(text: str, n: int = 500) -> str:
    """Get first N words of text."""
    words = text.split()
    return " ".join(words[:n])

def create_summary(doc_data: dict) -> str:
    """Create a summary entry for a document."""
    if "error" in doc_data:
        return f"""
## {doc_data['filename']}
**Error:** {doc_data['error']}
"""

    metadata = doc_data["metadata"]
    title = metadata.get("title", "") or doc_data["filename"]
    author = metadata.get("author", "Unknown")

    # Keywords
    keywords = extract_keywords(doc_data["text"])
    keyword_str = ", ".join([f"{w}({c})" for w, c in keywords[:8]])

    # First 500 words
    intro = get_first_n_words(doc_data["text"], 500)
    # Clean up whitespace
    intro = " ".join(intro.split())

    # TOC
    toc_str = ""
    if doc_data["toc"]:
        toc_items = [f"  - {item[1]}" for item in doc_data["toc"][:10]]
        toc_str = "\n**Table of Contents:**\n" + "\n".join(toc_items)
        if len(doc_data["toc"]) > 10:
            toc_str += f"\n  - ... ({len(doc_data['toc']) - 10} more sections)"

    return f"""
## {title}

| Property | Value |
|----------|-------|
| File | `{doc_data['rel_path']}` |
| Pages | {doc_data['page_count']} |
| Author | {author} |
| Keywords | {keyword_str} |
{toc_str}

**Introduction (first 500 words):**

> {intro}...

---
"""

def main():
    print("=" * 60)
    print("PDF Extraction & Summarization")
    print("=" * 60)

    # Create output folder for extracted text
    text_folder = BASE_DIR / "extracted_text"
    text_folder.mkdir(exist_ok=True)

    # Find all PDFs
    pdfs = find_pdfs(BASE_DIR)
    print(f"\nFound {len(pdfs)} PDFs:")
    for pdf in pdfs:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"  - {pdf.relative_to(BASE_DIR)} ({size_mb:.1f} MB)")

    # Process each PDF
    summaries = []
    for pdf in pdfs:
        print(f"\nProcessing: {pdf.name}...")
        data = extract_text(pdf)

        if "error" not in data:
            # Save full text
            txt_name = pdf.stem + ".txt"
            txt_path = text_folder / txt_name
            txt_path.write_text(data["text"], encoding="utf-8")
            print(f"  -> Saved: extracted_text/{txt_name} ({len(data['text'])} chars)")
        else:
            print(f"  -> Error: {data['error']}")

        summaries.append(create_summary(data))

    # Create summary report
    report = f"""# Document Summaries

Generated from `output/` folder.

**Total documents:** {len(pdfs)}

---
""" + "\n".join(summaries)

    summary_path = BASE_DIR / "document_summaries.md"
    summary_path.write_text(report, encoding="utf-8")
    print(f"\n{'=' * 60}")
    print(f"Summary report saved to: {summary_path}")
    print(f"Extracted text saved to: {text_folder}/")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
