"""
Data Generator for Research Pages

Creates JSON data files for dynamic page content from parsed
LaTeX documents and file inventory.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict
import logging

from config import (
    SOURCE_REPO,
    DATA_DEST,
    RESEARCH_STREAMS,
    KNOWN_PAPERS,
    THESIS_CHAPTERS,
    COLLABORATORS,
    STATUS_CONFIG,
    EXCLUDED_TEX_FILES,
    EXCLUDED_CATALOG_FILES,
    get_generation_metadata,
    get_paper_override,
    get_stream_by_path
)
from latex_parser import (
    ParsedDocument,
    parse_latex_document,
    get_authors_string,
    get_section_outline
)
from image_handler import ImageCollection, ImageInfo, generate_image_report

logger = logging.getLogger(__name__)

# =============================================================================
# DATA TRANSFORMATION
# =============================================================================

def document_to_dict(doc: ParsedDocument, override: Optional[dict] = None) -> Dict:
    """
    Convert ParsedDocument to dictionary for JSON serialization.

    Args:
        doc: Parsed LaTeX document
        override: Optional manual override values

    Returns:
        Dictionary representation
    """
    # Determine stream
    stream = get_stream_by_path(doc.filepath)
    if override and 'stream' in override:
        stream = override['stream']

    # Get status
    status = "IN_PROGRESS"
    if override and 'status' in override:
        status = override['status']

    # Get venue
    venue = ""
    if override and 'venue' in override:
        venue = override['venue']

    # Get work package
    work_package = ""
    if override and 'work_package' in override:
        work_package = override['work_package']

    # Get title - prefer override, then parsed, then filename
    title = doc.title
    if override and 'title' in override:
        title = override['title']
    if not title:
        title = doc.filepath.stem.replace('_', ' ').title()

    # Build author list
    authors = []
    for author in doc.authors:
        authors.append({
            'name': author.name,
            'affiliations': author.affiliations,
            'email': author.email
        })

    # Build sections outline
    outline = get_section_outline(doc.sections, max_depth=2)

    # Get publication URLs
    ssrn_url = override.get('ssrn_url', '') if override else ''
    arxiv_url = override.get('arxiv_url', '') if override else ''
    doi = override.get('doi', '') if override else ''

    return {
        'id': doc.filepath.stem,
        'filename': doc.filepath.name,
        'filepath': str(doc.filepath.relative_to(SOURCE_REPO)),
        'title': title,
        'authors': authors,
        'authors_string': get_authors_string(doc.authors),
        'abstract': doc.abstract or "",
        'abstract_short': (doc.abstract[:200] + "...") if doc.abstract and len(doc.abstract) > 200 else (doc.abstract or ""),
        'keywords': doc.keywords,
        'sections': outline,
        'figures': doc.figures,
        'has_bibliography': doc.has_bibliography,
        'document_class': doc.document_class,
        'status': status,
        'status_label': STATUS_CONFIG.get(status, {}).get('label', status),
        'venue': venue,
        'work_package': work_package,
        'stream': stream or 'other',
        'year': override.get('year', datetime.now().year) if override else datetime.now().year,
        'ssrn_url': ssrn_url,
        'arxiv_url': arxiv_url,
        'doi': doi
    }

def file_to_catalog_entry(filepath: Path, base_path: Path) -> Dict:
    """
    Convert a file path to a catalog entry.

    Args:
        filepath: Path to the file
        base_path: Base path for relative path calculation

    Returns:
        Dictionary with file metadata
    """
    stat = filepath.stat()

    # Determine category
    ext = filepath.suffix.lower()
    if ext == '.tex':
        file_type = 'LaTeX Document'
    elif ext == '.bib':
        file_type = 'Bibliography'
    elif ext == '.png':
        file_type = 'Image'
    elif ext == '.pdf':
        file_type = 'PDF Document'
    elif ext in ['.bst', '.cls']:
        file_type = 'Style File'
    else:
        file_type = 'Other'

    # Determine research stream
    stream = get_stream_by_path(filepath) or 'other'

    # Determine document category
    path_lower = str(filepath).lower()
    if 'archive' in path_lower:
        doc_category = 'Archive'
    elif 'template' in path_lower:
        doc_category = 'Template'
    elif 'example' in path_lower:
        doc_category = 'Example'
    elif 'logo' in path_lower:
        doc_category = 'Asset'
    else:
        doc_category = 'Active'

    return {
        'filename': filepath.name,
        'path': str(filepath.relative_to(base_path)),
        'extension': ext,
        'size_kb': round(stat.st_size / 1024, 2),
        'file_type': file_type,
        'research_stream': stream,
        'document_category': doc_category,
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
    }

# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_research_data(
    parsed_documents: List[ParsedDocument],
    output_path: Path = DATA_DEST / "research.json"
) -> Dict:
    """
    Generate research.json with all paper metadata.

    Args:
        parsed_documents: List of parsed LaTeX documents
        output_path: Path to write JSON file

    Returns:
        Generated data dictionary
    """
    papers = []

    for doc in parsed_documents:
        # Check for manual override
        override = get_paper_override(doc.filepath.name)

        paper_dict = document_to_dict(doc, override)
        papers.append(paper_dict)

    # Organize by stream
    by_stream = {}
    for paper in papers:
        stream = paper['stream']
        if stream not in by_stream:
            by_stream[stream] = []
        by_stream[stream].append(paper)

    # Organize by status
    by_status = {}
    for paper in papers:
        status = paper['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(paper)

    # Build data structure
    data = {
        **get_generation_metadata(),
        'paper_count': len(papers),
        'papers': papers,
        'by_stream': by_stream,
        'by_status': by_status,
        'streams_summary': {
            stream: {
                'name': RESEARCH_STREAMS[stream].name if stream in RESEARCH_STREAMS else stream,
                'count': len(stream_papers),
                'description': RESEARCH_STREAMS[stream].description if stream in RESEARCH_STREAMS else ""
            }
            for stream, stream_papers in by_stream.items()
        },
        'status_summary': {
            status: len(status_papers)
            for status, status_papers in by_status.items()
        }
    }

    # Write to file with explicit UTF-8 encoding
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    logger.info(f"Generated research.json with {len(papers)} papers")

    return data

def generate_file_catalog(
    source_path: Path = SOURCE_REPO,
    output_path: Path = DATA_DEST / "file_catalog.json",
    include_archives: bool = False
) -> Dict:
    """
    Generate file_catalog.json with complete file inventory.

    Args:
        source_path: Base path to scan
        output_path: Path to write JSON file
        include_archives: Whether to include archive folders

    Returns:
        Generated catalog dictionary
    """
    files = []
    seen_filenames = set()  # Track seen filenames to avoid duplicates
    summary = {
        'tex_files': 0,
        'bib_files': 0,
        'png_files': 0,
        'pdf_files': 0,
        'other_files': 0,
        'total_size_mb': 0.0
    }

    # Scan all files
    for filepath in source_path.rglob('*'):
        if not filepath.is_file():
            continue

        # Skip archives if not requested
        if not include_archives and 'archive' in str(filepath).lower():
            continue

        # Skip hidden files
        if filepath.name.startswith('.'):
            continue

        # Skip excluded files from catalog
        if any(excl in filepath.name for excl in EXCLUDED_CATALOG_FILES):
            continue

        # Skip .claude directories
        if '.claude' in str(filepath):
            continue

        # Skip duplicate PDFs (same filename from different directories)
        if filepath.suffix.lower() == '.pdf':
            if filepath.name in seen_filenames:
                continue
            seen_filenames.add(filepath.name)

        try:
            entry = file_to_catalog_entry(filepath, source_path)
            files.append(entry)

            # Update summary
            ext = filepath.suffix.lower()
            if ext == '.tex':
                summary['tex_files'] += 1
            elif ext == '.bib':
                summary['bib_files'] += 1
            elif ext == '.png':
                summary['png_files'] += 1
            elif ext == '.pdf':
                summary['pdf_files'] += 1
            else:
                summary['other_files'] += 1

            summary['total_size_mb'] += entry['size_kb'] / 1024

        except Exception as e:
            logger.warning(f"Failed to process {filepath}: {e}")

    summary['total_size_mb'] = round(summary['total_size_mb'], 2)
    summary['total_files'] = len(files)

    # Organize by extension
    by_extension = {}
    for entry in files:
        ext = entry['extension']
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(entry)

    # Organize by stream
    by_stream = {}
    for entry in files:
        stream = entry['research_stream']
        if stream not in by_stream:
            by_stream[stream] = []
        by_stream[stream].append(entry)

    # Build catalog
    catalog = {
        **get_generation_metadata(),
        'summary': summary,
        'files': files,
        'by_extension': {ext: len(items) for ext, items in by_extension.items()},
        'by_stream': {stream: len(items) for stream, items in by_stream.items()},
        'by_category': {}
    }

    # Count by document category
    for entry in files:
        cat = entry['document_category']
        if cat not in catalog['by_category']:
            catalog['by_category'][cat] = 0
        catalog['by_category'][cat] += 1

    # Write to file with explicit UTF-8 encoding
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, default=str, ensure_ascii=False)

    logger.info(f"Generated file_catalog.json with {len(files)} files")

    return catalog

def generate_thesis_data(output_path: Path = DATA_DEST / "thesis.json") -> Dict:
    """
    Generate thesis.json with chapter structure.

    Args:
        output_path: Path to write JSON file

    Returns:
        Generated thesis data
    """
    # Enhance chapter data with status colors
    chapters = []
    for chapter in THESIS_CHAPTERS:
        status = chapter['status']
        status_config = STATUS_CONFIG.get(status, STATUS_CONFIG['IN_PROGRESS'])

        chapters.append({
            **chapter,
            'status_label': status_config['label'],
            'status_color': status_config['color'],
            'status_text_color': status_config['text_color']
        })

    data = {
        **get_generation_metadata(),
        'title': "Modeling Narrative Dynamics for Volatility Regime Detection in Financial Markets",
        'author': "Gabin Taibi",
        'supervisors': ["Prof. Dr. Joerg Osterrieder"],
        'institutions': [
            "University of Twente",
            "Bern University of Applied Sciences"
        ],
        'grant': "SNSF IZCOZ0_213370",
        'chapters': chapters,
        'chapter_count': len(chapters),
        'completed_count': sum(1 for c in chapters if c['status'] == 'PUBLISHED'),
        'in_progress_count': sum(1 for c in chapters if c['status'] in ['IN_PROGRESS', 'UNDER_REVIEW', 'SUBMITTED'])
    }

    # Write to file with explicit UTF-8 encoding
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    logger.info("Generated thesis.json")

    return data

def generate_collaborators_data(output_path: Path = DATA_DEST / "collaborators.json") -> Dict:
    """
    Generate collaborators.json with team information.

    Args:
        output_path: Path to write JSON file

    Returns:
        Generated collaborators data
    """
    data = {
        **get_generation_metadata(),
        'collaborators': COLLABORATORS,
        'count': len(COLLABORATORS),
        'institutions': list(set(
            affil
            for collab in COLLABORATORS
            for affil in collab['affiliations']
        ))
    }

    # Write to file with explicit UTF-8 encoding
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    logger.info("Generated collaborators.json")

    return data

def generate_images_data(
    collection: ImageCollection,
    output_path: Path = DATA_DEST / "images.json"
) -> Dict:
    """
    Generate images.json with image metadata.

    Args:
        collection: Collected images
        output_path: Path to write JSON file

    Returns:
        Generated images data
    """
    images = []
    for img in collection.images:
        images.append({
            'filename': img.filename,
            'category': img.category,
            'stream': img.research_stream,
            'size_kb': round(img.size_kb, 2),
            'web_path': f"images/research/{img.research_stream}/{img.filename}" if img.dest_path else None
        })

    report = generate_image_report(collection)

    data = {
        **get_generation_metadata(),
        **report,
        'images': images
    }

    # Write to file with explicit UTF-8 encoding
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    logger.info(f"Generated images.json with {len(images)} images")

    return data

# =============================================================================
# COMBINED GENERATION
# =============================================================================

def generate_all_data(
    parsed_documents: List[ParsedDocument],
    image_collection: Optional[ImageCollection] = None,
    output_dir: Path = DATA_DEST
) -> Dict[str, Path]:
    """
    Generate all JSON data files.

    Args:
        parsed_documents: List of parsed LaTeX documents
        image_collection: Optional collected images
        output_dir: Output directory

    Returns:
        Dictionary mapping data type to output path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {}

    # Research data
    research_path = output_dir / "research.json"
    generate_research_data(parsed_documents, research_path)
    outputs['research'] = research_path

    # File catalog
    catalog_path = output_dir / "file_catalog.json"
    generate_file_catalog(SOURCE_REPO, catalog_path)
    outputs['catalog'] = catalog_path

    # Thesis data
    thesis_path = output_dir / "thesis.json"
    generate_thesis_data(thesis_path)
    outputs['thesis'] = thesis_path

    # Collaborators data
    collab_path = output_dir / "collaborators.json"
    generate_collaborators_data(collab_path)
    outputs['collaborators'] = collab_path

    # Images data (if provided)
    if image_collection:
        images_path = output_dir / "images.json"
        generate_images_data(image_collection, images_path)
        outputs['images'] = images_path

    logger.info(f"Generated {len(outputs)} data files in {output_dir}")

    return outputs

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test data generation
    print("Testing data generation...")

    # Generate thesis data
    thesis_data = generate_thesis_data()
    print(f"Thesis chapters: {thesis_data['chapter_count']}")

    # Generate collaborators data
    collab_data = generate_collaborators_data()
    print(f"Collaborators: {collab_data['count']}")

    # Generate file catalog
    catalog_data = generate_file_catalog()
    print(f"Files cataloged: {catalog_data['summary']['total_files']}")
