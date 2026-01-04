"""
HTML Page Generator for Research Pages

Generates HTML pages matching the existing NDF site style with
navbar, sidebar, and main content area.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import html
import json
import logging

from config import (
    TARGET_REPO,
    SITE_CONFIG,
    RESEARCH_STREAMS,
    THESIS_CHAPTERS,
    STATUS_CONFIG,
    PAGES_TO_GENERATE,
    COLLABORATORS
)

logger = logging.getLogger(__name__)

# =============================================================================
# HTML COMPONENTS
# =============================================================================

def get_head_section(title: str, description: str, page_name: str = "") -> str:
    """Generate HTML head with proper meta tags."""
    canonical = f"{SITE_CONFIG['base_url']}{page_name}" if page_name else SITE_CONFIG['base_url']

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} | {SITE_CONFIG['site_title']}</title>
    <meta name="description" content="{html.escape(description)}">
    <meta name="keywords" content="narrative finance, PhD research, NLP, machine learning, HFT, volatility, financial markets">
    <meta name="author" content="Gabin Taibi, Prof. Dr. Joerg Osterrieder">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{html.escape(title)} | {SITE_CONFIG['site_title']}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta name="twitter:card" content="summary">
    <link rel="icon" type="image/svg+xml" href="{SITE_CONFIG['favicon']}">
    <link href="{SITE_CONFIG['font_url']}" rel="stylesheet">
    <link rel="stylesheet" href="{SITE_CONFIG['styles']}">
</head>'''

def get_navbar(active_page: str = "") -> str:
    """Generate navbar matching existing site."""
    nav_items = [
        ("index.html", "Home"),
        ("gabin-research.html", "PhD Research"),
        ("objectives.html", "Objectives"),
        ("inventory.html", "Inventory"),
    ]

    nav_links = []
    for href, label in nav_items:
        active_class = ' class="active"' if href == active_page else ''
        nav_links.append(f'<a href="{href}"{active_class}>{label}</a>')

    return f'''<nav class="navbar">
    <a href="index.html" class="navbar-brand"><span>NDF</span> Narrative Digital Finance</a>
    <div class="navbar-nav">
        {" ".join(nav_links)}
    </div>
</nav>'''

def get_sidebar(active_page: str = "") -> str:
    """Generate sidebar with PhD research section."""

    def sidebar_link(href: str, label: str) -> str:
        active = ' style="font-weight: 600; color: var(--color-primary);"' if href == active_page else ''
        return f'<a href="{href}" class="sidebar-link"{active}>{label}</a>'

    return f'''<aside class="sidebar" aria-label="Main navigation">
    <div class="sidebar-section">
        <div class="sidebar-title">Navigation</div>
        <ul class="sidebar-nav">
            <li><a href="index.html#overview">Home</a></li>
            <li><a href="index.html#research">Research</a></li>
            <li><a href="index.html#publications">Publications</a></li>
        </ul>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">PhD Research</div>
        {sidebar_link("gabin-research.html", "Overview")}
        {sidebar_link("hft-papers.html", "HFT Papers")}
        {sidebar_link("narratives-papers.html", "Narratives Papers")}
        {sidebar_link("research-catalog.html", "File Catalog")}
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Project Pages</div>
        {sidebar_link("objectives.html", "Research Objectives")}
        {sidebar_link("report.html", "Final Report")}
        {sidebar_link("inventory.html", "Evidence Inventory")}
        {sidebar_link("dmp.html", "Data Management")}
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Official Links</div>
        <a href="https://data.snf.ch/grants/grant/213370" class="sidebar-link" target="_blank" rel="noopener noreferrer">SNSF Portal</a>
        <a href="https://www.bfh.ch/en/research/research-projects/2023-180-022-876/" class="sidebar-link" target="_blank" rel="noopener noreferrer">BFH Project</a>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Funding</div>
        <div class="sidebar-badge">
            <a href="https://www.mysnf.ch/grants/grant.aspx?id=c8d8081e-6eee-4418-92bb-21dc2c89566a" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/SNSF-red?style=flat-square" alt="SNSF"></a>
        </div>
    </div>
</aside>'''

def get_footer() -> str:
    """Generate page footer."""
    year = datetime.now().year
    return f'''<footer class="footer">
    <div class="container">
        <div class="footer-bottom">
            {SITE_CONFIG['project_grant']} | {SITE_CONFIG['site_title']} | {SITE_CONFIG['project_duration']}
            <br>
            <span style="font-size: 10px; color: var(--color-text-light);">
                PhD Research pages generated on {datetime.now().strftime("%Y-%m-%d")}
            </span>
        </div>
    </div>
</footer>'''

def get_paper_comparison_html(papers: List[Dict]) -> str:
    """Generate paper comparison modal and scripts."""
    if not papers:
        return ""

    # Build paper data for JavaScript
    papers_json = json.dumps([{
        'id': p.get('id', ''),
        'title': p.get('title', 'Untitled'),
        'authors': p.get('authors_string', ''),
        'abstract': p.get('abstract', ''),
        'status': p.get('status', ''),
        'venue': p.get('venue', ''),
        'year': p.get('year', ''),
        'stream': p.get('stream', ''),
        'work_package': p.get('work_package', ''),
        'keywords': p.get('keywords', [])
    } for p in papers])

    return f'''
<!-- Paper Comparison Modal -->
<div id="compare-modal" class="compare-overlay" style="display: none;">
    <div class="compare-content" style="background: white; border-radius: 8px; max-width: 95%; max-height: 90%; overflow: auto; padding: 20px; position: relative;">
        <button class="compare-close" onclick="closeComparison()" aria-label="Close" style="position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
        <h3 style="font-size: 16px; margin-bottom: 16px; color: var(--color-dark);">Compare Papers</h3>
        <div id="compare-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div id="compare-left" class="compare-paper"></div>
            <div id="compare-right" class="compare-paper"></div>
        </div>
    </div>
</div>

<!-- Compare Selection Bar -->
<div id="compare-bar" style="display: none; position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--color-dark); color: white; padding: 12px 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 1000; display: none; align-items: center; gap: 12px;">
    <span id="compare-count">0 papers selected</span>
    <button onclick="showComparison()" style="background: var(--color-accent); color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 11px;">Compare</button>
    <button onclick="clearSelection()" style="background: transparent; color: white; border: 1px solid white; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 11px;">Clear</button>
</div>

<style>
.compare-overlay {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.compare-paper {{
    background: var(--color-bg-alt);
    padding: 16px;
    border-radius: 6px;
}}
.compare-btn {{
    font-size: 9px;
    padding: 2px 6px;
    border: 1px solid var(--color-primary);
    background: white;
    color: var(--color-primary);
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.2s;
}}
.compare-btn.selected {{
    background: var(--color-primary);
    color: white;
}}
</style>

<script>
const allPapers = {papers_json};
let selectedPapers = [];

function toggleCompare(paperId, btn) {{
    const idx = selectedPapers.indexOf(paperId);
    if (idx === -1) {{
        if (selectedPapers.length < 2) {{
            selectedPapers.push(paperId);
            btn.classList.add('selected');
            btn.textContent = 'Selected';
        }}
    }} else {{
        selectedPapers.splice(idx, 1);
        btn.classList.remove('selected');
        btn.textContent = 'Compare';
    }}
    updateCompareBar();
}}

function updateCompareBar() {{
    const bar = document.getElementById('compare-bar');
    const count = document.getElementById('compare-count');
    if (selectedPapers.length > 0) {{
        bar.style.display = 'flex';
        count.textContent = selectedPapers.length + ' paper(s) selected';
    }} else {{
        bar.style.display = 'none';
    }}
}}

function showComparison() {{
    if (selectedPapers.length < 2) {{
        alert('Please select 2 papers to compare');
        return;
    }}
    const p1 = allPapers.find(p => p.id === selectedPapers[0]);
    const p2 = allPapers.find(p => p.id === selectedPapers[1]);

    document.getElementById('compare-left').innerHTML = buildPaperCard(p1);
    document.getElementById('compare-right').innerHTML = buildPaperCard(p2);
    document.getElementById('compare-modal').style.display = 'flex';
}}

function buildPaperCard(p) {{
    const keywords = (p.keywords || []).slice(0, 5).map(k => '<span style="font-size:9px;background:#f3f4f6;padding:2px 4px;border-radius:2px;">' + k + '</span>').join(' ');
    return '<h4 style="font-size:13px;color:var(--color-dark);margin-bottom:8px;">' + p.title + '</h4>' +
           '<p style="font-size:10px;color:var(--color-text-muted);margin-bottom:6px;">' + p.authors + '</p>' +
           '<p style="font-size:10px;margin-bottom:6px;"><strong>Venue:</strong> ' + p.venue + ' (' + p.year + ')</p>' +
           '<p style="font-size:10px;margin-bottom:6px;"><strong>Status:</strong> ' + p.status + '</p>' +
           '<p style="font-size:10px;margin-bottom:6px;"><strong>Stream:</strong> ' + p.stream + ' | <strong>WP:</strong> ' + p.work_package + '</p>' +
           '<p style="font-size:11px;margin-bottom:8px;">' + (p.abstract || '').substring(0, 300) + '...</p>' +
           '<div style="display:flex;gap:4px;flex-wrap:wrap;">' + keywords + '</div>';
}}

function closeComparison() {{
    document.getElementById('compare-modal').style.display = 'none';
}}

function clearSelection() {{
    selectedPapers = [];
    document.querySelectorAll('.compare-btn').forEach(btn => {{
        btn.classList.remove('selected');
        btn.textContent = 'Compare';
    }});
    updateCompareBar();
}}

document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeComparison();
}});
</script>
'''

def get_lightbox_html() -> str:
    """Generate lightbox modal for image viewing."""
    return '''
<!-- Image Lightbox Modal -->
<div id="lightbox-modal" class="lightbox-overlay" style="display: none;">
    <div class="lightbox-content">
        <button class="lightbox-close" onclick="closeLightbox()" aria-label="Close">&times;</button>
        <img id="lightbox-img" src="" alt="">
        <div id="lightbox-caption" class="lightbox-caption"></div>
    </div>
</div>

<style>
.lightbox-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.lightbox-content {
    position: relative;
    max-width: 90%;
    max-height: 90%;
    cursor: default;
}
.lightbox-content img {
    max-width: 100%;
    max-height: 85vh;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5);
}
.lightbox-close {
    position: absolute;
    top: -40px;
    right: 0;
    background: none;
    border: none;
    color: white;
    font-size: 32px;
    cursor: pointer;
    padding: 8px;
    line-height: 1;
}
.lightbox-close:hover {
    color: var(--color-accent);
}
.lightbox-caption {
    color: white;
    text-align: center;
    padding: 12px;
    font-size: 12px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 0 0 8px 8px;
}
.gallery-item {
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}
.gallery-item:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>

<script>
function openLightbox(imgSrc, caption) {
    const modal = document.getElementById('lightbox-modal');
    const img = document.getElementById('lightbox-img');
    const cap = document.getElementById('lightbox-caption');
    img.src = imgSrc;
    cap.textContent = caption || '';
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const modal = document.getElementById('lightbox-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

// Close on background click
document.addEventListener('click', function(e) {
    if (e.target.id === 'lightbox-modal') {
        closeLightbox();
    }
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeLightbox();
    }
});
</script>
'''

def get_status_badge(status: str) -> str:
    """Generate status badge HTML."""
    config = STATUS_CONFIG.get(status, STATUS_CONFIG['IN_PROGRESS'])
    return f'''<span class="badge" style="background: {config['color']}; color: {config['text_color']}; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 500;">{config['label']}</span>'''

def get_stream_badge(stream: str) -> str:
    """Generate research stream badge."""
    stream_config = RESEARCH_STREAMS.get(stream)
    if stream_config:
        return f'''<span class="wp-tag" style="font-size: 10px;">{stream_config.work_package}</span>'''
    return ''

# =============================================================================
# PAGE GENERATORS
# =============================================================================

def generate_research_overview_page(research_data: Dict, image_data: Optional[Dict] = None) -> str:
    """
    Generate gabin-research.html - PhD research overview.

    Args:
        research_data: Research papers data
        image_data: Optional image collection data

    Returns:
        Complete HTML string
    """
    head = get_head_section(
        "PhD Research Overview",
        "Gabin Taibi's PhD research on Narrative Dynamics in Financial Markets - combining NLP with high-frequency financial data analysis",
        "gabin-research.html"
    )

    # Statistics
    paper_count = research_data.get('paper_count', 0)
    image_count = image_data.get('total_images', 0) if image_data else 124
    chapter_count = len(THESIS_CHAPTERS)

    # Build thesis chapters HTML
    chapters_html = build_thesis_chapters_html()

    # Build thesis timeline HTML
    timeline_html = build_thesis_timeline_html()

    # Build research streams HTML
    streams_html = build_research_streams_html(research_data)

    # Build papers summary HTML
    papers_html = build_papers_summary_html(research_data)

    # Build collaborators section
    collaborators_html = build_collaborators_html()

    # Build collaboration network
    network_html = build_collaboration_network_html()

    # Build OpenAlex integration script
    openalex_script = build_openalex_script(research_data)

    return f'''{head}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("gabin-research.html")}
    {get_sidebar("gabin-research.html")}

    <main class="main" id="main-content">
        <div class="hero" style="background: linear-gradient(135deg, var(--color-dark) 0%, var(--color-dark-light) 100%); padding: 24px; text-align: center;">
            <h1 style="color: white; font-size: 20px; margin-bottom: 8px;">PhD Research: Narrative Dynamics in Financial Markets</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 12px; margin-bottom: 16px;">Gabin Taibi | University of Twente & Bern University of Applied Sciences</p>
            <div class="hero-stats" style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">
                <div class="hero-stat" style="text-align: center;">
                    <div class="hero-stat-val" style="font-size: 24px; font-weight: 700; color: white;">{paper_count}</div>
                    <div class="hero-stat-lbl" style="font-size: 10px; color: rgba(255,255,255,0.7);">Papers</div>
                </div>
                <div class="hero-stat" style="text-align: center;">
                    <div class="hero-stat-val" style="font-size: 24px; font-weight: 700; color: white;">{image_count}</div>
                    <div class="hero-stat-lbl" style="font-size: 10px; color: rgba(255,255,255,0.7);">Visualizations</div>
                </div>
                <div class="hero-stat" style="text-align: center;">
                    <div class="hero-stat-val" style="font-size: 24px; font-weight: 700; color: white;">{chapter_count}</div>
                    <div class="hero-stat-lbl" style="font-size: 10px; color: rgba(255,255,255,0.7);">Thesis Chapters</div>
                </div>
            </div>
        </div>

        <div class="container" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

            <section class="section" id="timeline" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-cyan);">
                    PhD Timeline (2023-2026)
                </div>
                {timeline_html}
            </section>

            <section class="section" id="thesis" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-primary);">
                    Thesis Structure
                </div>
                <p style="font-size: 12px; color: var(--color-text-muted); margin-bottom: 16px;">
                    <strong>Title:</strong> Modeling Narrative Dynamics for Volatility Regime Detection in Financial Markets
                </p>
                {chapters_html}
            </section>

            <section class="section" id="streams" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-purple);">
                    Research Streams
                </div>
                {streams_html}
            </section>

            <section class="section" id="papers" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-green);">
                    Papers Overview
                </div>
                {papers_html}
            </section>

            <section class="section" id="team" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-purple);">
                    Research Team
                </div>
                {collaborators_html}
            </section>

            <section class="section" id="network" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-cyan);">
                    Collaboration Network
                </div>
                {network_html}
            </section>

            <section class="section" id="links" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-accent);">
                    Detailed Pages
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                    <a href="hft-papers.html" class="card" style="text-decoration: none; padding: 16px; border-left: 3px solid var(--color-primary);">
                        <h4 style="font-size: 13px; color: var(--color-dark); margin-bottom: 4px;">HFT Research</h4>
                        <p style="font-size: 11px; color: var(--color-text-muted);">Deutsche Borse market microstructure papers</p>
                    </a>
                    <a href="narratives-papers.html" class="card" style="text-decoration: none; padding: 16px; border-left: 3px solid var(--color-purple);">
                        <h4 style="font-size: 13px; color: var(--color-dark); margin-bottom: 4px;">Narratives Research</h4>
                        <p style="font-size: 11px; color: var(--color-text-muted);">NLP and narrative modeling papers</p>
                    </a>
                    <a href="research-catalog.html" class="card" style="text-decoration: none; padding: 16px; border-left: 3px solid var(--color-green);">
                        <h4 style="font-size: 13px; color: var(--color-dark); margin-bottom: 4px;">File Catalog</h4>
                        <p style="font-size: 11px; color: var(--color-text-muted);">Complete research file inventory</p>
                    </a>
                </div>
            </section>

        </div>

        {get_footer()}
        {openalex_script}
    </main>
</body>
</html>'''

def build_thesis_timeline_html() -> str:
    """Build visual timeline for PhD progress."""
    # PhD timeline milestones
    milestones = [
        {"year": "2023", "month": "Nov", "event": "PhD Start", "status": "completed", "icon": "start"},
        {"year": "2024", "month": "Mar", "event": "SLR Paper Submitted", "status": "completed", "icon": "paper"},
        {"year": "2024", "month": "Jun", "event": "HFT Paper 1 (SSRN)", "status": "completed", "icon": "paper"},
        {"year": "2025", "month": "Jan", "event": "TOPOL (EPIA)", "status": "completed", "icon": "paper"},
        {"year": "2025", "month": "Jun", "event": "Qualifier Exam", "status": "current", "icon": "exam"},
        {"year": "2025", "month": "Dec", "event": "HFT Paper 2", "status": "upcoming", "icon": "paper"},
        {"year": "2026", "month": "Jun", "event": "Thesis Draft", "status": "upcoming", "icon": "thesis"},
        {"year": "2026", "month": "Oct", "event": "Defense", "status": "upcoming", "icon": "defense"},
    ]

    items = []
    for i, m in enumerate(milestones):
        if m['status'] == 'completed':
            color = 'var(--color-green)'
            opacity = '1'
        elif m['status'] == 'current':
            color = 'var(--color-accent)'
            opacity = '1'
        else:
            color = 'var(--color-text-light)'
            opacity = '0.6'

        items.append(f'''
        <div style="display: flex; flex-direction: column; align-items: center; flex: 1; opacity: {opacity};">
            <div style="width: 12px; height: 12px; border-radius: 50%; background: {color}; border: 2px solid {color};"></div>
            <div style="font-size: 10px; font-weight: 600; color: {color}; margin-top: 4px;">{m['month']} {m['year']}</div>
            <div style="font-size: 9px; color: var(--color-text-muted); text-align: center; max-width: 70px;">{m['event']}</div>
        </div>''')

    return f'''
    <div style="position: relative; padding: 20px 0;">
        <!-- Progress line -->
        <div style="position: absolute; top: 26px; left: 5%; right: 5%; height: 2px; background: var(--color-border);"></div>
        <div style="position: absolute; top: 26px; left: 5%; width: 55%; height: 2px; background: var(--color-green);"></div>

        <!-- Milestones -->
        <div style="display: flex; justify-content: space-between; position: relative;">
            {"".join(items)}
        </div>
    </div>
    '''

def build_openalex_script(research_data: Dict) -> str:
    """Build JavaScript for OpenAlex citation fetching."""
    # Collect DOIs from papers
    dois = []
    for paper in research_data.get('papers', []):
        if paper.get('doi'):
            dois.append(paper['doi'])

    if not dois:
        return ""

    dois_json = json.dumps(dois)

    return f'''
<script>
// OpenAlex Citation Integration
const paperDOIs = {dois_json};

async function fetchCitations() {{
    for (const doi of paperDOIs) {{
        try {{
            const response = await fetch(`https://api.openalex.org/works/doi:${{doi}}`);
            if (response.ok) {{
                const data = await response.json();
                const citationCount = data.cited_by_count || 0;
                console.log(`${{doi}}: ${{citationCount}} citations`);
                // Update UI if element exists
                const elem = document.getElementById(`citations-${{doi.replace(/[^a-z0-9]/gi, '-')}}`);
                if (elem) {{
                    elem.textContent = `${{citationCount}} citations`;
                    elem.style.display = 'inline';
                }}
            }}
        }} catch (e) {{
            console.log(`Failed to fetch citations for ${{doi}}`);
        }}
    }}
}}

// Fetch citations on page load
document.addEventListener('DOMContentLoaded', fetchCitations);
</script>
'''

def build_thesis_chapters_html() -> str:
    """Build HTML for thesis chapters grid."""
    cards = []

    # Map paper_link values to actual page URLs
    link_page_map = {
        'hft': 'hft-papers.html',
        'narratives': 'narratives-papers.html',
        'slr': 'narratives-papers.html#slr',
        'quoniam': 'narratives-papers.html#quoniam',
        'topol': 'narratives-papers.html#topol',
    }

    for chapter in THESIS_CHAPTERS:
        status_badge = get_status_badge(chapter['status'])
        link_html = ""
        paper_link = chapter.get('paper_link')
        if paper_link and paper_link in link_page_map:
            link_html = f'<a href="{link_page_map[paper_link]}" style="font-size: 10px;">View related papers</a>'

        cards.append(f'''
        <div class="card" style="padding: 12px; border-left: 3px solid var(--color-primary);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                <h4 style="font-size: 12px; color: var(--color-dark);">Chapter {chapter['number']}: {html.escape(chapter['title'])}</h4>
                {status_badge}
            </div>
            <p style="font-size: 11px; color: var(--color-text-muted); margin-bottom: 6px;">{html.escape(chapter['description'])}</p>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="wp-tag" style="font-size: 10px;">{chapter['work_package']}</span>
                {link_html}
            </div>
        </div>''')

    return f'''<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px;">
        {"".join(cards)}
    </div>'''

def build_research_streams_html(research_data: Dict) -> str:
    """Build HTML for research streams."""
    cards = []

    for stream_id, stream in RESEARCH_STREAMS.items():
        paper_count = len(research_data.get('by_stream', {}).get(stream_id, []))

        cards.append(f'''
        <div class="card" style="padding: 12px;">
            <h4 style="font-size: 13px; color: var(--color-dark); margin-bottom: 4px;">{html.escape(stream.name)}</h4>
            <p style="font-size: 11px; color: var(--color-text-muted); margin-bottom: 8px;">{html.escape(stream.description)}</p>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span class="wp-tag" style="font-size: 10px;">{stream.work_package}</span>
                <span style="font-size: 10px; color: var(--color-text-muted);">{paper_count} paper(s)</span>
            </div>
        </div>''')

    return f'''<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px;">
        {"".join(cards)}
    </div>'''

def build_papers_summary_html(research_data: Dict) -> str:
    """Build HTML for papers summary by status."""
    status_counts = research_data.get('status_summary', {})

    items = []
    for status, count in status_counts.items():
        config = STATUS_CONFIG.get(status, STATUS_CONFIG['IN_PROGRESS'])
        items.append(f'''
        <div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: {config['color']}; border-radius: 6px;">
            <span style="font-size: 18px; font-weight: 700; color: {config['text_color']};">{count}</span>
            <span style="font-size: 11px; color: {config['text_color']};">{config['label']}</span>
        </div>''')

    return f'''<div style="display: flex; gap: 12px; flex-wrap: wrap;">
        {"".join(items)}
    </div>'''

def build_collaborators_html() -> str:
    """Build HTML for collaborators with ORCID badges."""
    cards = []

    for collab in COLLABORATORS:
        # ORCID badge
        orcid_html = ""
        if collab.get('orcid'):
            orcid_html = f'''
            <a href="https://orcid.org/{collab['orcid']}" target="_blank" rel="noopener noreferrer"
               style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; color: #a6ce39; text-decoration: none;">
                <img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" alt="ORCID" style="width: 14px; height: 14px;">
                {collab['orcid']}
            </a>'''

        # Email link
        email_html = ""
        if collab.get('email'):
            email_html = f'<a href="mailto:{collab["email"]}" style="font-size: 10px; color: var(--color-primary);">{collab["email"]}</a>'

        # Role badge color
        role_colors = {
            'PhD Researcher': 'var(--color-accent)',
            'Principal Investigator': 'var(--color-primary)',
            'Industry Collaborator': 'var(--color-green)',
            'Researcher': 'var(--color-purple)'
        }
        role_color = role_colors.get(collab['role'], 'var(--color-text-muted)')

        cards.append(f'''
        <div class="card" style="padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                <h4 style="font-size: 12px; color: var(--color-dark); margin: 0;">{html.escape(collab['name'])}</h4>
                <span style="font-size: 9px; background: {role_color}; color: white; padding: 2px 6px; border-radius: 3px;">{collab['role']}</span>
            </div>
            <p style="font-size: 10px; color: var(--color-text-muted); margin-bottom: 6px;">
                {', '.join(collab['affiliations'])}
            </p>
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                {orcid_html}
                {email_html}
            </div>
        </div>''')

    return f'''<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">
        {"".join(cards)}
    </div>'''

def build_collaboration_network_html() -> str:
    """Build SVG collaboration network visualization."""
    # Define node positions and connections
    # Center: Gabin Taibi, connected to all
    # Top: Joerg Osterrieder (PI)
    # Left: Stefan Schlamp (DB), Right: Axel Gross-Klussmann (Quoniam)
    # Bottom: Lucia Gomez Teijeiro

    nodes = [
        {"id": "gabin", "name": "Gabin Taibi", "role": "PhD", "x": 200, "y": 150, "color": "#d97706"},
        {"id": "joerg", "name": "J. Osterrieder", "role": "PI", "x": 200, "y": 50, "color": "#3b82f6"},
        {"id": "stefan", "name": "S. Schlamp", "role": "DB", "x": 80, "y": 120, "color": "#10b981"},
        {"id": "axel", "name": "A. Gross-Klussmann", "role": "Quoniam", "x": 320, "y": 120, "color": "#10b981"},
        {"id": "lucia", "name": "L. Gomez Teijeiro", "role": "UT", "x": 200, "y": 250, "color": "#8b5cf6"},
    ]

    edges = [
        ("gabin", "joerg"),
        ("gabin", "stefan"),
        ("gabin", "axel"),
        ("gabin", "lucia"),
        ("joerg", "stefan"),
        ("joerg", "lucia"),
    ]

    # Build SVG
    node_dict = {n["id"]: n for n in nodes}

    lines_svg = []
    for src, dst in edges:
        n1, n2 = node_dict[src], node_dict[dst]
        lines_svg.append(f'<line x1="{n1["x"]}" y1="{n1["y"]}" x2="{n2["x"]}" y2="{n2["y"]}" stroke="#e5e7eb" stroke-width="2"/>')

    nodes_svg = []
    for n in nodes:
        nodes_svg.append(f'''
        <g transform="translate({n["x"]}, {n["y"]})">
            <circle r="25" fill="{n["color"]}" opacity="0.9"/>
            <text y="4" text-anchor="middle" fill="white" font-size="9" font-weight="600">{n["role"]}</text>
        </g>
        <text x="{n["x"]}" y="{n["y"] + 40}" text-anchor="middle" fill="#374151" font-size="10">{n["name"]}</text>
        ''')

    return f'''
    <div style="display: flex; justify-content: center;">
        <svg width="400" height="300" viewBox="0 0 400 300" style="max-width: 100%;">
            <!-- Edges -->
            {"".join(lines_svg)}
            <!-- Nodes -->
            {"".join(nodes_svg)}
        </svg>
    </div>
    <p style="font-size: 10px; color: var(--color-text-muted); text-align: center; margin-top: 8px;">
        Research collaboration network: PhD Researcher (orange), PI (blue), Industry (green), Academic (purple)
    </p>
    '''

def generate_hft_papers_page(research_data: Dict, image_data: Optional[Dict] = None) -> str:
    """
    Generate hft-papers.html with Deutsche Borse research.

    Args:
        research_data: Research papers data
        image_data: Optional image collection data

    Returns:
        Complete HTML string
    """
    head = get_head_section(
        "HFT Research Papers",
        "Deutsche Borse high-frequency trading and market microstructure research using nanosecond-level data",
        "hft-papers.html"
    )

    # Get HFT papers
    hft_papers = research_data.get('by_stream', {}).get('hft', [])

    # Build papers HTML
    papers_html = build_papers_detail_html(hft_papers, "hft")

    # Build images gallery
    images_html = build_image_gallery_html(image_data, "hft") if image_data else ""

    # Build comparison modal
    comparison_html = get_paper_comparison_html(hft_papers)

    return f'''{head}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("hft-papers.html")}
    {get_sidebar("hft-papers.html")}

    <main class="main" id="main-content">
        <div style="background: var(--color-primary); padding: 20px; text-align: center;">
            <h1 style="color: white; font-size: 18px; margin-bottom: 4px;">Deutsche Borse HFT Research</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 11px;">Market microstructure analysis using nanosecond-level trading data from Eurex and Xetra</p>
        </div>

        <div class="container" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

            <section class="section" id="papers" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-primary);">
                    Research Papers ({len(hft_papers)})
                </div>
                {papers_html}
            </section>

            {f'''<section class="section" id="figures" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-accent);">
                    Analysis Figures
                </div>
                {images_html}
            </section>''' if images_html else ''}

            <div style="margin-top: 24px; padding: 12px; background: var(--color-bg-alt); border-radius: 6px;">
                <p style="font-size: 11px; color: var(--color-text-muted);">
                    <strong>Data Source:</strong> Deutsche Borse Group - Eurex and Xetra platforms<br>
                    <strong>Period:</strong> January 2021 - January 2024<br>
                    <strong>Collaboration:</strong> Stefan Schlamp (Deutsche Borse)
                </p>
            </div>

        </div>

        {get_footer()}
        {get_lightbox_html()}
        {comparison_html}
    </main>
</body>
</html>'''

def generate_narratives_papers_page(research_data: Dict, image_data: Optional[Dict] = None) -> str:
    """
    Generate narratives-papers.html with narrative research.

    Args:
        research_data: Research papers data
        image_data: Optional image collection data

    Returns:
        Complete HTML string
    """
    head = get_head_section(
        "Narratives Research Papers",
        "NLP and transformer-based narrative modeling research for financial markets",
        "narratives-papers.html"
    )

    # Get narrative-related papers
    narrative_streams = ['narratives', 'topol', 'slr', 'quoniam']
    all_papers = []
    for stream in narrative_streams:
        all_papers.extend(research_data.get('by_stream', {}).get(stream, []))

    # Build papers HTML by stream
    sections_html = []

    stream_configs = [
        ('topol', 'TOPOL Framework', 'var(--color-cyan)'),
        ('slr', 'Systematic Literature Review', 'var(--color-green)'),
        ('narratives', 'Macro Narratives', 'var(--color-purple)'),
        ('quoniam', 'Quoniam Collaboration', 'var(--color-accent)'),
    ]

    for stream_id, stream_name, color in stream_configs:
        papers = research_data.get('by_stream', {}).get(stream_id, [])
        if papers:
            papers_html = build_papers_detail_html(papers, stream_id)
            sections_html.append(f'''
            <section class="section" id="{stream_id}" style="margin-bottom: 24px;">
                <div class="section-title" style="font-size: 14px; font-weight: 600; color: var(--color-dark); margin-bottom: 12px; padding-bottom: 6px; border-bottom: 2px solid {color};">
                    {stream_name} ({len(papers)})
                </div>
                {papers_html}
            </section>''')

    # Build images gallery
    images_html = ""
    if image_data:
        # Filter images by narrative streams
        all_images = image_data.get('images', [])
        narrative_images = [img for img in all_images if img.get('stream') in narrative_streams]
        if narrative_images:
            images_html = build_image_gallery_html(image_data, narrative_streams)

    # Build comparison modal for all narrative papers
    comparison_html = get_paper_comparison_html(all_papers)

    return f'''{head}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("narratives-papers.html")}
    {get_sidebar("narratives-papers.html")}

    <main class="main" id="main-content">
        <div style="background: linear-gradient(135deg, var(--color-purple) 0%, var(--color-cyan) 100%); padding: 20px; text-align: center;">
            <h1 style="color: white; font-size: 18px; margin-bottom: 4px;">Narratives Research Papers</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 11px;">NLP and transformer-based narrative detection from financial text</p>
        </div>

        <div class="container" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

            {"".join(sections_html)}

            {f'''<section class="section" id="figures" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-accent);">
                    Analysis Figures
                </div>
                {images_html}
            </section>''' if images_html else ''}

        </div>

        {get_footer()}
        {get_lightbox_html()}
        {comparison_html}
    </main>
</body>
</html>'''

def generate_research_catalog_page(catalog_data: Dict) -> str:
    """
    Generate research-catalog.html with complete file listing.

    Args:
        catalog_data: File catalog data

    Returns:
        Complete HTML string
    """
    head = get_head_section(
        "Research File Catalog",
        "Complete inventory of PhD research files and resources",
        "research-catalog.html"
    )

    summary = catalog_data.get('summary', {})

    # Build summary cards
    summary_cards = f'''
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 24px;">
        <div class="card" style="padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: var(--color-primary);">{summary.get('tex_files', 0)}</div>
            <div style="font-size: 10px; color: var(--color-text-muted);">LaTeX Files</div>
        </div>
        <div class="card" style="padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: var(--color-green);">{summary.get('bib_files', 0)}</div>
            <div style="font-size: 10px; color: var(--color-text-muted);">Bibliographies</div>
        </div>
        <div class="card" style="padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: var(--color-purple);">{summary.get('png_files', 0)}</div>
            <div style="font-size: 10px; color: var(--color-text-muted);">Images</div>
        </div>
        <div class="card" style="padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: var(--color-accent);">{summary.get('pdf_files', 0)}</div>
            <div style="font-size: 10px; color: var(--color-text-muted);">PDFs</div>
        </div>
        <div class="card" style="padding: 12px; text-align: center;">
            <div style="font-size: 24px; font-weight: 700; color: var(--color-dark);">{summary.get('total_files', 0)}</div>
            <div style="font-size: 10px; color: var(--color-text-muted);">Total Files</div>
        </div>
    </div>'''

    # Build by-stream breakdown
    by_stream = catalog_data.get('by_stream', {})
    stream_items = []
    for stream, count in sorted(by_stream.items(), key=lambda x: -x[1]):
        stream_name = RESEARCH_STREAMS[stream].name if stream in RESEARCH_STREAMS else stream.title()
        stream_items.append(f'''
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid var(--color-border);">
            <span style="font-size: 11px;">{stream_name}</span>
            <span style="font-size: 11px; font-weight: 600;">{count}</span>
        </div>''')

    # Build file table (show all files with search/filter)
    files = catalog_data.get('files', [])
    table_rows = []
    for f in files:
        ext_color = {
            '.tex': 'var(--color-primary)',
            '.bib': 'var(--color-green)',
            '.png': 'var(--color-purple)',
            '.pdf': 'var(--color-accent)'
        }.get(f['extension'], 'var(--color-text-muted)')

        table_rows.append(f'''
        <tr data-filename="{html.escape(f['filename'].lower())}" data-ext="{f['extension']}" data-stream="{f['research_stream']}">
            <td style="font-size: 11px; padding: 6px 8px;">{html.escape(f['filename'])}</td>
            <td style="font-size: 10px; padding: 6px 8px;"><span style="color: {ext_color}; font-weight: 500;">{f['extension']}</span></td>
            <td style="font-size: 10px; padding: 6px 8px;">{f['research_stream']}</td>
            <td style="font-size: 10px; padding: 6px 8px;">{f['size_kb']:.1f} KB</td>
        </tr>''')

    # Get unique extensions and streams for filters
    extensions = sorted(set(f['extension'] for f in files))
    streams = sorted(set(f['research_stream'] for f in files))

    ext_options = ''.join(f'<option value="{ext}">{ext}</option>' for ext in extensions)
    stream_options = ''.join(f'<option value="{s}">{RESEARCH_STREAMS[s].name if s in RESEARCH_STREAMS else s.title()}</option>' for s in streams)

    return f'''{head}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("research-catalog.html")}
    {get_sidebar("research-catalog.html")}

    <main class="main" id="main-content">
        <div style="background: var(--color-dark); padding: 20px; text-align: center;">
            <h1 style="color: white; font-size: 18px; margin-bottom: 4px;">Research File Catalog</h1>
            <p style="color: rgba(255,255,255,0.8); font-size: 11px;">Complete inventory of PhD research files ({summary.get('total_size_mb', 0):.1f} MB)</p>
        </div>

        <div class="container" style="max-width: 1000px; margin: 0 auto; padding: 20px;">

            <section class="section" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-primary);">
                    Summary
                </div>
                {summary_cards}
            </section>

            <section class="section" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-purple);">
                    By Research Stream
                </div>
                <div class="card" style="padding: 12px;">
                    {"".join(stream_items)}
                </div>
            </section>

            <section class="section" style="margin-bottom: 32px;">
                <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-green);">
                    File Listing
                </div>

                <!-- Search and Filter Controls -->
                <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center;">
                    <div style="flex: 1; min-width: 200px;">
                        <input type="text" id="search-input" placeholder="Search files..."
                               style="width: 100%; padding: 8px 12px; border: 1px solid var(--color-border); border-radius: 6px; font-size: 12px;"
                               oninput="filterTable()">
                    </div>
                    <div>
                        <select id="ext-filter" onchange="filterTable()"
                                style="padding: 8px 12px; border: 1px solid var(--color-border); border-radius: 6px; font-size: 11px;">
                            <option value="">All Types</option>
                            {ext_options}
                        </select>
                    </div>
                    <div>
                        <select id="stream-filter" onchange="filterTable()"
                                style="padding: 8px 12px; border: 1px solid var(--color-border); border-radius: 6px; font-size: 11px;">
                            <option value="">All Streams</option>
                            {stream_options}
                        </select>
                    </div>
                    <div id="result-count" style="font-size: 11px; color: var(--color-text-muted);">
                        Showing {len(files)} files
                    </div>
                </div>

                <div style="overflow-x: auto; max-height: 500px; overflow-y: auto;">
                    <table id="file-table" class="inventory-table" style="width: 100%; border-collapse: collapse; font-size: 11px;">
                        <thead style="position: sticky; top: 0; background: var(--color-bg-alt);">
                            <tr>
                                <th style="text-align: left; padding: 8px; font-weight: 600; cursor: pointer;" onclick="sortTable(0)">Filename</th>
                                <th style="text-align: left; padding: 8px; font-weight: 600; cursor: pointer;" onclick="sortTable(1)">Type</th>
                                <th style="text-align: left; padding: 8px; font-weight: 600; cursor: pointer;" onclick="sortTable(2)">Stream</th>
                                <th style="text-align: left; padding: 8px; font-weight: 600; cursor: pointer;" onclick="sortTable(3)">Size</th>
                            </tr>
                        </thead>
                        <tbody id="file-tbody">
                            {"".join(table_rows)}
                        </tbody>
                    </table>
                </div>
                <p style="font-size: 10px; color: var(--color-text-muted); margin-top: 8px; text-align: center;">
                    Full catalog available in data/file_catalog.json
                </p>
            </section>

<script>
function filterTable() {{
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const extFilter = document.getElementById('ext-filter').value;
    const streamFilter = document.getElementById('stream-filter').value;
    const rows = document.querySelectorAll('#file-tbody tr');
    let visibleCount = 0;

    rows.forEach(row => {{
        const filename = row.dataset.filename;
        const ext = row.dataset.ext;
        const stream = row.dataset.stream;

        const matchesSearch = filename.includes(searchTerm);
        const matchesExt = !extFilter || ext === extFilter;
        const matchesStream = !streamFilter || stream === streamFilter;

        if (matchesSearch && matchesExt && matchesStream) {{
            row.style.display = '';
            visibleCount++;
        }} else {{
            row.style.display = 'none';
        }}
    }});

    document.getElementById('result-count').textContent = `Showing ${{visibleCount}} files`;
}}

let sortDirection = {{}};
function sortTable(columnIndex) {{
    const table = document.getElementById('file-table');
    const tbody = document.getElementById('file-tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    sortDirection[columnIndex] = !sortDirection[columnIndex];
    const dir = sortDirection[columnIndex] ? 1 : -1;

    rows.sort((a, b) => {{
        let aVal = a.cells[columnIndex].textContent.trim();
        let bVal = b.cells[columnIndex].textContent.trim();

        // Handle size column (numeric sort)
        if (columnIndex === 3) {{
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
            return (aVal - bVal) * dir;
        }}

        return aVal.localeCompare(bVal) * dir;
    }});

    rows.forEach(row => tbody.appendChild(row));
}}
</script>

        </div>

        {get_footer()}
    </main>
</body>
</html>'''

def build_papers_detail_html(papers: List[Dict], stream: str) -> str:
    """Build detailed paper cards HTML."""
    if not papers:
        return '<p style="font-size: 11px; color: var(--color-text-muted);">No papers found for this stream.</p>'

    cards = []
    for paper in papers:
        status_badge = get_status_badge(paper.get('status', 'IN_PROGRESS'))

        # Build links
        links = []
        if paper.get('ssrn_url'):
            links.append(f'<a href="{paper["ssrn_url"]}" target="_blank" rel="noopener noreferrer" style="font-size: 10px;">SSRN</a>')
        if paper.get('arxiv_url'):
            links.append(f'<a href="{paper["arxiv_url"]}" target="_blank" rel="noopener noreferrer" style="font-size: 10px;">arXiv</a>')
        if paper.get('doi'):
            links.append(f'<a href="https://doi.org/{paper["doi"]}" target="_blank" rel="noopener noreferrer" style="font-size: 10px;">DOI</a>')

        links_html = " | ".join(links) if links else ""

        # PDF download button
        pdf_html = ""
        if paper.get('arxiv_url'):
            # arXiv: convert /abs/ to /pdf/
            pdf_url = paper['arxiv_url'].replace('/abs/', '/pdf/') + '.pdf'
            pdf_html = f'<a href="{pdf_url}" target="_blank" rel="noopener noreferrer" class="pdf-download-btn" style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; background: var(--color-accent); color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; margin-left: 8px;">PDF</a>'
        elif paper.get('ssrn_url') and 'abstract_id=' in paper['ssrn_url']:
            # SSRN: extract ID and build download URL
            import re
            ssrn_match = re.search(r'abstract_id=(\d+)', paper['ssrn_url'])
            if ssrn_match:
                ssrn_id = ssrn_match.group(1)
                pdf_url = f"https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{ssrn_id}.pdf"
                pdf_html = f'<a href="{pdf_url}" target="_blank" rel="noopener noreferrer" class="pdf-download-btn" style="display: inline-flex; align-items: center; gap: 4px; font-size: 10px; background: var(--color-accent); color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; margin-left: 8px;">PDF</a>'

        # Keywords
        keywords_html = ""
        if paper.get('keywords'):
            kw_badges = [f'<span style="font-size: 9px; background: var(--color-bg-alt); padding: 2px 6px; border-radius: 3px;">{html.escape(kw)}</span>' for kw in paper['keywords'][:5]]
            keywords_html = f'<div style="display: flex; gap: 4px; flex-wrap: wrap; margin-top: 6px;">{"".join(kw_badges)}</div>'

        cards.append(f'''
        <div class="card" style="padding: 12px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                <h4 style="font-size: 13px; color: var(--color-dark); margin: 0;">{html.escape(paper.get('title', 'Untitled'))}</h4>
                {status_badge}
            </div>
            <p style="font-size: 11px; color: var(--color-text-muted); margin-bottom: 4px;">
                {html.escape(paper.get('authors_string', ''))}
            </p>
            <p style="font-size: 10px; color: var(--color-text-light); margin-bottom: 6px;">
                {html.escape(paper.get('venue', ''))} ({paper.get('year', '')})
            </p>
            <p style="font-size: 11px; color: var(--color-text); margin-bottom: 8px;">
                {html.escape(paper.get('abstract_short', ''))}
            </p>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <span class="wp-tag" style="font-size: 10px;">{paper.get('work_package', '')}</span>
                {links_html}
                {pdf_html}
                <button class="compare-btn" onclick="toggleCompare('{paper.get('id', '')}', this)">Compare</button>
            </div>
            {keywords_html}
        </div>''')

    return "".join(cards)

def build_image_gallery_html(image_data: Optional[Dict], streams) -> str:
    """Build image gallery HTML with lightbox support."""
    if not image_data:
        return ""

    # Handle single stream or list of streams
    if isinstance(streams, str):
        streams = [streams]

    images = []
    for stream in streams:
        stream_images = [
            img for img in image_data.get('images', [])
            if img.get('stream') == stream and img.get('web_path')
        ]
        images.extend(stream_images[:8])  # Limit to 8 per stream

    if not images:
        return ""

    gallery_items = []
    for img in images[:16]:  # Max 16 images
        caption = f"{img['filename']} - {img['category']}"
        gallery_items.append(f'''
        <div class="gallery-item" style="background: var(--color-bg-alt); border-radius: 6px; overflow: hidden;"
             onclick="openLightbox('{img['web_path']}', '{html.escape(caption)}')"
             tabindex="0"
             role="button"
             aria-label="View {html.escape(img['filename'])} in full size">
            <img src="{img['web_path']}" alt="{html.escape(img['filename'])}" style="width: 100%; height: 120px; object-fit: cover;">
            <div style="padding: 6px;">
                <p style="font-size: 10px; color: var(--color-text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {html.escape(img['filename'])}
                </p>
                <p style="font-size: 9px; color: var(--color-text-light);">{img['category']}</p>
            </div>
        </div>''')

    return f'''<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px;">
        {"".join(gallery_items)}
    </div>'''

# =============================================================================
# MAIN GENERATOR
# =============================================================================

class HTMLGenerator:
    """Main HTML generator class."""

    def __init__(self, target_dir: Path = TARGET_REPO):
        self.target_dir = target_dir

    def generate_all_pages(
        self,
        research_data: Dict,
        catalog_data: Dict,
        image_data: Optional[Dict] = None,
        dry_run: bool = False
    ) -> Dict[str, Path]:
        """
        Generate all HTML pages.

        Args:
            research_data: Research papers data
            catalog_data: File catalog data
            image_data: Optional image collection data
            dry_run: If True, don't write files

        Returns:
            Dictionary mapping page name to output path
        """
        outputs = {}

        # Generate overview page
        overview_html = generate_research_overview_page(research_data, image_data)
        overview_path = self.target_dir / "gabin-research.html"
        if not dry_run:
            overview_path.write_text(overview_html, encoding='utf-8')
        outputs['gabin-research'] = overview_path
        logger.info(f"Generated: gabin-research.html")

        # Generate HFT papers page
        hft_html = generate_hft_papers_page(research_data, image_data)
        hft_path = self.target_dir / "hft-papers.html"
        if not dry_run:
            hft_path.write_text(hft_html, encoding='utf-8')
        outputs['hft-papers'] = hft_path
        logger.info(f"Generated: hft-papers.html")

        # Generate narratives papers page
        narratives_html = generate_narratives_papers_page(research_data, image_data)
        narratives_path = self.target_dir / "narratives-papers.html"
        if not dry_run:
            narratives_path.write_text(narratives_html, encoding='utf-8')
        outputs['narratives-papers'] = narratives_path
        logger.info(f"Generated: narratives-papers.html")

        # Generate catalog page
        catalog_html = generate_research_catalog_page(catalog_data)
        catalog_path = self.target_dir / "research-catalog.html"
        if not dry_run:
            catalog_path.write_text(catalog_html, encoding='utf-8')
        outputs['research-catalog'] = catalog_path
        logger.info(f"Generated: research-catalog.html")

        return outputs

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test with sample data
    sample_research = {
        'paper_count': 5,
        'by_stream': {},
        'status_summary': {'SUBMITTED': 2, 'IN_PROGRESS': 2, 'PLANNING': 1}
    }

    sample_catalog = {
        'summary': {
            'tex_files': 93,
            'bib_files': 17,
            'png_files': 124,
            'pdf_files': 64,
            'total_files': 315,
            'total_size_mb': 45.2
        },
        'files': [],
        'by_stream': {'hft': 50, 'narratives': 100, 'slr': 80, 'quoniam': 85}
    }

    generator = HTMLGenerator()
    outputs = generator.generate_all_pages(sample_research, sample_catalog, dry_run=True)
    print(f"Would generate {len(outputs)} pages")
