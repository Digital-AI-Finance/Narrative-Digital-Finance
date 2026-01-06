"""
LaTeX Document Parser for Research Metadata Extraction

Extracts titles, authors, abstracts, keywords, and section structure
from LaTeX documents for HTML page generation.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ParsedAuthor:
    """Parsed author information."""
    name: str
    affiliations: List[str] = field(default_factory=list)
    email: Optional[str] = None

@dataclass
class ParsedSection:
    """Parsed section information."""
    level: str  # section, subsection, subsubsection
    title: str
    is_starred: bool = False

@dataclass
class ParsedDocument:
    """Complete parsed LaTeX document."""
    filepath: Path
    title: Optional[str] = None
    authors: List[ParsedAuthor] = field(default_factory=list)
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    sections: List[ParsedSection] = field(default_factory=list)
    figures: List[str] = field(default_factory=list)
    has_bibliography: bool = False
    document_class: Optional[str] = None
    raw_content: str = ""

# =============================================================================
# TEXT CLEANING
# =============================================================================

def clean_latex_text(text: str) -> str:
    """
    Remove LaTeX commands and clean text for HTML display.

    Args:
        text: Raw LaTeX text

    Returns:
        Cleaned plain text
    """
    if not text:
        return ""

    # Remove comments (lines starting with %)
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)

    # Remove author correspondence markers (e.g., {cor1}, \corref{cor1}, $^{1}$, $^{1,2}$)
    text = re.sub(r'\{cor\d+\}', '', text)
    text = re.sub(r'\\corref\{[^}]*\}', '', text)
    text = re.sub(r'\$\^\{[^}]*\}\$?', '', text)
    text = re.sub(r'\$\^[0-9,]+\$?', '', text)
    text = re.sub(r'\^\{[^}]*\}', '', text)

    # Remove affiliation markers like [1], [1,2]
    text = re.sub(r'\[[\d,\s]+\]', '', text)

    # Remove common formatting commands
    formatting_patterns = [
        (r'\\textbf\{([^}]+)\}', r'\1'),
        (r'\\textit\{([^}]+)\}', r'\1'),
        (r'\\emph\{([^}]+)\}', r'\1'),
        (r'\\underline\{([^}]+)\}', r'\1'),
        (r'\\textrm\{([^}]+)\}', r'\1'),
        (r'\\textsf\{([^}]+)\}', r'\1'),
        (r'\\texttt\{([^}]+)\}', r'\1'),
        (r'\\textsc\{([^}]+)\}', r'\1'),
    ]

    for pattern, replacement in formatting_patterns:
        text = re.sub(pattern, replacement, text)

    # Remove citation commands
    citation_patterns = [
        r'\\cite\{[^}]+\}',
        r'\\citep\{[^}]+\}',
        r'\\citet\{[^}]+\}',
        r'\\textcite\{[^}]+\}',
        r'\\parencite\{[^}]+\}',
        r'\\autocite\{[^}]+\}',
    ]

    for pattern in citation_patterns:
        text = re.sub(pattern, '', text)

    # Remove footnotes
    text = re.sub(r'\\footnote\{[^}]*\}', '', text)

    # Remove URLs but keep the text
    text = re.sub(r'\\url\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]+\}\{([^}]+)\}', r'\1', text)

    # Remove math mode markers
    text = re.sub(r'\$([^$]+)\$', r'\1', text)
    text = re.sub(r'\\\(([^)]+)\\\)', r'\1', text)
    text = re.sub(r'\\\[([^\]]+)\\\]', r'\1', text)

    # Remove remaining LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?', '', text)

    # Clean special characters
    special_chars = [
        (r'\\&', '&'),
        (r'\\%', '%'),
        (r'\\#', '#'),
        (r'\\_', '_'),
        (r'\\{', '{'),
        (r'\\}', '}'),
        (r'\\~', '~'),
        (r'\\^', '^'),
        (r"``", '"'),
        (r"''", '"'),
        (r"`", "'"),
    ]

    for pattern, replacement in special_chars:
        text = text.replace(pattern, replacement)

    # Final cleanup - remove any remaining LaTeX artifacts
    # Remove any remaining corref/affiliation markers that may have been left behind
    text = re.sub(r'\{cor\d*\}?', '', text)  # {cor1}, {cor1 (without closing brace), {cor}, etc.
    text = re.sub(r'\{cor\d*,?', '', text)  # {cor1, at end of names
    text = re.sub(r'\{[0-9,\s]+\}', '', text)  # {1}, {1,2}, etc.
    text = re.sub(r'\$\^[\{\}0-9,\s]+\$?', '', text)  # $^{1}$, $^1$, etc.
    text = re.sub(r'\^\{[^}]*\}', '', text)  # ^{1}, ^{1,2}, etc.
    text = re.sub(r'\s+and\s+\d+$', '', text)  # trailing "and 2" from "$^{1 and 2"
    text = re.sub(r'\band\s+\d+$', '', text)  # standalone "and 2" at end

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================

def extract_document_class(content: str) -> Optional[str]:
    """Extract document class."""
    match = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', content)
    return match.group(1) if match else None

def extract_title(content: str) -> Optional[str]:
    """
    Extract title from LaTeX document.

    Handles:
    - \\title{...}
    - \\title[short]{full title}
    - Multi-line titles with nested braces
    """
    # Try simple title first
    patterns = [
        r'\\title\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
        r'\\title\[[^\]]*\]\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            title = clean_latex_text(match.group(1))
            if title and len(title) > 5:  # Avoid empty or very short titles
                return title

    return None

def extract_authors_elsarticle(content: str) -> List[ParsedAuthor]:
    """
    Extract authors from elsarticle format.

    Handles:
    - \\author[affil]{name}
    - \\address[num]{affiliation}
    - \\ead{email}
    """
    authors = []

    # Extract affiliations first
    affiliations = {}
    address_pattern = r'\\address\[([^\]]+)\]\{([^}]+)\}'
    for match in re.finditer(address_pattern, content):
        affil_key = match.group(1).strip()
        affil_text = clean_latex_text(match.group(2))
        affiliations[affil_key] = affil_text

    # Extract authors
    author_pattern = r'\\author\[([^\]]*)\]\{([^}]+)\}'
    email_pattern = r'\\ead\{([^}]+)\}'

    for match in re.finditer(author_pattern, content):
        affil_keys = [k.strip() for k in match.group(1).split(',')]
        name = clean_latex_text(match.group(2))

        # Remove corref markers
        name = re.sub(r'\\corref\{[^}]*\}', '', name).strip()

        author_affils = [affiliations.get(k, '') for k in affil_keys if k in affiliations]

        authors.append(ParsedAuthor(
            name=name,
            affiliations=author_affils
        ))

    # Try to match emails to authors
    emails = re.findall(email_pattern, content)
    for i, email in enumerate(emails):
        if i < len(authors):
            authors[i].email = email.strip()

    return authors

def extract_authors_authblk(content: str) -> List[ParsedAuthor]:
    """
    Extract authors from authblk format.

    Handles:
    - \\author[affil]{name}
    - \\affil[num]{affiliation}
    """
    authors = []

    # Extract affiliations
    affiliations = {}
    affil_pattern = r'\\affil\[([^\]]+)\]\{([^}]+)\}'
    for match in re.finditer(affil_pattern, content):
        affil_key = match.group(1).strip()
        affil_text = clean_latex_text(match.group(2))
        affiliations[affil_key] = affil_text

    # Extract authors
    author_pattern = r'\\author\[([^\]]*)\]\{([^}]+)\}'
    for match in re.finditer(author_pattern, content):
        affil_keys = [k.strip() for k in match.group(1).split(',')]
        name = clean_latex_text(match.group(2))

        author_affils = [affiliations.get(k, '') for k in affil_keys if k in affiliations]

        authors.append(ParsedAuthor(
            name=name,
            affiliations=author_affils
        ))

    return authors

def extract_authors_simple(content: str) -> List[ParsedAuthor]:
    """
    Extract authors from simple \\author{} format.

    Handles:
    - \\author{Name1 and Name2}
    - \\author{Name1, Name2, Name3}
    """
    match = re.search(r'\\author\{([^}]+)\}', content)
    if not match:
        return []

    author_text = clean_latex_text(match.group(1))

    # Split by 'and' or comma
    if ' and ' in author_text:
        names = [n.strip() for n in author_text.split(' and ')]
    else:
        names = [n.strip() for n in author_text.split(',')]

    return [ParsedAuthor(name=name) for name in names if name]

def extract_authors(content: str) -> List[ParsedAuthor]:
    """
    Extract authors using the appropriate method.
    """
    # Try elsarticle format first
    authors = extract_authors_elsarticle(content)
    if authors:
        return authors

    # Try authblk format
    authors = extract_authors_authblk(content)
    if authors:
        return authors

    # Fall back to simple format
    return extract_authors_simple(content)

def extract_abstract(content: str) -> Optional[str]:
    """
    Extract abstract content.
    """
    pattern = r'\\begin\{abstract\}(.*?)\\end\{abstract\}'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        abstract = clean_latex_text(match.group(1))
        # Ensure minimum length
        if len(abstract) > 50:
            return abstract

    return None

def extract_keywords(content: str) -> List[str]:
    """
    Extract keywords from various formats.
    """
    patterns = [
        r'\\keywords\{([^}]+)\}',
        r'\\begin\{keyword\}(.*?)\\end\{keyword\}',
        r'\\begin\{keywords\}(.*?)\\end\{keywords\}',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            raw = match.group(1)

            # Handle \sep delimiter
            if '\\sep' in raw:
                keywords = [clean_latex_text(k) for k in raw.split('\\sep')]
            # Handle comma delimiter
            elif ',' in raw:
                keywords = [clean_latex_text(k) for k in raw.split(',')]
            else:
                keywords = [clean_latex_text(raw)]

            # Filter empty keywords
            return [k for k in keywords if k and len(k) > 1]

    return []

def extract_sections(content: str) -> List[ParsedSection]:
    """
    Extract section structure for outline.
    """
    sections = []
    pattern = r'\\(section|subsection|subsubsection)(\*?)\{([^}]+)\}'

    for match in re.finditer(pattern, content):
        level = match.group(1)
        is_starred = bool(match.group(2))
        title = clean_latex_text(match.group(3))

        if title:
            sections.append(ParsedSection(
                level=level,
                title=title,
                is_starred=is_starred
            ))

    return sections

def extract_figures(content: str) -> List[str]:
    """
    Find all referenced image files.
    """
    pattern = r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}'
    figures = []

    for match in re.finditer(pattern, content):
        fig_path = match.group(1)

        # Normalize path - add extension if missing
        if not any(fig_path.endswith(ext) for ext in ['.png', '.pdf', '.jpg', '.jpeg', '.eps']):
            fig_path += '.png'

        figures.append(fig_path)

    return figures

def has_bibliography(content: str) -> bool:
    """
    Check if document has bibliography.
    """
    patterns = [
        r'\\bibliography\{',
        r'\\addbibresource\{',
        r'\\printbibliography',
    ]

    return any(re.search(p, content) for p in patterns)

# =============================================================================
# MAIN PARSER
# =============================================================================

def parse_latex_document(filepath: Path) -> ParsedDocument:
    """
    Parse a LaTeX document and extract all metadata.

    Args:
        filepath: Path to the .tex file

    Returns:
        ParsedDocument with extracted metadata
    """
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Failed to read {filepath}: {e}")
        return ParsedDocument(filepath=filepath)

    doc = ParsedDocument(
        filepath=filepath,
        raw_content=content,
        document_class=extract_document_class(content),
        title=extract_title(content),
        authors=extract_authors(content),
        abstract=extract_abstract(content),
        keywords=extract_keywords(content),
        sections=extract_sections(content),
        figures=extract_figures(content),
        has_bibliography=has_bibliography(content)
    )

    return doc

def parse_multiple_documents(filepaths: List[Path]) -> List[ParsedDocument]:
    """
    Parse multiple LaTeX documents.

    Args:
        filepaths: List of paths to .tex files

    Returns:
        List of ParsedDocument objects
    """
    documents = []

    for filepath in filepaths:
        try:
            doc = parse_latex_document(filepath)
            documents.append(doc)
            logger.info(f"Parsed: {filepath.name} - Title: {doc.title[:50] if doc.title else 'None'}...")
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")

    return documents

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_authors_string(authors: List[ParsedAuthor], separator: str = ", ") -> str:
    """
    Format authors list as a string.
    """
    if not authors:
        return ""

    names = [a.name for a in authors]

    if len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        return separator.join(names[:-1]) + f", and {names[-1]}"

def get_section_outline(sections: List[ParsedSection], max_depth: int = 2) -> List[dict]:
    """
    Convert sections to a hierarchical outline.
    """
    depth_map = {'section': 1, 'subsection': 2, 'subsubsection': 3}

    outline = []
    for section in sections:
        depth = depth_map.get(section.level, 1)
        if depth <= max_depth:
            outline.append({
                'level': depth,
                'title': section.title
            })

    return outline

# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    # Test with a sample file
    import sys

    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
        if test_path.exists():
            doc = parse_latex_document(test_path)
            print(f"Title: {doc.title}")
            print(f"Authors: {get_authors_string(doc.authors)}")
            print(f"Abstract: {doc.abstract[:200] if doc.abstract else 'None'}...")
            print(f"Keywords: {doc.keywords}")
            print(f"Sections: {len(doc.sections)}")
            print(f"Figures: {doc.figures}")
