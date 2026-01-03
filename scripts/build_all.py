"""
Build All - Main Orchestration Script for PhD Research Pages

Coordinates all generation tasks:
1. Parse LaTeX documents for metadata
2. Collect and copy research images
3. Generate JSON data files
4. Generate HTML pages

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)

Usage:
    python build_all.py              # Full build
    python build_all.py --dry-run    # Preview without writing files
    python build_all.py --skip-images # Skip image copying
    python build_all.py --verbose    # Enable debug logging
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Ensure scripts directory is in path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from config import (
    SOURCE_REPO,
    TARGET_REPO,
    DATA_DEST,
    IMAGES_DEST,
    RESEARCH_STREAMS,
    EXCLUDED_TEX_FILES,
    get_generation_metadata
)
from latex_parser import (
    parse_latex_document,
    parse_multiple_documents,
    ParsedDocument
)
from image_handler import (
    collect_research_images,
    copy_images_to_target,
    generate_image_report,
    ImageCollection
)
from data_generator import (
    generate_research_data,
    generate_file_catalog,
    generate_thesis_data,
    generate_collaborators_data,
    generate_images_data
)
from html_generator import HTMLGenerator

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the build process."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)

    # Also configure module loggers
    for module in ['config', 'latex_parser', 'image_handler', 'data_generator', 'html_generator']:
        logging.getLogger(module).setLevel(level)

    return logging.getLogger(__name__)

# =============================================================================
# LATEX DOCUMENT DISCOVERY
# =============================================================================

def discover_latex_files(source_path: Path) -> List[Path]:
    """
    Discover LaTeX files for processing.

    Returns main paper documents suitable for the research showcase.
    """
    tex_files = []

    # Known main paper files to include (exact matches take priority)
    priority_papers = [
        'Market_Participants_Classification.tex',
        'UFT-HFT_Market_Impact.tex',
        'TBD.tex',
        'manuscript-EPIA2025.tex',
        'FIN-manuscript.tex',
        'main.tex',
        'manuscript.tex',
    ]

    for tex_path in source_path.rglob('*.tex'):
        path_str = str(tex_path).lower()
        filename = tex_path.name

        # Skip excluded tex files (thesis_outline.tex, etc.)
        if filename in EXCLUDED_TEX_FILES:
            continue

        # Skip archived files
        if 'archive' in path_str:
            continue

        # Skip templates and examples folders
        if 'template' in path_str or 'example' in path_str:
            continue

        # Include priority papers
        if filename in priority_papers:
            tex_files.append(tex_path)
            continue

        # Skip presentation/slides files
        if any(x in path_str for x in ['slide', 'pres', 'poster', 'beamer']):
            continue

        # Skip outline/notes files
        if any(x in filename.lower() for x in ['outline', 'notes', 'comment', 'cover', 'review', 'feedback']):
            continue

        # Include files that are likely papers (>5KB of content)
        try:
            if tex_path.stat().st_size > 5000:
                tex_files.append(tex_path)
        except OSError:
            continue

    return tex_files

# =============================================================================
# BUILD STEPS
# =============================================================================

def step_parse_documents(
    tex_files: List[Path],
    logger: logging.Logger
) -> List[ParsedDocument]:
    """Step 1: Parse all LaTeX documents."""
    logger.info("=" * 60)
    logger.info("STEP 1: Parsing LaTeX Documents")
    logger.info("=" * 60)

    documents = []
    success_count = 0

    for tex_path in tex_files:
        try:
            doc = parse_latex_document(tex_path)
            documents.append(doc)

            if doc.title:
                logger.info(f"  [OK] {tex_path.name}: {doc.title[:50]}...")
                success_count += 1
            else:
                logger.warning(f"  [--] {tex_path.name}: No title found")

        except Exception as e:
            logger.error(f"  [XX] {tex_path.name}: {e}")

    logger.info(f"Parsed {success_count}/{len(tex_files)} documents with titles")

    return documents

def step_collect_images(
    logger: logging.Logger,
    skip_copy: bool = False,
    dry_run: bool = False
) -> ImageCollection:
    """Step 2: Collect and optionally copy images."""
    logger.info("=" * 60)
    logger.info("STEP 2: Collecting Research Images")
    logger.info("=" * 60)

    # Collect images from source
    collection = collect_research_images(
        source_base=SOURCE_REPO,
        include_archives=False,
        include_logos=True
    )

    # Report collection
    logger.info(f"Found {len(collection.images)} unique images")
    logger.info(f"Total size: {collection.total_size_mb:.2f} MB")

    for stream, images in collection.by_stream.items():
        logger.info(f"  {stream}: {len(images)} images")

    # Copy images if not skipped
    if not skip_copy:
        if dry_run:
            logger.info("[DRY RUN] Would copy images to: %s", IMAGES_DEST)
        else:
            logger.info(f"Copying images to: {IMAGES_DEST}")
            copy_images_to_target(
                collection,
                target_dir=IMAGES_DEST,
                organize_by_stream=True,
                dry_run=False
            )
    else:
        logger.info("Skipping image copy (--skip-images)")

    return collection

def step_generate_data(
    documents: List[ParsedDocument],
    image_collection: ImageCollection,
    logger: logging.Logger,
    dry_run: bool = False
) -> dict:
    """Step 3: Generate JSON data files."""
    logger.info("=" * 60)
    logger.info("STEP 3: Generating JSON Data Files")
    logger.info("=" * 60)

    if dry_run:
        logger.info("[DRY RUN] Would generate data files in: %s", DATA_DEST)
        return {}

    # Ensure output directory exists
    DATA_DEST.mkdir(parents=True, exist_ok=True)

    outputs = {}

    # Generate research data
    logger.info("Generating research.json...")
    research_path = DATA_DEST / "research.json"
    research_data = generate_research_data(documents, research_path)
    outputs['research'] = research_data
    logger.info(f"  -> {research_path.name}: {research_data['paper_count']} papers")

    # Generate file catalog
    logger.info("Generating file_catalog.json...")
    catalog_path = DATA_DEST / "file_catalog.json"
    catalog_data = generate_file_catalog(SOURCE_REPO, catalog_path)
    outputs['catalog'] = catalog_data
    logger.info(f"  -> {catalog_path.name}: {catalog_data['summary']['total_files']} files")

    # Generate thesis data
    logger.info("Generating thesis.json...")
    thesis_path = DATA_DEST / "thesis.json"
    thesis_data = generate_thesis_data(thesis_path)
    outputs['thesis'] = thesis_data
    logger.info(f"  -> {thesis_path.name}: {thesis_data['chapter_count']} chapters")

    # Generate collaborators data
    logger.info("Generating collaborators.json...")
    collab_path = DATA_DEST / "collaborators.json"
    collab_data = generate_collaborators_data(collab_path)
    outputs['collaborators'] = collab_data
    logger.info(f"  -> {collab_path.name}: {collab_data['count']} collaborators")

    # Generate images data
    logger.info("Generating images.json...")
    images_path = DATA_DEST / "images.json"
    images_data = generate_images_data(image_collection, images_path)
    outputs['images'] = images_data
    logger.info(f"  -> {images_path.name}: {images_data['total_images']} images")

    return outputs

def step_generate_html(
    data: dict,
    logger: logging.Logger,
    dry_run: bool = False
) -> List[Path]:
    """Step 4: Generate HTML pages."""
    logger.info("=" * 60)
    logger.info("STEP 4: Generating HTML Pages")
    logger.info("=" * 60)

    if dry_run:
        logger.info("[DRY RUN] Would generate HTML pages in: %s", TARGET_REPO)
        return []

    # Create HTML generator
    generator = HTMLGenerator(target_dir=TARGET_REPO)

    # Generate all pages
    generated_pages = generator.generate_all_pages(
        research_data=data.get('research', {}),
        catalog_data=data.get('catalog', {}),
        image_data=data.get('images', {}),
        dry_run=False
    )

    for page_name, page_path in generated_pages.items():
        logger.info(f"  -> {page_path.name}")

    return list(generated_pages.values())

# =============================================================================
# MAIN BUILD
# =============================================================================

def build_all(
    dry_run: bool = False,
    skip_images: bool = False,
    verbose: bool = False
) -> bool:
    """
    Execute the complete build process.

    Args:
        dry_run: If True, preview without writing files
        skip_images: If True, skip image copying
        verbose: If True, enable debug logging

    Returns:
        True if build succeeded, False otherwise
    """
    start_time = datetime.now()

    # Setup logging
    logger = setup_logging(verbose)

    logger.info("=" * 60)
    logger.info("PhD RESEARCH PAGES GENERATOR")
    logger.info("=" * 60)
    logger.info(f"Source: {SOURCE_REPO}")
    logger.info(f"Target: {TARGET_REPO}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("")

    # Validate paths
    if not SOURCE_REPO.exists():
        logger.error(f"Source repository not found: {SOURCE_REPO}")
        return False

    if not TARGET_REPO.exists():
        logger.error(f"Target repository not found: {TARGET_REPO}")
        return False

    try:
        # Step 1: Discover and parse LaTeX documents
        tex_files = discover_latex_files(SOURCE_REPO)
        logger.info(f"Discovered {len(tex_files)} LaTeX documents")

        documents = step_parse_documents(tex_files, logger)

        # Step 2: Collect images
        image_collection = step_collect_images(
            logger,
            skip_copy=skip_images,
            dry_run=dry_run
        )

        # Step 3: Generate data files
        data = step_generate_data(
            documents,
            image_collection,
            logger,
            dry_run=dry_run
        )

        # Step 4: Generate HTML pages
        generated_pages = step_generate_html(
            data,
            logger,
            dry_run=dry_run
        )

        # Summary
        duration = datetime.now() - start_time

        logger.info("")
        logger.info("=" * 60)
        logger.info("BUILD COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration.total_seconds():.2f} seconds")
        logger.info(f"Documents parsed: {len(documents)}")
        logger.info(f"Images collected: {len(image_collection.images)}")
        logger.info(f"Data files generated: {len(data)}")
        logger.info(f"HTML pages generated: {len(generated_pages)}")

        if not dry_run:
            logger.info("")
            logger.info("Generated pages:")
            for page in generated_pages:
                logger.info(f"  - {page.relative_to(TARGET_REPO)}")

        return True

    except Exception as e:
        logger.error(f"Build failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface for build script."""
    parser = argparse.ArgumentParser(
        description="Generate PhD Research Pages for GitHub Pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build_all.py                 # Full build
    python build_all.py --dry-run       # Preview without writing
    python build_all.py --skip-images   # Skip image copying
    python build_all.py -v              # Verbose output
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview build without writing files'
    )

    parser.add_argument(
        '--skip-images',
        action='store_true',
        help='Skip copying images (faster rebuild)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose/debug logging'
    )

    args = parser.parse_args()

    success = build_all(
        dry_run=args.dry_run,
        skip_images=args.skip_images,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
