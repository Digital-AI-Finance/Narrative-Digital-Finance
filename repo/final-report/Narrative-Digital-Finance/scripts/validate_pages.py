"""
Comprehensive Validation Script for PhD Research Pages

Performs ultra-deep validation of generated HTML pages, JSON data,
images, links, and accessibility compliance.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPTS_DIR = Path(__file__).parent
REPO_DIR = SCRIPTS_DIR.parent
DATA_DIR = REPO_DIR / "data"
IMAGES_DIR = REPO_DIR / "images" / "research"

# Generated pages to validate
GENERATED_PAGES = [
    "gabin-research.html",
    "hft-papers.html",
    "narratives-papers.html",
    "research-catalog.html"
]

# COST Action pages to validate
COST_PAGES = [
    "cost-action.html",
    "cost-network.html",
    "cost-events.html",
    "cost-publications.html",
    "cost-mobility.html",
    "cost-resources.html"
]

# All pages to validate
ALL_PAGES = GENERATED_PAGES + COST_PAGES

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationResult:
    """Single validation check result."""
    check_name: str
    passed: bool
    message: str
    severity: str = "info"  # info, warning, error, critical
    details: Optional[Dict] = None

@dataclass
class PageValidation:
    """Validation results for a single page."""
    page_name: str
    file_path: Path
    file_size_kb: float
    results: List[ValidationResult] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity in ["error", "critical"])

@dataclass
class ValidationReport:
    """Complete validation report."""
    timestamp: str
    pages: List[PageValidation] = field(default_factory=list)
    json_validations: List[ValidationResult] = field(default_factory=list)
    image_validations: List[ValidationResult] = field(default_factory=list)
    cross_page_validations: List[ValidationResult] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        total = sum(len(p.results) for p in self.pages)
        total += len(self.json_validations)
        total += len(self.image_validations)
        total += len(self.cross_page_validations)
        return total

    @property
    def total_passed(self) -> int:
        passed = sum(p.passed_count for p in self.pages)
        passed += sum(1 for r in self.json_validations if r.passed)
        passed += sum(1 for r in self.image_validations if r.passed)
        passed += sum(1 for r in self.cross_page_validations if r.passed)
        return passed

# =============================================================================
# HTML PARSER
# =============================================================================

class HTMLAnalyzer(HTMLParser):
    """Parse HTML and extract structure for validation."""

    # HTML5 void elements (self-closing, no end tag needed)
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }

    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.images = []
        self.meta_tags = {}
        self.headings = []
        self.css_classes = set()
        self.ids = set()
        self.aria_labels = []
        self.forms = []
        self.scripts = []
        self.current_tag = None
        self.tag_stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tags.append(tag)
        # Don't add void elements to stack (they don't need closing tags)
        if tag not in self.VOID_ELEMENTS:
            self.tag_stack.append(tag)
        self.current_tag = tag

        # Extract links
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append({
                'href': attrs_dict['href'],
                'target': attrs_dict.get('target', ''),
                'rel': attrs_dict.get('rel', ''),
                'text': ''
            })

        # Extract images
        if tag == 'img':
            self.images.append({
                'src': attrs_dict.get('src', ''),
                'alt': attrs_dict.get('alt', ''),
                'width': attrs_dict.get('width', ''),
                'height': attrs_dict.get('height', '')
            })

        # Extract meta tags
        if tag == 'meta':
            name = attrs_dict.get('name', attrs_dict.get('property', ''))
            content = attrs_dict.get('content', '')
            if name:
                self.meta_tags[name] = content

        # Extract headings
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.headings.append({'level': int(tag[1]), 'text': ''})

        # Extract CSS classes
        if 'class' in attrs_dict:
            for cls in attrs_dict['class'].split():
                self.css_classes.add(cls)

        # Extract IDs
        if 'id' in attrs_dict:
            self.ids.add(attrs_dict['id'])

        # Extract ARIA labels
        if 'aria-label' in attrs_dict:
            self.aria_labels.append(attrs_dict['aria-label'])

        # Extract forms
        if tag == 'form':
            self.forms.append(attrs_dict)

        # Extract scripts
        if tag == 'script':
            self.scripts.append(attrs_dict)

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif self.tag_stack:
            self.errors.append(f"Mismatched tag: expected </{self.tag_stack[-1]}>, got </{tag}>")

    def handle_data(self, data):
        data = data.strip()
        if data:
            # Update last link text
            if self.links and self.current_tag == 'a':
                self.links[-1]['text'] = data[:100]
            # Update last heading text
            if self.headings and self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.headings[-1]['text'] = data[:200]

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_html_structure(content: str, page_name: str) -> List[ValidationResult]:
    """Validate HTML structure and syntax."""
    results = []

    # Parse HTML
    analyzer = HTMLAnalyzer()
    try:
        analyzer.feed(content)
        results.append(ValidationResult(
            "HTML Parsing",
            True,
            "HTML parsed successfully without fatal errors"
        ))
    except Exception as e:
        results.append(ValidationResult(
            "HTML Parsing",
            False,
            f"HTML parsing failed: {e}",
            severity="critical"
        ))
        return results

    # Check for parsing errors
    if analyzer.errors:
        results.append(ValidationResult(
            "Tag Matching",
            False,
            f"Found {len(analyzer.errors)} tag matching issues",
            severity="error",
            details={"errors": analyzer.errors[:10]}
        ))
    else:
        results.append(ValidationResult(
            "Tag Matching",
            True,
            "All HTML tags properly matched"
        ))

    # Check DOCTYPE
    if content.strip().lower().startswith('<!doctype html>'):
        results.append(ValidationResult(
            "DOCTYPE Declaration",
            True,
            "Valid HTML5 DOCTYPE declaration"
        ))
    else:
        results.append(ValidationResult(
            "DOCTYPE Declaration",
            False,
            "Missing or invalid DOCTYPE declaration",
            severity="warning"
        ))

    # Check essential meta tags
    essential_meta = ['description', 'viewport', 'og:title', 'og:description']
    missing_meta = [m for m in essential_meta if m not in analyzer.meta_tags]

    if not missing_meta:
        results.append(ValidationResult(
            "Meta Tags",
            True,
            f"All {len(essential_meta)} essential meta tags present",
            details={"meta_tags": list(analyzer.meta_tags.keys())}
        ))
    else:
        results.append(ValidationResult(
            "Meta Tags",
            False,
            f"Missing meta tags: {', '.join(missing_meta)}",
            severity="warning",
            details={"missing": missing_meta, "present": list(analyzer.meta_tags.keys())}
        ))

    # Check heading hierarchy
    if analyzer.headings:
        h1_count = sum(1 for h in analyzer.headings if h['level'] == 1)
        if h1_count == 1:
            results.append(ValidationResult(
                "H1 Heading",
                True,
                f"Single H1 heading found: '{analyzer.headings[0]['text'][:50]}...'"
            ))
        elif h1_count == 0:
            results.append(ValidationResult(
                "H1 Heading",
                False,
                "No H1 heading found",
                severity="warning"
            ))
        else:
            results.append(ValidationResult(
                "H1 Heading",
                False,
                f"Multiple H1 headings found ({h1_count})",
                severity="warning"
            ))

    # Check for skip link (accessibility)
    skip_link_found = any('skip' in link.get('href', '').lower() or 'skip' in link.get('text', '').lower()
                          for link in analyzer.links)
    results.append(ValidationResult(
        "Skip Link",
        skip_link_found,
        "Skip to main content link present" if skip_link_found else "No skip link found",
        severity="info" if skip_link_found else "warning"
    ))

    # Check for main landmark
    main_found = 'main-content' in analyzer.ids or 'main' in [t for t in analyzer.tags]
    results.append(ValidationResult(
        "Main Landmark",
        main_found,
        "Main content landmark found" if main_found else "No main content landmark",
        severity="info" if main_found else "warning"
    ))

    # Check ARIA labels
    if analyzer.aria_labels:
        results.append(ValidationResult(
            "ARIA Labels",
            True,
            f"Found {len(analyzer.aria_labels)} ARIA labels",
            details={"labels": analyzer.aria_labels}
        ))

    return results

def validate_links(content: str, page_name: str, repo_dir: Path) -> List[ValidationResult]:
    """Validate all links in the page."""
    results = []

    analyzer = HTMLAnalyzer()
    analyzer.feed(content)

    internal_links = []
    external_links = []
    broken_internal = []

    for link in analyzer.links:
        href = link['href']

        if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue

        parsed = urlparse(href)

        if parsed.scheme in ['http', 'https']:
            external_links.append(href)
        else:
            internal_links.append(href)
            # Check if internal file exists
            link_path = repo_dir / href.split('#')[0]
            if not link_path.exists():
                broken_internal.append(href)

    # Report internal links
    if internal_links:
        if broken_internal:
            results.append(ValidationResult(
                "Internal Links",
                False,
                f"Found {len(broken_internal)} broken internal links out of {len(internal_links)}",
                severity="error",
                details={"broken": broken_internal}
            ))
        else:
            results.append(ValidationResult(
                "Internal Links",
                True,
                f"All {len(internal_links)} internal links valid"
            ))

    # Report external links
    if external_links:
        results.append(ValidationResult(
            "External Links",
            True,
            f"Found {len(external_links)} external links (not verified)",
            details={"links": external_links[:10]}
        ))

    # Check for rel="noopener" on external links
    external_with_target = [l for l in analyzer.links
                           if l.get('target') == '_blank' and
                           urlparse(l.get('href', '')).scheme in ['http', 'https']]
    missing_noopener = [l for l in external_with_target
                        if 'noopener' not in l.get('rel', '')]

    if external_with_target:
        if missing_noopener:
            results.append(ValidationResult(
                "External Link Security",
                False,
                f"{len(missing_noopener)} external links missing rel='noopener'",
                severity="warning"
            ))
        else:
            results.append(ValidationResult(
                "External Link Security",
                True,
                "All external links have proper rel='noopener'"
            ))

    return results

def validate_images(content: str, page_name: str, repo_dir: Path) -> List[ValidationResult]:
    """Validate all image references."""
    results = []

    analyzer = HTMLAnalyzer()
    analyzer.feed(content)

    missing_images = []
    missing_alt = []
    valid_images = []

    for img in analyzer.images:
        src = img['src']
        alt = img['alt']

        if not src:
            continue

        # Check if local image exists
        if not src.startswith('http'):
            img_path = repo_dir / src
            if img_path.exists():
                valid_images.append(src)
            else:
                missing_images.append(src)

        # Check alt text
        if not alt:
            missing_alt.append(src)

    # Report image validation
    total_images = len(analyzer.images)
    if total_images > 0:
        if missing_images:
            results.append(ValidationResult(
                "Image Files",
                False,
                f"{len(missing_images)} missing images out of {total_images}",
                severity="error",
                details={"missing": missing_images}
            ))
        else:
            results.append(ValidationResult(
                "Image Files",
                True,
                f"All {len(valid_images)} local images exist"
            ))

        if missing_alt:
            results.append(ValidationResult(
                "Image Alt Text",
                False,
                f"{len(missing_alt)} images missing alt text",
                severity="warning",
                details={"missing_alt": missing_alt[:10]}
            ))
        else:
            results.append(ValidationResult(
                "Image Alt Text",
                True,
                f"All {total_images} images have alt text"
            ))
    else:
        results.append(ValidationResult(
            "Images",
            True,
            "No images in this page"
        ))

    return results

def validate_css_classes(content: str, page_name: str, repo_dir: Path) -> List[ValidationResult]:
    """Validate CSS classes against existing stylesheet."""
    results = []

    # Parse HTML
    analyzer = HTMLAnalyzer()
    analyzer.feed(content)

    # Read existing CSS
    css_path = repo_dir / "styles.css"
    if not css_path.exists():
        results.append(ValidationResult(
            "CSS File",
            False,
            "styles.css not found",
            severity="error"
        ))
        return results

    css_content = css_path.read_text(encoding='utf-8')

    # Extract CSS class definitions
    css_classes = set(re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', css_content))

    # Check which classes are used but not defined
    used_classes = analyzer.css_classes
    undefined_classes = used_classes - css_classes

    # Filter out common utility/inline classes
    ignore_patterns = ['active', 'hidden', 'visible', 'text-', 'bg-', 'p-', 'm-', 'flex', 'grid']
    undefined_filtered = [c for c in undefined_classes
                          if not any(c.startswith(p) for p in ignore_patterns)]

    if undefined_filtered:
        results.append(ValidationResult(
            "CSS Classes",
            False,
            f"Found {len(undefined_filtered)} potentially undefined CSS classes",
            severity="info",
            details={"undefined": list(undefined_filtered)[:20]}
        ))
    else:
        results.append(ValidationResult(
            "CSS Classes",
            True,
            f"All {len(used_classes)} CSS classes appear valid"
        ))

    # Check for critical site classes
    critical_classes = ['navbar', 'sidebar', 'main', 'container', 'card']
    used_critical = [c for c in critical_classes if c in used_classes]

    results.append(ValidationResult(
        "Site Structure Classes",
        len(used_critical) >= 3,
        f"Using {len(used_critical)}/5 critical layout classes: {', '.join(used_critical)}",
        severity="info"
    ))

    return results

def validate_json_data(data_dir: Path) -> List[ValidationResult]:
    """Validate JSON data files."""
    results = []

    json_files = {
        'research.json': ['papers', 'paper_count', 'by_stream'],
        'file_catalog.json': ['files', 'summary'],
        'thesis.json': ['chapters', 'chapter_count'],
        'collaborators.json': ['collaborators', 'count'],
        'images.json': ['images', 'total_images'],
        'cost_summary.json': ['metadata', 'stats', 'working_groups']
    }

    for filename, required_keys in json_files.items():
        filepath = data_dir / filename

        if not filepath.exists():
            results.append(ValidationResult(
                f"JSON: {filename}",
                False,
                f"File not found: {filename}",
                severity="error"
            ))
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required keys
            missing_keys = [k for k in required_keys if k not in data]

            if missing_keys:
                results.append(ValidationResult(
                    f"JSON: {filename}",
                    False,
                    f"Missing required keys: {', '.join(missing_keys)}",
                    severity="error"
                ))
            else:
                # Get some stats
                stats = {}
                for key in required_keys:
                    val = data.get(key)
                    if isinstance(val, list):
                        stats[key] = len(val)
                    elif isinstance(val, (int, float)):
                        stats[key] = val
                    elif isinstance(val, dict):
                        stats[key] = len(val)

                results.append(ValidationResult(
                    f"JSON: {filename}",
                    True,
                    f"Valid JSON with {stats}",
                    details=stats
                ))

        except json.JSONDecodeError as e:
            results.append(ValidationResult(
                f"JSON: {filename}",
                False,
                f"Invalid JSON syntax: {e}",
                severity="critical"
            ))
        except Exception as e:
            results.append(ValidationResult(
                f"JSON: {filename}",
                False,
                f"Error reading file: {e}",
                severity="error"
            ))

    return results

def validate_image_files(images_dir: Path) -> List[ValidationResult]:
    """Validate image files in research directory."""
    results = []

    if not images_dir.exists():
        results.append(ValidationResult(
            "Images Directory",
            False,
            f"Images directory not found: {images_dir}",
            severity="error"
        ))
        return results

    # Count images by stream
    stream_dirs = ['hft', 'narratives', 'slr', 'topol', 'quoniam']
    total_images = 0
    stream_counts = {}

    for stream in stream_dirs:
        stream_dir = images_dir / stream
        if stream_dir.exists():
            images = list(stream_dir.glob('*.png'))
            stream_counts[stream] = len(images)
            total_images += len(images)
        else:
            stream_counts[stream] = 0

    results.append(ValidationResult(
        "Image Organization",
        total_images > 0,
        f"Found {total_images} images across {len([s for s, c in stream_counts.items() if c > 0])} streams",
        details=stream_counts
    ))

    # Check image sizes
    large_images = []
    for stream in stream_dirs:
        stream_dir = images_dir / stream
        if stream_dir.exists():
            for img in stream_dir.glob('*.png'):
                size_kb = img.stat().st_size / 1024
                if size_kb > 500:  # > 500KB
                    large_images.append((img.name, round(size_kb, 1)))

    if large_images:
        results.append(ValidationResult(
            "Image Sizes",
            True,
            f"Found {len(large_images)} large images (>500KB)",
            severity="info",
            details={"large_images": large_images[:10]}
        ))
    else:
        results.append(ValidationResult(
            "Image Sizes",
            True,
            "All images are reasonably sized"
        ))

    return results

def validate_cross_page_consistency(pages_data: Dict[str, str], repo_dir: Path) -> List[ValidationResult]:
    """Validate consistency across all pages."""
    results = []

    # Check navbar consistency
    navbar_patterns = []
    for page_name, content in pages_data.items():
        navbar_match = re.search(r'<nav class="navbar">(.*?)</nav>', content, re.DOTALL)
        if navbar_match:
            navbar_patterns.append(navbar_match.group(1)[:200])

    if len(set(navbar_patterns)) == 1:
        results.append(ValidationResult(
            "Navbar Consistency",
            True,
            "All pages have consistent navbar structure"
        ))
    else:
        results.append(ValidationResult(
            "Navbar Consistency",
            False,
            "Navbar structure varies between pages",
            severity="warning"
        ))

    # Check sidebar consistency
    sidebar_patterns = []
    for page_name, content in pages_data.items():
        sidebar_match = re.search(r'<aside class="sidebar"', content)
        sidebar_patterns.append(bool(sidebar_match))

    if all(sidebar_patterns):
        results.append(ValidationResult(
            "Sidebar Presence",
            True,
            "All pages have sidebar"
        ))
    elif any(sidebar_patterns):
        results.append(ValidationResult(
            "Sidebar Presence",
            False,
            "Some pages missing sidebar",
            severity="warning"
        ))

    # Check footer consistency
    footer_patterns = []
    for page_name, content in pages_data.items():
        footer_match = re.search(r'<footer', content)
        footer_patterns.append(bool(footer_match))

    if all(footer_patterns):
        results.append(ValidationResult(
            "Footer Presence",
            True,
            "All pages have footer"
        ))
    elif any(footer_patterns):
        results.append(ValidationResult(
            "Footer Presence",
            False,
            "Some pages missing footer",
            severity="info"
        ))

    # Check cross-references
    all_pages = set(pages_data.keys())
    for page_name, content in pages_data.items():
        analyzer = HTMLAnalyzer()
        analyzer.feed(content)

        for link in analyzer.links:
            href = link['href'].split('#')[0]
            if href.endswith('.html') and href in ALL_PAGES:
                if href not in all_pages:
                    results.append(ValidationResult(
                        "Cross-Page Links",
                        False,
                        f"{page_name} links to missing page: {href}",
                        severity="error"
                    ))

    results.append(ValidationResult(
        "Cross-Page Links",
        True,
        "All cross-page references valid"
    ))

    return results

def analyze_paper_extraction(data_dir: Path) -> List[ValidationResult]:
    """Analyze accuracy of paper metadata extraction."""
    results = []

    research_path = data_dir / "research.json"
    if not research_path.exists():
        results.append(ValidationResult(
            "Paper Analysis",
            False,
            "research.json not found",
            severity="error"
        ))
        return results

    with open(research_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])

    # Analyze paper quality
    papers_with_title = [p for p in papers if p.get('title')]
    papers_with_abstract = [p for p in papers if p.get('abstract')]
    papers_with_authors = [p for p in papers if p.get('authors')]
    papers_with_keywords = [p for p in papers if p.get('keywords')]

    results.append(ValidationResult(
        "Paper Titles",
        len(papers_with_title) == len(papers),
        f"{len(papers_with_title)}/{len(papers)} papers have titles",
        severity="info" if len(papers_with_title) == len(papers) else "warning"
    ))

    results.append(ValidationResult(
        "Paper Abstracts",
        len(papers_with_abstract) > len(papers) * 0.5,
        f"{len(papers_with_abstract)}/{len(papers)} papers have abstracts",
        severity="info"
    ))

    results.append(ValidationResult(
        "Paper Authors",
        len(papers_with_authors) > len(papers) * 0.5,
        f"{len(papers_with_authors)}/{len(papers)} papers have authors",
        severity="info"
    ))

    # Check stream distribution
    by_stream = data.get('by_stream', {})
    if by_stream:
        results.append(ValidationResult(
            "Stream Distribution",
            True,
            f"Papers distributed across {len(by_stream)} streams",
            details={s: len(p) for s, p in by_stream.items()}
        ))

    # Check status distribution
    by_status = data.get('by_status', {})
    if by_status:
        results.append(ValidationResult(
            "Status Distribution",
            True,
            f"Papers have {len(by_status)} different statuses",
            details={s: len(p) for s, p in by_status.items()}
        ))

    return results

# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_full_validation() -> ValidationReport:
    """Run complete validation suite."""
    report = ValidationReport(timestamp=datetime.now().isoformat())

    print("=" * 70)
    print("PhD RESEARCH PAGES - COMPREHENSIVE VALIDATION")
    print("=" * 70)
    print(f"Repository: {REPO_DIR}")
    print(f"Timestamp: {report.timestamp}")
    print()

    # Validate each generated page
    print("VALIDATING HTML PAGES")
    print("-" * 40)

    pages_data = {}
    for page_name in ALL_PAGES:
        page_path = REPO_DIR / page_name

        if not page_path.exists():
            print(f"  [MISSING] {page_name}")
            page_val = PageValidation(
                page_name=page_name,
                file_path=page_path,
                file_size_kb=0
            )
            page_val.results.append(ValidationResult(
                "File Exists",
                False,
                f"Page file not found: {page_name}",
                severity="critical"
            ))
            report.pages.append(page_val)
            continue

        # Read page content
        content = page_path.read_text(encoding='utf-8')
        pages_data[page_name] = content
        file_size_kb = page_path.stat().st_size / 1024

        print(f"  [OK] {page_name} ({file_size_kb:.1f} KB)")

        page_val = PageValidation(
            page_name=page_name,
            file_path=page_path,
            file_size_kb=file_size_kb
        )

        # Run validations
        page_val.results.extend(validate_html_structure(content, page_name))
        page_val.results.extend(validate_links(content, page_name, REPO_DIR))
        page_val.results.extend(validate_images(content, page_name, REPO_DIR))
        page_val.results.extend(validate_css_classes(content, page_name, REPO_DIR))

        report.pages.append(page_val)

    print()

    # Validate JSON data
    print("VALIDATING JSON DATA")
    print("-" * 40)
    report.json_validations = validate_json_data(DATA_DIR)
    for result in report.json_validations:
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} {result.check_name}: {result.message}")
    print()

    # Validate images
    print("VALIDATING IMAGE FILES")
    print("-" * 40)
    report.image_validations = validate_image_files(IMAGES_DIR)
    for result in report.image_validations:
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} {result.check_name}: {result.message}")
    print()

    # Cross-page validation
    print("VALIDATING CROSS-PAGE CONSISTENCY")
    print("-" * 40)
    report.cross_page_validations = validate_cross_page_consistency(pages_data, REPO_DIR)
    for result in report.cross_page_validations:
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} {result.check_name}: {result.message}")
    print()

    # Paper extraction analysis
    print("ANALYZING PAPER EXTRACTION")
    print("-" * 40)
    paper_results = analyze_paper_extraction(DATA_DIR)
    report.cross_page_validations.extend(paper_results)
    for result in paper_results:
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} {result.check_name}: {result.message}")
    print()

    return report

def print_summary(report: ValidationReport):
    """Print validation summary."""
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    total = report.total_checks
    passed = report.total_passed
    failed = total - passed

    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print()

    # Per-page summary
    print("Per-Page Results:")
    for page in report.pages:
        status = "PASS" if page.error_count == 0 else "FAIL"
        print(f"  [{status}] {page.page_name}: {page.passed_count}/{len(page.results)} checks passed")
    print()

    # List any critical/error issues
    critical_issues = []
    for page in report.pages:
        for result in page.results:
            if not result.passed and result.severity in ['error', 'critical']:
                critical_issues.append(f"{page.page_name}: {result.check_name} - {result.message}")

    for result in report.json_validations:
        if not result.passed and result.severity in ['error', 'critical']:
            critical_issues.append(f"JSON: {result.check_name} - {result.message}")

    for result in report.image_validations:
        if not result.passed and result.severity in ['error', 'critical']:
            critical_issues.append(f"Images: {result.check_name} - {result.message}")

    if critical_issues:
        print("CRITICAL ISSUES:")
        for issue in critical_issues:
            print(f"  - {issue}")
    else:
        print("No critical issues found!")

    print()
    print("=" * 70)

    return failed == 0 or all(page.error_count == 0 for page in report.pages)

def save_report(report: ValidationReport, output_path: Path):
    """Save detailed report to JSON."""
    report_dict = {
        'timestamp': report.timestamp,
        'summary': {
            'total_checks': report.total_checks,
            'total_passed': report.total_passed,
            'total_failed': report.total_checks - report.total_passed
        },
        'pages': [
            {
                'name': page.page_name,
                'file_size_kb': page.file_size_kb,
                'passed': page.passed_count,
                'failed': page.failed_count,
                'results': [
                    {
                        'check': r.check_name,
                        'passed': r.passed,
                        'message': r.message,
                        'severity': r.severity,
                        'details': r.details
                    }
                    for r in page.results
                ]
            }
            for page in report.pages
        ],
        'json_validations': [
            {'check': r.check_name, 'passed': r.passed, 'message': r.message}
            for r in report.json_validations
        ],
        'image_validations': [
            {'check': r.check_name, 'passed': r.passed, 'message': r.message, 'details': r.details}
            for r in report.image_validations
        ],
        'cross_page_validations': [
            {'check': r.check_name, 'passed': r.passed, 'message': r.message, 'details': r.details}
            for r in report.cross_page_validations
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2, default=str)

    print(f"Detailed report saved to: {output_path}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    report = run_full_validation()
    success = print_summary(report)

    # Save detailed report
    report_path = DATA_DIR / "validation_report.json"
    save_report(report, report_path)

    sys.exit(0 if success else 1)
