"""
Configuration for PhD Research Pages Generator
Generates GitHub Pages subpages for Gabin Taibi's PhD research

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Source repository with research content
SOURCE_REPO = Path(r"D:\Joerg\Research\slides\Narrative-Digital-Finance-Gabin-Research")

# Target repository for GitHub Pages
TARGET_REPO = Path(r"D:\Joerg\Research\slides\Narrative-Digital-Finance\repo")

# Output directories
IMAGES_DEST = TARGET_REPO / "images" / "research"
DATA_DEST = TARGET_REPO / "data"
SCRIPTS_DIR = TARGET_REPO / "scripts"

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Author:
    """Author information."""
    name: str
    email: Optional[str] = None
    affiliations: List[str] = field(default_factory=list)
    orcid: Optional[str] = None

@dataclass
class ResearchPaper:
    """Metadata structure for a research paper."""
    id: str
    title: str
    authors: List[Author] = field(default_factory=list)
    abstract: str = ""
    status: str = "IN_PROGRESS"  # SUBMITTED, IN_PROGRESS, PLANNING, UNDER_REVIEW, PUBLISHED
    venue: str = ""
    year: int = 2025
    keywords: List[str] = field(default_factory=list)
    work_package: str = ""
    latex_path: Optional[Path] = None
    images: List[Path] = field(default_factory=list)
    ssrn_url: Optional[str] = None
    arxiv_url: Optional[str] = None
    doi: Optional[str] = None
    stream: str = ""

@dataclass
class ResearchStream:
    """Research stream configuration."""
    id: str
    name: str
    description: str
    icon: str  # CSS class or emoji
    color: str  # CSS color variable
    work_package: str
    base_path: Path
    papers: List[ResearchPaper] = field(default_factory=list)

# =============================================================================
# RESEARCH STREAMS CONFIGURATION
# =============================================================================

RESEARCH_STREAMS = {
    "hft": ResearchStream(
        id="hft",
        name="Deutsche Borse HFT Research",
        description="Market microstructure analysis using nanosecond-level trading data from Eurex and Xetra platforms",
        icon="chart-line",
        color="var(--color-primary)",
        work_package="WP4",
        base_path=SOURCE_REPO / "SNF_Narrative_Research" / "Deutsche Börse"
    ),
    "narratives": ResearchStream(
        id="narratives",
        name="Narrative Modeling Research",
        description="NLP and transformer-based narrative detection from central bank speeches and financial text",
        icon="comment-dots",
        color="var(--color-purple)",
        work_package="WP2-WP3",
        base_path=SOURCE_REPO / "SNF_Narrative_Research" / "SNF_Narratives"
    ),
    "slr": ResearchStream(
        id="slr",
        name="Systematic Literature Review",
        description="AI-enhanced systematic review of financial narrative modeling literature",
        icon="book",
        color="var(--color-green)",
        work_package="WP1",
        base_path=SOURCE_REPO / "SNF_Narrative_Research" / "Systematic Literature review"
    ),
    "topol": ResearchStream(
        id="topol",
        name="TOPOL Framework",
        description="Transformer Narrative Polarity Fields for multidimensional semantic shift detection",
        icon="project-diagram",
        color="var(--color-cyan)",
        work_package="WP3",
        base_path=SOURCE_REPO / "SNF_Narrative_Research" / "SNF_Narratives" / "Macro_Narratives" / "Macro_Index_CPD" / "TOPOL"
    ),
    "quoniam": ResearchStream(
        id="quoniam",
        name="Quoniam Industry Collaboration",
        description="Industry-relevant narrative modeling from U.S. financial news headlines",
        icon="handshake",
        color="var(--color-accent)",
        work_package="WP3",
        base_path=SOURCE_REPO / "Quoniam_Narratives"
    )
}

# =============================================================================
# PAPER STATUS CONFIGURATION
# =============================================================================

STATUS_CONFIG = {
    "SUBMITTED": {
        "label": "Submitted",
        "css_class": "badge-submitted",
        "color": "#fef3c7",
        "text_color": "#92400e"
    },
    "IN_PROGRESS": {
        "label": "In Progress",
        "css_class": "badge-progress",
        "color": "#dbeafe",
        "text_color": "#1e40af"
    },
    "PLANNING": {
        "label": "Planning",
        "css_class": "badge-planning",
        "color": "#e0e7ff",
        "text_color": "#3730a3"
    },
    "UNDER_REVIEW": {
        "label": "Under Review",
        "css_class": "badge-review",
        "color": "#fce7f3",
        "text_color": "#9d174d"
    },
    "PUBLISHED": {
        "label": "Published",
        "css_class": "badge-published",
        "color": "#dcfce7",
        "text_color": "#166534"
    }
}

# =============================================================================
# EXCLUDED FILES CONFIGURATION
# =============================================================================

# Files to exclude from paper list (not research papers)
EXCLUDED_TEX_FILES = [
    "thesis_outline.tex",  # Thesis structure, not a paper
    "notes.tex",  # Notes, not a paper
    "template.tex",  # Template
    "example.tex",  # Example
]

# Files to exclude from file catalog
EXCLUDED_CATALOG_FILES = [
    "CLAUDE.md",  # Claude Code config file
    ".claude",  # Claude Code directory
]

# =============================================================================
# KNOWN PAPERS CONFIGURATION (Manual overrides for status/venue)
# =============================================================================

KNOWN_PAPERS = {
    "Market_Participants_Classification.tex": {
        "status": "SUBMITTED",
        "venue": "SSRN",
        "year": 2024,
        "work_package": "WP4",
        "stream": "hft",
        "ssrn_url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4698153",
        "doi": "10.2139/ssrn.4698153"
    },
    "UFT-HFT_Market_Impact.tex": {
        "status": "IN_PROGRESS",
        "venue": "Physica A",
        "year": 2025,
        "work_package": "WP4",
        "stream": "hft"
    },
    "TBD.tex": {
        "status": "PLANNING",
        "venue": "Top Journal TBD",
        "year": 2026,
        "work_package": "WP4",
        "stream": "hft"
    },
    "manuscript-EPIA2025.tex": {
        "status": "SUBMITTED",
        "venue": "EPIA 2025",
        "year": 2025,
        "work_package": "WP3",
        "stream": "topol",
        "arxiv_url": "https://arxiv.org/abs/2510.25069",
        "doi": "10.48550/arXiv.2510.25069"
    },
    "FIN-manuscript.tex": {
        "status": "UNDER_REVIEW",
        "venue": "Financial Innovation",
        "year": 2025,
        "work_package": "WP1",
        "stream": "slr",
        "title": "An Algorithmic Framework for Systematic Literature Reviews with Application to Financial Narratives"
    },
    "main.tex": {
        "status": "IN_PROGRESS",
        "venue": "Working Paper",
        "year": 2025,
        "work_package": "WP1",
        "stream": "slr"
    },
    "manuscript.tex": {
        "status": "IN_PROGRESS",
        "venue": "Quoniam Collaboration",
        "year": 2025,
        "work_package": "WP3",
        "stream": "quoniam"
    }
}

# =============================================================================
# THESIS CHAPTERS CONFIGURATION
# =============================================================================

THESIS_CHAPTERS = [
    {
        "number": 1,
        "title": "Systematic Literature Review of Narratives in Finance",
        "description": "AI-enhanced systematic review mapping narrative concepts in financial research",
        "status": "UNDER_REVIEW",
        "work_package": "WP1",
        "paper_link": "slr"
    },
    {
        "number": 2,
        "title": "Key Financial Market Narratives",
        "description": "Narrative detection methods: supervised embeddings, LLM tagging, and unsupervised clustering",
        "status": "IN_PROGRESS",
        "work_package": "WP2",
        "paper_link": "narratives"
    },
    {
        "number": 3,
        "title": "Market Microstructure and Volatility Modeling",
        "description": "HFT analysis using nanosecond data; realized, implied, and rough volatility estimation",
        "status": "SUBMITTED",
        "work_package": "WP4",
        "paper_link": "hft"
    },
    {
        "number": 4,
        "title": "Do Narratives Drive Markets?",
        "description": "Extending Sadka et al. framework to evaluate narrative explanatory power",
        "status": "IN_PROGRESS",
        "work_package": "WP3",
        "paper_link": "quoniam"
    },
    {
        "number": 5,
        "title": "Narrative-Driven Volatility Structural Breaks",
        "description": "Integrating textual and volatility features for regime detection",
        "status": "PLANNING",
        "work_package": "WP3-WP4",
        "paper_link": None
    },
    {
        "number": 6,
        "title": "Conclusion: Synthesizing Narratives and Volatility",
        "description": "Integration of findings and implications for risk management",
        "status": "PLANNING",
        "work_package": "WP4",
        "paper_link": None
    }
]

# =============================================================================
# COLLABORATORS
# =============================================================================

COLLABORATORS = [
    {
        "name": "Gabin Taibi",
        "role": "PhD Researcher",
        "affiliations": ["Bern University of Applied Sciences", "University of Twente"],
        "email": "gabin.taibi@bfh.ch",
        "orcid": "0000-0002-0785-6771"
    },
    {
        "name": "Joerg Osterrieder",
        "role": "Principal Investigator",
        "affiliations": ["Bern University of Applied Sciences", "University of Twente"],
        "email": "joerg.osterrieder@bfh.ch",
        "orcid": "0000-0003-0189-8636"
    },
    {
        "name": "Stefan Schlamp",
        "role": "Industry Collaborator",
        "affiliations": ["Deutsche Borse"],
        "email": "stefan.schlamp@deutsche-boerse.com",
        "orcid": None
    },
    {
        "name": "Axel Gross-Klussmann",
        "role": "Industry Collaborator",
        "affiliations": ["Quoniam Asset Management"],
        "email": None,
        "orcid": None
    },
    {
        "name": "Lucia Gomez Teijeiro",
        "role": "Researcher",
        "affiliations": ["University of Twente"],
        "email": None,
        "orcid": None
    }
]

# =============================================================================
# HTML GENERATION CONFIG
# =============================================================================

SITE_CONFIG = {
    "base_url": "https://digital-ai-finance.github.io/Narrative-Digital-Finance/",
    "site_title": "Narrative Digital Finance",
    "project_grant": "SNSF Grant IZCOZ0_213370",
    "project_duration": "2023-2026",
    "favicon": "favicon.svg",
    "styles": "styles.css",
    "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
}

# Pages to generate
PAGES_TO_GENERATE = [
    {
        "filename": "gabin-research.html",
        "title": "PhD Research Overview",
        "description": "Gabin Taibi's PhD research on Narrative Dynamics in Financial Markets"
    },
    {
        "filename": "hft-papers.html",
        "title": "HFT Research Papers",
        "description": "Deutsche Borse high-frequency trading and market microstructure research"
    },
    {
        "filename": "narratives-papers.html",
        "title": "Narratives Research Papers",
        "description": "Narrative modeling research using NLP and machine learning"
    },
    {
        "filename": "research-catalog.html",
        "title": "Research File Catalog",
        "description": "Complete inventory of PhD research files and resources"
    }
]

# =============================================================================
# IMAGE CATEGORIES
# =============================================================================

IMAGE_CATEGORIES = {
    "regression": "Regression Analysis",
    "clustering": "Clustering Analysis",
    "pca": "Dimensionality Reduction",
    "wordcloud": "Text Visualization",
    "logo": "Logo",
    "diagram": "Diagram",
    "timeseries": "Time Series",
    "rolling": "Rolling Analysis",
    "distribution": "Distribution Plot",
    "null_hypo": "Statistical Test"
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_status_config(status: str) -> dict:
    """Get status display configuration."""
    return STATUS_CONFIG.get(status, STATUS_CONFIG["IN_PROGRESS"])

def get_paper_override(filename: str) -> Optional[dict]:
    """Get manual override for a paper if it exists."""
    return KNOWN_PAPERS.get(filename)

def get_stream_by_path(file_path: Path) -> Optional[str]:
    """Determine research stream from file path."""
    path_str = str(file_path).lower()

    if "deutsche" in path_str or "hft" in path_str:
        return "hft"
    elif "topol" in path_str:
        return "topol"
    elif "systematic" in path_str or "slr" in path_str:
        return "slr"
    elif "quoniam" in path_str:
        return "quoniam"
    elif "narrative" in path_str or "macro" in path_str:
        return "narratives"

    return None

def categorize_image(filename: str) -> str:
    """Categorize an image by its filename."""
    name_lower = filename.lower()

    for key, category in IMAGE_CATEGORIES.items():
        if key in name_lower:
            return category

    return "Analysis Chart"

# =============================================================================
# GENERATION METADATA
# =============================================================================

def get_generation_metadata() -> dict:
    """Get metadata for generated files."""
    return {
        "generated_at": datetime.now().isoformat(),
        "generator": "PhD Research Pages Generator",
        "version": "1.0.0",
        "source_repo": str(SOURCE_REPO),
        "target_repo": str(TARGET_REPO)
    }
