"""
Image Handler for Research Pages

Collects, categorizes, and copies research images (PNGs)
from the source repository to the target GitHub Pages site.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging
import hashlib

from config import (
    SOURCE_REPO,
    IMAGES_DEST,
    IMAGE_CATEGORIES,
    get_stream_by_path,
    categorize_image
)

logger = logging.getLogger(__name__)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ImageInfo:
    """Information about a research image."""
    source_path: Path
    filename: str
    extension: str
    size_kb: float
    category: str
    research_stream: str
    relative_path: Path
    dest_path: Optional[Path] = None
    hash: Optional[str] = None

@dataclass
class ImageCollection:
    """Collection of images organized by stream and category."""
    images: List[ImageInfo] = field(default_factory=list)
    by_stream: Dict[str, List[ImageInfo]] = field(default_factory=dict)
    by_category: Dict[str, List[ImageInfo]] = field(default_factory=dict)
    total_size_mb: float = 0.0

# =============================================================================
# IMAGE DISCOVERY
# =============================================================================

def is_archive_path(path: Path) -> bool:
    """Check if path is in an archive directory."""
    path_str = str(path).lower()
    archive_indicators = ['archive', 'previous', 'old', 'backup']
    return any(ind in path_str for ind in archive_indicators)

def is_logo(filename: str) -> bool:
    """Check if image is a logo."""
    logo_indicators = ['logo', 'badge', 'icon', 'snsf', 'bfh', 'deutsche']
    name_lower = filename.lower()
    return any(ind in name_lower for ind in logo_indicators)

def get_image_stream(img_path: Path) -> str:
    """Determine research stream from image path."""
    stream = get_stream_by_path(img_path)
    if stream:
        return stream

    # Additional path-based detection
    path_str = str(img_path).lower()

    if 'qualifier' in path_str:
        return 'phd'
    elif 'test_1' in path_str:
        return 'quoniam'

    return 'other'

def get_image_category(filename: str) -> str:
    """Categorize image by filename."""
    name_lower = filename.lower()

    # Check for specific patterns
    if 'regression' in name_lower:
        return 'Regression Analysis'
    elif 'clustering' in name_lower or 'cluster' in name_lower:
        return 'Clustering Analysis'
    elif 'pca' in name_lower:
        return 'Dimensionality Reduction'
    elif 'wordcloud' in name_lower:
        return 'Text Visualization'
    elif is_logo(filename):
        return 'Logo'
    elif 'diagram' in name_lower or 'flow' in name_lower or 'filter' in name_lower:
        return 'Diagram'
    elif 'timeseries' in name_lower or 'time_series' in name_lower:
        return 'Time Series'
    elif 'rolling' in name_lower:
        return 'Rolling Analysis'
    elif 'distribution' in name_lower or 'quantile' in name_lower:
        return 'Distribution Plot'
    elif 'null_hypo' in name_lower or 'hypothesis' in name_lower:
        return 'Statistical Test'
    elif 'narrative' in name_lower:
        return 'Narrative Visualization'
    elif 'participation' in name_lower or 'deep' in name_lower or 'cancelled' in name_lower:
        return 'Market Microstructure'
    elif 'fig_' in name_lower or 'figure' in name_lower:
        return 'Research Figure'

    return 'Analysis Chart'

def compute_file_hash(filepath: Path) -> str:
    """Compute MD5 hash of file for deduplication."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# =============================================================================
# IMAGE COLLECTION
# =============================================================================

def collect_research_images(
    source_base: Path = SOURCE_REPO,
    include_archives: bool = False,
    include_logos: bool = True
) -> ImageCollection:
    """
    Collect all PNG images from research directories.

    Args:
        source_base: Base path to search
        include_archives: Whether to include archived images
        include_logos: Whether to include logo images

    Returns:
        ImageCollection with categorized images
    """
    collection = ImageCollection()
    seen_hashes = set()

    logger.info(f"Scanning for images in {source_base}")

    for img_path in source_base.rglob('*.png'):
        # Skip archives if not requested
        if not include_archives and is_archive_path(img_path):
            continue

        # Skip logos if not requested
        if not include_logos and is_logo(img_path.name):
            continue

        try:
            # Compute hash for deduplication
            file_hash = compute_file_hash(img_path)

            # Skip duplicates
            if file_hash in seen_hashes:
                logger.debug(f"Skipping duplicate: {img_path.name}")
                continue

            seen_hashes.add(file_hash)

            # Get file info
            stat = img_path.stat()
            size_kb = stat.st_size / 1024

            # Categorize
            stream = get_image_stream(img_path)
            category = get_image_category(img_path.name)

            img_info = ImageInfo(
                source_path=img_path,
                filename=img_path.name,
                extension=img_path.suffix.lower(),
                size_kb=size_kb,
                category=category,
                research_stream=stream,
                relative_path=img_path.relative_to(source_base),
                hash=file_hash
            )

            collection.images.append(img_info)
            collection.total_size_mb += size_kb / 1024

            # Organize by stream
            if stream not in collection.by_stream:
                collection.by_stream[stream] = []
            collection.by_stream[stream].append(img_info)

            # Organize by category
            if category not in collection.by_category:
                collection.by_category[category] = []
            collection.by_category[category].append(img_info)

        except Exception as e:
            logger.warning(f"Failed to process {img_path}: {e}")

    logger.info(f"Collected {len(collection.images)} unique images ({collection.total_size_mb:.2f} MB)")

    return collection

# =============================================================================
# IMAGE COPYING
# =============================================================================

def get_stream_folder_name(stream: str) -> str:
    """Get folder name for a research stream."""
    stream_folders = {
        'hft': 'hft',
        'narratives': 'narratives',
        'slr': 'slr',
        'topol': 'topol',
        'quoniam': 'quoniam',
        'phd': 'phd',
        'other': 'other'
    }
    return stream_folders.get(stream, 'other')

def copy_images_to_target(
    collection: ImageCollection,
    target_dir: Path = IMAGES_DEST,
    organize_by_stream: bool = True,
    dry_run: bool = False
) -> Dict[Path, Path]:
    """
    Copy images to target directory, organizing by stream.

    Args:
        collection: ImageCollection to copy
        target_dir: Destination directory
        organize_by_stream: Whether to organize into subdirectories
        dry_run: If True, don't actually copy files

    Returns:
        Dictionary mapping source paths to destination paths
    """
    path_mapping = {}

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    for img in collection.images:
        try:
            # Determine destination path
            if organize_by_stream:
                stream_folder = get_stream_folder_name(img.research_stream)
                dest_dir = target_dir / stream_folder
            else:
                dest_dir = target_dir

            dest_path = dest_dir / img.filename

            # Handle name collisions
            if dest_path.exists() and not dry_run:
                # Check if it's the same file
                existing_hash = compute_file_hash(dest_path)
                if existing_hash == img.hash:
                    # Same file, no need to copy
                    img.dest_path = dest_path
                    path_mapping[img.source_path] = dest_path
                    continue

                # Different file, add suffix
                stem = dest_path.stem
                suffix = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img.source_path, dest_path)

            img.dest_path = dest_path
            path_mapping[img.source_path] = dest_path

            logger.debug(f"Copied: {img.filename} -> {dest_path}")

        except Exception as e:
            logger.warning(f"Failed to copy {img.source_path}: {e}")

    logger.info(f"Copied {len(path_mapping)} images to {target_dir}")

    return path_mapping

# =============================================================================
# IMAGE SELECTION
# =============================================================================

def select_key_images(
    collection: ImageCollection,
    max_per_stream: int = 10,
    max_total: int = 50
) -> List[ImageInfo]:
    """
    Select key images for showcase.

    Prioritizes:
    1. Research figures
    2. Regression analyses
    3. Unique categories

    Args:
        collection: Full image collection
        max_per_stream: Maximum images per stream
        max_total: Maximum total images

    Returns:
        List of selected ImageInfo
    """
    selected = []
    selected_per_stream = {}

    # Priority order for categories
    priority_categories = [
        'Research Figure',
        'Regression Analysis',
        'Time Series',
        'Clustering Analysis',
        'Dimensionality Reduction',
        'Narrative Visualization',
        'Market Microstructure',
        'Distribution Plot',
        'Diagram',
        'Text Visualization',
    ]

    # Select by priority
    for category in priority_categories:
        if category not in collection.by_category:
            continue

        for img in collection.by_category[category]:
            stream = img.research_stream

            # Check stream limit
            if stream not in selected_per_stream:
                selected_per_stream[stream] = 0

            if selected_per_stream[stream] >= max_per_stream:
                continue

            # Check total limit
            if len(selected) >= max_total:
                break

            selected.append(img)
            selected_per_stream[stream] += 1

        if len(selected) >= max_total:
            break

    logger.info(f"Selected {len(selected)} key images from {len(collection.images)} total")

    return selected

# =============================================================================
# REPORTING
# =============================================================================

def generate_image_report(collection: ImageCollection) -> Dict:
    """
    Generate a summary report of collected images.

    Returns:
        Dictionary with summary statistics
    """
    report = {
        'total_images': len(collection.images),
        'total_size_mb': round(collection.total_size_mb, 2),
        'by_stream': {
            stream: len(images)
            for stream, images in collection.by_stream.items()
        },
        'by_category': {
            category: len(images)
            for category, images in collection.by_category.items()
        },
        'streams_detail': {}
    }

    # Detailed stream info
    for stream, images in collection.by_stream.items():
        categories_in_stream = {}
        for img in images:
            cat = img.category
            if cat not in categories_in_stream:
                categories_in_stream[cat] = 0
            categories_in_stream[cat] += 1

        report['streams_detail'][stream] = {
            'count': len(images),
            'size_mb': round(sum(img.size_kb for img in images) / 1024, 2),
            'categories': categories_in_stream
        }

    return report

# =============================================================================
# UTILITY
# =============================================================================

def get_web_path(img: ImageInfo, base_url: str = "images/research/") -> str:
    """
    Get web-relative path for an image.

    Args:
        img: ImageInfo object
        base_url: Base URL path

    Returns:
        Web-relative path string
    """
    if img.dest_path:
        stream_folder = get_stream_folder_name(img.research_stream)
        return f"{base_url}{stream_folder}/{img.filename}"

    return f"{base_url}{img.filename}"

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    # Collect images
    collection = collect_research_images()

    # Generate report
    report = generate_image_report(collection)

    print("\n=== IMAGE COLLECTION REPORT ===")
    print(f"Total images: {report['total_images']}")
    print(f"Total size: {report['total_size_mb']} MB")

    print("\nBy Stream:")
    for stream, count in sorted(report['by_stream'].items()):
        print(f"  {stream}: {count}")

    print("\nBy Category:")
    for category, count in sorted(report['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")
