"""
COST Action CA19130 Integration Script

Generates COST Action showcase pages for the Narrative Digital Finance website.
Reads data from COST_Network repository and generates HTML pages + JSON data files.

Author: Gabin Taibi, Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)

Usage:
    python cost_integration.py              # Full generation
    python cost_integration.py --dry-run    # Preview without writing files
    python cost_integration.py --verbose    # Enable debug logging
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import html

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# COST Network data source
COST_DATA_SOURCE = Path(r"D:\Joerg\Research\slides\COST_Network\data")

# Target repository
TARGET_REPO = Path(r"D:\Joerg\Research\slides\Narrative-Digital-Finance\repo")
DATA_DEST = TARGET_REPO / "data"

# Site configuration
SITE_CONFIG = {
    "base_url": "https://digital-ai-finance.github.io/Narrative-Digital-Finance/",
    "site_title": "Narrative Digital Finance",
    "project_grant": "SNSF Grant IZCOZ0_213370",
    "favicon": "favicon.svg",
    "styles": "styles.css",
    "font_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
}

# SNSF-COST Work Package to Working Group alignment
WP_WG_ALIGNMENT = {
    "WP1": {
        "name": "Text Data & Text Analytics",
        "cost_wgs": ["WG1"],
        "alignment": "Strong - Both focus on ML/NLP for financial transparency"
    },
    "WP2": {
        "name": "Structural Breaks & Bubbles",
        "cost_wgs": ["WG3"],
        "alignment": "Strong - Time series analysis and interpretable ML"
    },
    "WP3": {
        "name": "Narratives for Structural Breaks",
        "cost_wgs": ["WG1", "WG2"],
        "alignment": "Moderate - Narrative analysis uses XAI concepts"
    },
    "WP4": {
        "name": "Multidimensional AI/ML",
        "cost_wgs": ["WG3"],
        "alignment": "Strong - Market microstructure and HFT analysis"
    }
}

# Named SNSF-COST collaborators
SNSF_COST_COLLABORATORS = [
    {
        "name": "Prof. Wolfgang Karl Hardle",
        "institution": "Humboldt-University Berlin",
        "country": "Germany",
        "role": "WG1 Leader, PhD examination, co-author",
        "cost_role": "Working Group 1 Leader"
    },
    {
        "name": "Prof. Daniel Traian Pele",
        "institution": "Bucharest University of Economic Studies",
        "country": "Romania",
        "role": "COST network, PhD training",
        "cost_role": "WG1 Co-Leader"
    },
    {
        "name": "Prof. Codruta Mare",
        "institution": "Babes-Bolyai University",
        "country": "Romania",
        "role": "Co-author 'Multimodal Influence'",
        "cost_role": "Grant Awarding Coordinator"
    },
    {
        "name": "Dr. Karolina Bolesta",
        "institution": "SGH Warsaw School of Economics",
        "country": "Poland",
        "role": "Co-author, COST network",
        "cost_role": "Virtual Grant Co-Coordinator"
    },
    {
        "name": "Dr. Stefan Schlamp",
        "institution": "Deutsche Borse AG",
        "country": "Germany",
        "role": "HFT data access, joint publications",
        "cost_role": "Industry Partner"
    }
]

logger = logging.getLogger(__name__)

# =============================================================================
# DATA LOADING
# =============================================================================

def load_cost_json(filepath: Path, required: bool = True) -> dict:
    """Load and validate a COST JSON file."""
    if not filepath.exists():
        if required:
            logger.error(f"Required file not found: {filepath}")
            return {}
        logger.warning(f"Optional file not found: {filepath}")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Loaded {filepath.name}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return {}


def load_all_cost_data() -> Dict[str, Any]:
    """Load all relevant COST data files."""
    data = {}

    # Core files
    files_to_load = {
        "final_report": "final_report_full.json",
        "leadership": "leadership.json",
        "summary_stats": "summary_statistics.json",
        "wg_members": "wg_members.json",
        "mc_members": "mc_members.json",
        "country_stats": "country_statistics_full.json",
        "meetings": "meetings_detailed.json",
        "training_schools": "training_schools_detailed.json",
        "stsm": "stsm_full.json",
        "virtual_mobility": "virtual_mobility_full.json",
        "publications": "publications_main.json",
        "deliverables": "deliverables.json",
        "working_groups": "working_groups.json",
    }

    for key, filename in files_to_load.items():
        filepath = COST_DATA_SOURCE / filename
        data[key] = load_cost_json(filepath, required=False)

    return data


# =============================================================================
# HTML GENERATION COMPONENTS
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
    <meta name="keywords" content="COST Action, CA19130, FinAI, fintech, AI in finance, SNSF, research network">
    <meta name="author" content="Prof. Dr. Joerg Osterrieder">
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
        ("cost-action.html", "COST Action"),
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


def get_sidebar_cost(active_page: str = "") -> str:
    """Generate sidebar with COST Action section."""

    def sidebar_link(href: str, label: str) -> str:
        if href == active_page:
            return f'<a href="{href}" class="sidebar-link" style="background:#eff6ff;color:#3b82f6;border-radius:4px">{label}</a>'
        return f'<a href="{href}" class="sidebar-link">{label}</a>'

    return f'''<aside class="sidebar" aria-label="Main navigation">
    <div class="sidebar-section">
        <div class="sidebar-title">Navigation</div>
        <ul class="sidebar-nav">
            <li><a href="index.html">Home</a></li>
            <li><a href="index.html#overview">Overview</a></li>
            <li><a href="index.html#team">Team</a></li>
            <li><a href="index.html#publications">Publications</a></li>
        </ul>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">COST Action CA19130</div>
        {sidebar_link("cost-action.html", "SNSF Integration")}
        {sidebar_link("cost-network.html", "Network (420+)")}
        {sidebar_link("cost-events.html", "Events (150+)")}
        {sidebar_link("cost-publications.html", "Publications (7K+)")}
        {sidebar_link("cost-mobility.html", "Mobility Grants")}
        {sidebar_link("cost-resources.html", "Resources")}
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Pages</div>
        <a href="objectives.html" class="sidebar-link">Research Objectives</a>
        <a href="report.html" class="sidebar-link">Final Report</a>
        <a href="inventory.html" class="sidebar-link">Evidence Inventory</a>
        <a href="dmp.html" class="sidebar-link">Data Management Plan</a>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Links</div>
        <a href="https://www.cost.eu/actions/CA19130/" class="sidebar-link" target="_blank" rel="noopener noreferrer">COST Portal</a>
        <a href="https://wiki.fin-ai.eu/" class="sidebar-link" target="_blank" rel="noopener noreferrer">FinAI Wiki</a>
        <a href="https://www.ai-in-finance.eu/" class="sidebar-link" target="_blank" rel="noopener noreferrer">AI-in-Finance.eu</a>
    </div>
    <div class="sidebar-divider"></div>
    <div class="sidebar-section">
        <div class="sidebar-title">Funding</div>
        <div class="sidebar-badge">
            <a href="https://www.mysnf.ch/grants/grant.aspx?id=c8d8081e-6eee-4418-92bb-21dc2c89566a" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/SNSF-red?style=flat-square" alt="SNSF"></a>
            <a href="https://cordis.europa.eu/project/id/101119635" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/EU-blue?style=flat-square" alt="EU"></a>
        </div>
    </div>
</aside>'''


def get_footer() -> str:
    """Generate standard footer."""
    return '''<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div><h5>Project</h5><a href="index.html#overview">Overview</a><a href="index.html#results">Results</a></div>
            <div><h5>Team</h5><a href="index.html#team">Members</a><a href="index.html#collaborations">Collaborations</a></div>
            <div><h5>COST Action</h5><a href="cost-action.html">SNSF Integration</a><a href="cost-network.html">Network</a></div>
            <div><h5>Funding</h5><a href="https://data.snf.ch/grants/grant/213370">SNSF Data</a><a href="https://www.cost.eu/actions/CA19130/">COST Portal</a></div>
        </div>
        <div class="footer-bottom">Funded by EU (Grant No. 101119635) and SNSF (Grant IZCOZ0_213370) | 2023-2026 Narrative Digital Finance</div>
    </div>
</footer>
<script async>
(function(){
  var img = new Image();
  img.src = 'https://analytics-narrative-digital-finance.digital-ai-finance.workers.dev/t?p=' + encodeURIComponent(location.pathname) + '&r=' + encodeURIComponent(document.referrer);
})();
</script>
<div class="copyright-footer">(c) Prof. Dr. Joerg Osterrieder 2025</div>
</body>
</html>'''


# =============================================================================
# PAGE GENERATORS
# =============================================================================

def generate_cost_action_page(data: Dict[str, Any]) -> str:
    """Generate the main COST Action hub page (cost-action.html)."""

    # Extract stats from data
    final_report = data.get("final_report", {})
    summary = final_report.get("summary", {})
    stats = summary.get("stats", {})
    summary_stats = data.get("summary_stats", {})
    leadership = data.get("leadership", {})

    # Key statistics
    researchers = stats.get("researchers", 420)
    countries = stats.get("countries", 55)
    cost_countries = stats.get("cost_countries", 39)
    citations = stats.get("citations", 10000)
    meetings = summary_stats.get("total_meetings", 52)
    stsms = summary_stats.get("total_stsms", 27)
    training_schools = summary_stats.get("total_training_schools", 7)
    total_budget = summary_stats.get("total_budget", 963654)

    # Working groups from leadership data
    wgs = leadership.get("working_groups", [])
    wg_cards = ""
    for wg in wgs:
        wg_cards += f'''<div class="card">
            <h4>WG{wg.get("number", "")}: {wg.get("title", "")}</h4>
            <p><strong>Leader:</strong> {wg.get("leader", "")}</p>
            <p><strong>Participants:</strong> {wg.get("participants", 0)}</p>
        </div>'''

    # WP-WG alignment table
    alignment_rows = ""
    for wp, info in WP_WG_ALIGNMENT.items():
        wgs_str = ", ".join(info["cost_wgs"])
        alignment_rows += f'''<tr>
            <td><strong>{wp}</strong>: {info["name"]}</td>
            <td>{wgs_str}</td>
            <td>{info["alignment"]}</td>
        </tr>'''

    # Collaborators table
    collab_rows = ""
    for collab in SNSF_COST_COLLABORATORS:
        collab_rows += f'''<tr>
            <td>{collab["name"]}</td>
            <td>{collab["institution"]}</td>
            <td>{collab["country"]}</td>
            <td>{collab["cost_role"]}</td>
        </tr>'''

    page_content = f'''{get_head_section(
        "COST Action CA19130 - SNSF Integration",
        "How SNSF Narrative Digital Finance project integrated with COST Action CA19130 FinAI network - 420+ researchers, 55 countries",
        "cost-action.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-action.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / COST Action CA19130</div>

        <div class="hero" style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 30px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 28px; margin-bottom: 8px;">COST Action CA19130: FinAI Network</h1>
            <p style="font-size: 14px; opacity: 0.9; margin-bottom: 16px;">Fintech and Artificial Intelligence in Finance - How SNSF Integration Amplified Research Impact</p>
            <div style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; font-size: 12px;">
                <div><div style="font-size: 24px; font-weight: 700;">{researchers}+</div><div style="opacity: 0.8;">Researchers</div></div>
                <div><div style="font-size: 24px; font-weight: 700;">{countries}</div><div style="opacity: 0.8;">Countries</div></div>
                <div><div style="font-size: 24px; font-weight: 700;">{meetings}</div><div style="opacity: 0.8;">Meetings</div></div>
                <div><div style="font-size: 24px; font-weight: 700;">{citations:,}+</div><div style="opacity: 0.8;">Citations</div></div>
                <div><div style="font-size: 24px; font-weight: 700;">EUR {total_budget/1000:.0f}K</div><div style="opacity: 0.8;">Budget</div></div>
            </div>
        </div>

        <section class="section">
            <div class="section-title">SNSF-COST Synergy Story</div>
            <div class="highlight" style="border-left: 4px solid var(--color-primary); padding: 16px; background: #f8fafc;">
                <h4 style="margin: 0 0 8px 0;">The Dual Leadership Advantage</h4>
                <p style="margin: 0; font-size: 12px;">Prof. Joerg Osterrieder serves as both <strong>SNSF Project Principal Investigator</strong> and <strong>COST Action Chair</strong>, creating a unique bridge between national research funding and pan-European collaboration. This dual role enabled the SNSF project to leverage an existing network of 420+ researchers across 55 countries.</p>
            </div>
            <div class="grid grid-2" style="margin-top: 16px;">
                <div class="card">
                    <h4>What SNSF Gained from COST</h4>
                    <ul style="font-size: 11px; margin: 0; padding-left: 16px;">
                        <li>Pre-existing network of {researchers}+ researchers</li>
                        <li>PhD training via COST FinAI PhD School 2024</li>
                        <li>Conference platform (7th/8th European Conferences at BFH)</li>
                        <li>Joint publications with 30+ COST co-authors</li>
                        <li>Industry connections (Deutsche Borse, Quoniam)</li>
                    </ul>
                </div>
                <div class="card">
                    <h4>What SNSF Contributed to COST</h4>
                    <ul style="font-size: 11px; margin: 0; padding-left: 16px;">
                        <li>Leadership as Action Chair (2020-2024)</li>
                        <li>Conference hosting in Bern (2023, 2024)</li>
                        <li>TOPol framework and HFT classification methods</li>
                        <li>Bridge to MSCA Industrial Doctoral Network (EUR 4.5M)</li>
                        <li>Research case studies for PhD training</li>
                    </ul>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Work Package to Working Group Alignment</div>
            <p style="font-size: 11px; margin-bottom: 12px;">The SNSF project's work packages align with COST Action working groups, enabling collaborative research across the network.</p>
            <table class="pub-table" style="font-size: 11px;">
                <thead>
                    <tr><th>SNSF Work Package</th><th>COST Working Group</th><th>Alignment</th></tr>
                </thead>
                <tbody>
                    {alignment_rows}
                </tbody>
            </table>
        </section>

        <section class="section">
            <div class="section-title">Working Groups Overview</div>
            <div class="grid grid-3">
                {wg_cards if wg_cards else '''
                <div class="card"><h4>WG1: Transparency in FinTech</h4><p>Leader: Prof. Wolfgang Hardle</p><p>281 participants</p></div>
                <div class="card"><h4>WG2: XAI Models</h4><p>Leader: Prof. Petre Lameski</p><p>254 participants</p></div>
                <div class="card"><h4>WG3: Investment Products</h4><p>Leader: Prof. Peter Schwendner</p><p>223 participants</p></div>
                '''}
            </div>
        </section>

        <section class="section">
            <div class="section-title">Key COST Collaborators</div>
            <p style="font-size: 11px; margin-bottom: 12px;">Named collaborators from the COST network who contributed to SNSF research outputs.</p>
            <table class="pub-table" style="font-size: 11px;">
                <thead>
                    <tr><th>Name</th><th>Institution</th><th>Country</th><th>COST Role</th></tr>
                </thead>
                <tbody>
                    {collab_rows}
                </tbody>
            </table>
        </section>

        <section class="section">
            <div class="section-title">Key Milestones</div>
            <div class="timeline">
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Sep 2020</div>
                    <div style="font-size: 11px;">COST Action CA19130 launched</div>
                </div>
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Jul 2023</div>
                    <div style="font-size: 11px;">SNSF Narrative Digital Finance project starts</div>
                </div>
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Sep 2023</div>
                    <div style="font-size: 11px;">7th European COST Conference on AI in Finance (Bern)</div>
                </div>
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Jun 2024</div>
                    <div style="font-size: 11px;">COST FinAI PhD School (University of Twente)</div>
                </div>
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Sep 2024</div>
                    <div style="font-size: 11px;">8th European COST Conference on AI in Finance (Bern)</div>
                </div>
                <div class="timeline-item" style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="min-width: 80px; font-weight: 600; font-size: 11px;">Oct 2024</div>
                    <div style="font-size: 11px;">COST Action CA19130 successfully concluded</div>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Explore COST Action</div>
            <div class="grid grid-3">
                <a href="cost-network.html" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Network</h4>
                    <p style="font-size: 11px;">{researchers}+ researchers from {countries} countries</p>
                </a>
                <a href="cost-events.html" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Events</h4>
                    <p style="font-size: 11px;">{meetings} meetings, {training_schools} training schools</p>
                </a>
                <a href="cost-publications.html" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Publications</h4>
                    <p style="font-size: 11px;">{citations:,}+ citations from network research</p>
                </a>
                <a href="cost-mobility.html" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Mobility</h4>
                    <p style="font-size: 11px;">{stsms} STSMs, {summary_stats.get("total_virtual_mobility", 39)} Virtual Mobility grants</p>
                </a>
                <a href="cost-resources.html" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Resources</h4>
                    <p style="font-size: 11px;">Platforms, deliverables, final report</p>
                </a>
                <a href="https://www.cost.eu/actions/CA19130/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>COST Portal</h4>
                    <p style="font-size: 11px;">Official COST Action page</p>
                </a>
            </div>
        </section>

        {get_footer()}'''

    return page_content


def generate_cost_network_page(data: Dict[str, Any]) -> str:
    """Generate the COST network page (cost-network.html)."""

    final_report = data.get("final_report", {})
    summary = final_report.get("summary", {})
    stats = summary.get("stats", {})
    country_stats = data.get("country_stats", {})
    wg_members = data.get("wg_members", {})

    researchers = stats.get("researchers", 420)
    countries = stats.get("countries", 55)
    cost_countries = stats.get("cost_countries", 39)

    # Country list from final report
    participant_countries = final_report.get("participants", {}).get("countries", [])
    country_rows = ""
    for i, country in enumerate(participant_countries[:30], 1):  # First 30 countries
        country_rows += f'''<tr>
            <td>{i}</td>
            <td>{country.get("code", "")}</td>
            <td>{country.get("date", "")}</td>
        </tr>'''

    page_content = f'''{get_head_section(
        "Network & Researchers",
        f"COST Action CA19130 network: {researchers}+ researchers from {countries} countries including {cost_countries} COST member countries",
        "cost-network.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-network.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="cost-action.html">COST Action</a> / Network</div>

        <div class="hero" style="background: var(--color-purple); padding: 24px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 8px;">Global Research Network</h1>
            <p style="font-size: 13px; opacity: 0.9;">{researchers}+ Researchers | {countries} Countries | {cost_countries} COST Countries</p>
        </div>

        <section class="section">
            <div class="section-title">Network Statistics</div>
            <div class="grid grid-4">
                <div class="output-card"><div class="output-num">{researchers}+</div><div class="output-lbl">Researchers</div></div>
                <div class="output-card"><div class="output-num">{countries}</div><div class="output-lbl">Countries</div></div>
                <div class="output-card"><div class="output-num">{cost_countries}</div><div class="output-lbl">COST Countries</div></div>
                <div class="output-card"><div class="output-num">{countries - cost_countries}</div><div class="output-lbl">Partner Countries</div></div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Working Group Participation</div>
            <div class="grid grid-3">
                <div class="card">
                    <h4>WG1: Transparency in FinTech</h4>
                    <div style="font-size: 24px; font-weight: 700; color: var(--color-primary);">281</div>
                    <p style="font-size: 11px; margin: 4px 0;">participants</p>
                    <p style="font-size: 10px; color: #64748b;">ML, Big Data Mining, Blockchain, NLP</p>
                </div>
                <div class="card">
                    <h4>WG2: XAI Models</h4>
                    <div style="font-size: 24px; font-weight: 700; color: var(--color-purple);">254</div>
                    <p style="font-size: 11px; margin: 4px 0;">participants</p>
                    <p style="font-size: 10px; color: #64748b;">Credit Scoring, Risk Assessment, Explainability</p>
                </div>
                <div class="card">
                    <h4>WG3: Investment Products</h4>
                    <div style="font-size: 24px; font-weight: 700; color: var(--color-green);">223</div>
                    <p style="font-size: 11px; margin: 4px 0;">participants</p>
                    <p style="font-size: 10px; color: #64748b;">Asset Management, Smart Beta, Market Microstructure</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Participating Countries</div>
            <p style="font-size: 11px; margin-bottom: 12px;">Countries joined the COST Action between 2020-2024. Showing first 30 of {len(participant_countries)} countries.</p>
            <table class="pub-table" style="font-size: 11px;">
                <thead>
                    <tr><th>#</th><th>Country Code</th><th>Join Date</th></tr>
                </thead>
                <tbody>
                    {country_rows}
                </tbody>
            </table>
            <p style="font-size: 10px; color: #64748b; margin-top: 8px;">See full country list at <a href="https://www.cost.eu/actions/CA19130/" target="_blank" rel="noopener noreferrer">COST Portal</a></p>
        </section>

        <section class="section">
            <div class="section-title">Diversity & Inclusion</div>
            <div class="grid grid-3">
                <div class="card">
                    <h4>ITC Countries</h4>
                    <p style="font-size: 11px;">53% of members from Inclusiveness Target Countries</p>
                    <p style="font-size: 10px; color: #64748b;">22 ITC countries represented</p>
                </div>
                <div class="card">
                    <h4>Young Researchers</h4>
                    <p style="font-size: 11px;">41.3% of participants are early career researchers</p>
                    <p style="font-size: 10px; color: #64748b;">YRI priority in grant allocation</p>
                </div>
                <div class="card">
                    <h4>Gender Diversity</h4>
                    <p style="font-size: 11px;">Active diversity team promoting inclusion</p>
                    <p style="font-size: 10px; color: #64748b;">Gender balance monitoring</p>
                </div>
            </div>
        </section>

        {get_footer()}'''

    return page_content


def generate_cost_events_page(data: Dict[str, Any]) -> str:
    """Generate the COST events page (cost-events.html)."""

    summary_stats = data.get("summary_stats", {})
    meetings = summary_stats.get("total_meetings", 52)
    training_schools = summary_stats.get("total_training_schools", 7)
    trainees = summary_stats.get("total_trainees", 96)

    meetings_by_gp = summary_stats.get("meetings_by_gp", {})
    ts_by_gp = summary_stats.get("ts_by_gp", {})

    page_content = f'''{get_head_section(
        "Events & Conferences",
        f"COST Action CA19130 events: {meetings} meetings, {training_schools} training schools, and more",
        "cost-events.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-events.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="cost-action.html">COST Action</a> / Events</div>

        <div class="hero" style="background: var(--color-green); padding: 24px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 8px;">Research Events & Training</h1>
            <p style="font-size: 13px; opacity: 0.9;">{meetings} Meetings | {training_schools} Training Schools | {trainees} Trainees</p>
        </div>

        <section class="section">
            <div class="section-title">Event Statistics</div>
            <div class="grid grid-4">
                <div class="output-card"><div class="output-num">{meetings}</div><div class="output-lbl">Meetings</div></div>
                <div class="output-card"><div class="output-num">{training_schools}</div><div class="output-lbl">Training Schools</div></div>
                <div class="output-card"><div class="output-num">{trainees}</div><div class="output-lbl">Trainees</div></div>
                <div class="output-card"><div class="output-num">6,000+</div><div class="output-lbl">Participants</div></div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Annual Conference Series</div>
            <div class="grid grid-2">
                <div class="card">
                    <h4>8th European COST Conference on AI in Finance</h4>
                    <p style="font-size: 11px;"><strong>Date:</strong> September 2024</p>
                    <p style="font-size: 11px;"><strong>Location:</strong> Bern University of Applied Sciences, Switzerland</p>
                    <p style="font-size: 11px;"><strong>Organizer:</strong> Prof. Joerg Osterrieder (SNSF PI)</p>
                    <p style="font-size: 10px; color: #64748b;">Final major COST event before Action conclusion</p>
                </div>
                <div class="card">
                    <h4>7th European COST Conference on AI in Finance</h4>
                    <p style="font-size: 11px;"><strong>Date:</strong> September 2023</p>
                    <p style="font-size: 11px;"><strong>Location:</strong> Bern University of Applied Sciences, Switzerland</p>
                    <p style="font-size: 11px;"><strong>Organizer:</strong> Prof. Joerg Osterrieder (SNSF PI)</p>
                    <p style="font-size: 10px; color: #64748b;">First COST conference during SNSF project period</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Training Schools</div>
            <div class="grid grid-2">
                <div class="card">
                    <h4>COST FinAI PhD School 2024</h4>
                    <p style="font-size: 11px;"><strong>Date:</strong> June 10-14, 2024</p>
                    <p style="font-size: 11px;"><strong>Location:</strong> University of Twente, Enschede, Netherlands</p>
                    <p style="font-size: 11px;"><strong>Topic:</strong> Generative AI, Chatbots, LLMs in Finance</p>
                    <p style="font-size: 10px; color: #64748b;">Gabin Taibi (SNSF PhD) participated</p>
                </div>
                <div class="card">
                    <h4>Additional Training Schools</h4>
                    <p style="font-size: 11px;">Total of {training_schools} training schools organized across GP4-GP5</p>
                    <p style="font-size: 11px;">{trainees} trainees benefited from COST-funded training</p>
                    <p style="font-size: 10px; color: #64748b;">Topics: ML, XAI, Blockchain, FinTech</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Meetings by Grant Period</div>
            <div class="grid grid-5">
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP1</div>
                    <div style="font-size: 24px; font-weight: 700;">{meetings_by_gp.get("1", 21)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP2</div>
                    <div style="font-size: 24px; font-weight: 700;">{meetings_by_gp.get("2", 4)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP3</div>
                    <div style="font-size: 24px; font-weight: 700;">{meetings_by_gp.get("3", 9)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP4</div>
                    <div style="font-size: 24px; font-weight: 700;">{meetings_by_gp.get("4", 8)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP5</div>
                    <div style="font-size: 24px; font-weight: 700;">{meetings_by_gp.get("5", 10)}</div>
                </div>
            </div>
        </section>

        {get_footer()}'''

    return page_content


def generate_cost_publications_page(data: Dict[str, Any]) -> str:
    """Generate the COST publications page (cost-publications.html)."""

    final_report = data.get("final_report", {})
    summary = final_report.get("summary", {})
    stats = summary.get("stats", {})
    citations = stats.get("citations", 10000)

    page_content = f'''{get_head_section(
        "Publications & Impact",
        f"COST Action CA19130 publications: {citations:,}+ citations from network research",
        "cost-publications.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-publications.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="cost-action.html">COST Action</a> / Publications</div>

        <div class="hero" style="background: var(--color-accent); padding: 24px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 8px;">Publication Impact</h1>
            <p style="font-size: 13px; opacity: 0.9;">7,483 Publications | 6,270 DOIs | 244 Authors | {citations:,}+ Citations</p>
        </div>

        <section class="section">
            <div class="section-title">Publication Statistics</div>
            <div class="grid grid-4">
                <div class="output-card"><div class="output-num">7,483</div><div class="output-lbl">Publications</div></div>
                <div class="output-card"><div class="output-num">6,270</div><div class="output-lbl">Unique DOIs</div></div>
                <div class="output-card"><div class="output-num">244</div><div class="output-lbl">Authors</div></div>
                <div class="output-card"><div class="output-num">{citations:,}+</div><div class="output-lbl">Citations</div></div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Joint SNSF-COST Publications</div>
            <div class="highlight" style="border-left: 4px solid var(--color-primary); padding: 16px; background: #f8fafc;">
                <h4 style="margin: 0 0 8px 0;">Mitigating Digital Asset Risks (2023)</h4>
                <p style="font-size: 11px; margin: 0 0 4px 0;"><strong>SSRN:</strong> 4594467</p>
                <p style="font-size: 11px; margin: 0 0 4px 0;"><strong>Authors:</strong> Teng, Hardle, Osterrieder, Baals + 30 co-authors</p>
                <p style="font-size: 11px; margin: 0;"><strong>Topics:</strong> Blockchain, DLT, Digital Asset Regulation</p>
            </div>
            <div class="grid grid-2" style="margin-top: 16px;">
                <div class="card">
                    <h4>Hypothesizing Multimodal Influence (2024)</h4>
                    <p style="font-size: 11px;"><strong>SSRN:</strong> 4698153</p>
                    <p style="font-size: 11px;">Authors: Bolesta, Taibi, Mare, Osterrieder, Hopp</p>
                    <p style="font-size: 10px; color: #64748b;">Cross-COST collaboration on multimodal NLP</p>
                </div>
                <div class="card">
                    <h4>AI 4 Crowdfunding (2024)</h4>
                    <p style="font-size: 11px;"><strong>SSRN:</strong> 4941279</p>
                    <p style="font-size: 11px;">Multiple COST network authors</p>
                    <p style="font-size: 10px; color: #64748b;">AI for crowdfunding analysis</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Top Authors from Network</div>
            <p style="font-size: 11px; margin-bottom: 12px;">Leading contributors to COST Action publications (via OpenAlex).</p>
            <table class="pub-table" style="font-size: 11px;">
                <thead>
                    <tr><th>#</th><th>Author</th><th>Publications</th></tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Nuray Bayar Muluk</td><td>346</td></tr>
                    <tr><td>2</td><td>Dervis Kirikkaleli</td><td>264</td></tr>
                    <tr><td>3</td><td>Gazi Salah Uddin</td><td>205</td></tr>
                    <tr style="background: #eff6ff;"><td>4</td><td><strong>Jorg Osterrieder</strong> (SNSF PI)</td><td>106</td></tr>
                    <tr><td>5</td><td>Samuel Asante Gyamerah</td><td>105</td></tr>
                </tbody>
            </table>
            <p style="font-size: 10px; color: #64748b; margin-top: 8px;">Full publication list available at <a href="https://wiki.fin-ai.eu/" target="_blank" rel="noopener noreferrer">COST FinAI Wiki</a></p>
        </section>

        {get_footer()}'''

    return page_content


def generate_cost_mobility_page(data: Dict[str, Any]) -> str:
    """Generate the COST mobility page (cost-mobility.html)."""

    summary_stats = data.get("summary_stats", {})
    stsms = summary_stats.get("total_stsms", 27)
    vm = summary_stats.get("total_virtual_mobility", 39)

    stsms_by_gp = summary_stats.get("stsms_by_gp", {})
    vm_by_gp = summary_stats.get("vm_by_gp", {})

    financial = summary_stats.get("financial_totals", {})
    stsm_budget = financial.get("stsms", 60082)
    vm_budget = financial.get("virtual_mobility", 56500)

    page_content = f'''{get_head_section(
        "Mobility Grants",
        f"COST Action CA19130 mobility: {stsms} STSMs, {vm} Virtual Mobility grants",
        "cost-mobility.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-mobility.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="cost-action.html">COST Action</a> / Mobility</div>

        <div class="hero" style="background: linear-gradient(135deg, #06b6d4, #0891b2); padding: 24px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 8px;">Researcher Mobility</h1>
            <p style="font-size: 13px; opacity: 0.9;">{stsms} STSMs | {vm} Virtual Mobility | EUR {(stsm_budget + vm_budget)/1000:.0f}K+ in Grants</p>
        </div>

        <section class="section">
            <div class="section-title">Mobility Overview</div>
            <div class="grid grid-4">
                <div class="output-card"><div class="output-num">{stsms}</div><div class="output-lbl">STSMs</div></div>
                <div class="output-card"><div class="output-num">{vm}</div><div class="output-lbl">Virtual Mobility</div></div>
                <div class="output-card"><div class="output-num">EUR {stsm_budget:,.0f}</div><div class="output-lbl">STSM Budget</div></div>
                <div class="output-card"><div class="output-num">EUR {vm_budget:,.0f}</div><div class="output-lbl">VM Budget</div></div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Short-Term Scientific Missions (STSMs)</div>
            <p style="font-size: 11px; margin-bottom: 12px;">STSMs enable researchers to visit another institution for collaborative research (typically 1-4 weeks).</p>
            <div class="grid grid-5">
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP1</div>
                    <div style="font-size: 24px; font-weight: 700;">{stsms_by_gp.get("1", 9)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP2</div>
                    <div style="font-size: 24px; font-weight: 700;">{stsms_by_gp.get("2", 0)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP3</div>
                    <div style="font-size: 24px; font-weight: 700;">{stsms_by_gp.get("3", 10)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP4</div>
                    <div style="font-size: 24px; font-weight: 700;">{stsms_by_gp.get("4", 6)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP5</div>
                    <div style="font-size: 24px; font-weight: 700;">{stsms_by_gp.get("5", 2)}</div>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Virtual Mobility Grants</div>
            <p style="font-size: 11px; margin-bottom: 12px;">Virtual Mobility grants support remote collaboration, particularly useful during/post-pandemic.</p>
            <div class="grid grid-5">
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP1</div>
                    <div style="font-size: 24px; font-weight: 700;">{vm_by_gp.get("1", 0)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP2</div>
                    <div style="font-size: 24px; font-weight: 700;">{vm_by_gp.get("2", 1)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP3</div>
                    <div style="font-size: 24px; font-weight: 700;">{vm_by_gp.get("3", 12)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP4</div>
                    <div style="font-size: 24px; font-weight: 700;">{vm_by_gp.get("4", 12)}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 11px; color: #64748b;">GP5</div>
                    <div style="font-size: 24px; font-weight: 700;">{vm_by_gp.get("5", 14)}</div>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">ITC & Young Researcher Support</div>
            <div class="grid grid-2">
                <div class="card">
                    <h4>ITC Priority</h4>
                    <p style="font-size: 11px;">53% of mobility grants awarded to researchers from Inclusiveness Target Countries</p>
                    <p style="font-size: 10px; color: #64748b;">Supporting researchers from less research-intensive countries</p>
                </div>
                <div class="card">
                    <h4>Young Researchers (YRI)</h4>
                    <p style="font-size: 11px;">Priority given to early career researchers</p>
                    <p style="font-size: 10px; color: #64748b;">Career development and network building focus</p>
                </div>
            </div>
        </section>

        {get_footer()}'''

    return page_content


def generate_cost_resources_page(data: Dict[str, Any]) -> str:
    """Generate the COST resources page (cost-resources.html)."""

    page_content = f'''{get_head_section(
        "Resources & Deliverables",
        "COST Action CA19130 resources: QuantLet, Quantinar, deliverables, and final report",
        "cost-resources.html"
    )}
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    {get_navbar("cost-action.html")}
    {get_sidebar_cost("cost-resources.html")}

    <main class="main" id="main-content">
        <div class="breadcrumb"><a href="index.html">Home</a> / <a href="cost-action.html">COST Action</a> / Resources</div>

        <div class="hero" style="background: linear-gradient(135deg, #0f172a, #6366f1); padding: 24px; text-align: center; color: white; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 8px;">Knowledge Resources</h1>
            <p style="font-size: 13px; opacity: 0.9;">Platforms | Datasets | Deliverables | Reports</p>
        </div>

        <section class="section">
            <div class="section-title">Knowledge Platforms</div>
            <div class="grid grid-3">
                <a href="https://quantlet.com/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>QuantLet</h4>
                    <p style="font-size: 11px;">Reproducible research code repository</p>
                    <p style="font-size: 10px; color: #64748b;">quantlet.com</p>
                </a>
                <a href="https://quantinar.com/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Quantinar</h4>
                    <p style="font-size: 11px;">P2P knowledge exchange platform</p>
                    <p style="font-size: 10px; color: #64748b;">quantinar.com</p>
                </a>
                <a href="https://explainableaiforfinance.com/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>Explainable AI</h4>
                    <p style="font-size: 11px;">XAI tools for finance</p>
                    <p style="font-size: 10px; color: #64748b;">explainableaiforfinance.com</p>
                </a>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Key Deliverables</div>
            <div class="grid grid-2">
                <div class="card">
                    <h4>ICO Database</h4>
                    <p style="font-size: 11px; color: #22c55e;">Delivered</p>
                    <p style="font-size: 10px; color: #64748b;">Comprehensive database of Initial Coin Offerings</p>
                </div>
                <div class="card">
                    <h4>Crowdfunding/P2P Database</h4>
                    <p style="font-size: 11px; color: #22c55e;">Delivered</p>
                    <p style="font-size: 10px; color: #64748b;">Crowdfunding and peer-to-peer lending data</p>
                </div>
                <div class="card">
                    <h4>ICO Evaluation Papers</h4>
                    <p style="font-size: 11px; color: #22c55e;">Delivered</p>
                    <p style="font-size: 10px; color: #64748b;">Research papers on ICO evaluation methods</p>
                </div>
                <div class="card">
                    <h4>Digital Assets Position Paper</h4>
                    <p style="font-size: 11px; color: #22c55e;">Delivered</p>
                    <p style="font-size: 10px; color: #64748b;">Policy recommendations for digital asset regulation</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="section-title">MoU Objectives Achievement</div>
            <p style="font-size: 11px; margin-bottom: 12px;">All 8 Memorandum of Understanding objectives achieved at 76-100% completion.</p>
            <div class="highlight" style="border-left: 4px solid #22c55e; padding: 16px; background: #f0fdf4;">
                <p style="font-size: 12px; margin: 0; font-weight: 600;">Action Successfully Concluded</p>
                <p style="font-size: 11px; margin: 8px 0 0 0;">COST Action CA19130 completed its 4-year term in October 2024 with all objectives met.</p>
            </div>
        </section>

        <section class="section">
            <div class="section-title">Documentation & Wiki</div>
            <div class="grid grid-2">
                <a href="https://wiki.fin-ai.eu/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>COST FinAI Wiki</h4>
                    <p style="font-size: 11px;">Complete documentation of Action activities</p>
                    <p style="font-size: 10px; color: #64748b;">wiki.fin-ai.eu</p>
                </a>
                <a href="https://www.cost.eu/actions/CA19130/" target="_blank" rel="noopener noreferrer" class="card" style="text-decoration: none; color: inherit;">
                    <h4>COST Official Portal</h4>
                    <p style="font-size: 11px;">Official COST Association page</p>
                    <p style="font-size: 10px; color: #64748b;">cost.eu/actions/CA19130</p>
                </a>
            </div>
        </section>

        {get_footer()}'''

    return page_content


# =============================================================================
# JSON OUTPUT GENERATION
# =============================================================================

def generate_cost_summary_json(data: Dict[str, Any]) -> dict:
    """Generate summary JSON for client-side use."""

    final_report = data.get("final_report", {})
    summary = final_report.get("summary", {})
    stats = summary.get("stats", {})
    summary_stats = data.get("summary_stats", {})
    leadership = data.get("leadership", {})

    return {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "source": "COST Action CA19130",
            "action_code": "CA19130",
            "action_name": "Fintech and Artificial Intelligence in Finance"
        },
        "stats": {
            "researchers": stats.get("researchers", 420),
            "countries": stats.get("countries", 55),
            "cost_countries": stats.get("cost_countries", 39),
            "citations": stats.get("citations", 10000),
            "meetings": summary_stats.get("total_meetings", 52),
            "stsms": summary_stats.get("total_stsms", 27),
            "training_schools": summary_stats.get("total_training_schools", 7),
            "virtual_mobility": summary_stats.get("total_virtual_mobility", 39),
            "total_budget": summary_stats.get("total_budget", 963654)
        },
        "working_groups": leadership.get("working_groups", []),
        "grant_periods": leadership.get("grant_periods", []),
        "snsf_alignment": WP_WG_ALIGNMENT,
        "collaborators": SNSF_COST_COLLABORATORS
    }


# =============================================================================
# MAIN BUILD FUNCTION
# =============================================================================

def build_cost_pages(dry_run: bool = False, verbose: bool = False) -> bool:
    """Build all COST Action pages."""

    # Setup logging
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    logger.info("=" * 60)
    logger.info("COST ACTION PAGES GENERATOR")
    logger.info("=" * 60)
    logger.info(f"Source: {COST_DATA_SOURCE}")
    logger.info(f"Target: {TARGET_REPO}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    # Validate paths
    if not COST_DATA_SOURCE.exists():
        logger.error(f"COST data source not found: {COST_DATA_SOURCE}")
        return False

    if not TARGET_REPO.exists():
        logger.error(f"Target repository not found: {TARGET_REPO}")
        return False

    # Load COST data
    logger.info("Loading COST data files...")
    data = load_all_cost_data()

    # Generate pages
    pages_to_generate = [
        ("cost-action.html", generate_cost_action_page, "Hub page"),
        ("cost-network.html", generate_cost_network_page, "Network page"),
        ("cost-events.html", generate_cost_events_page, "Events page"),
        ("cost-publications.html", generate_cost_publications_page, "Publications page"),
        ("cost-mobility.html", generate_cost_mobility_page, "Mobility page"),
        ("cost-resources.html", generate_cost_resources_page, "Resources page"),
    ]

    logger.info("Generating HTML pages...")
    for filename, generator, description in pages_to_generate:
        try:
            content = generator(data)
            output_path = TARGET_REPO / filename

            if dry_run:
                logger.info(f"  [DRY RUN] Would write: {filename} ({len(content):,} bytes)")
            else:
                output_path.write_text(content, encoding='utf-8')
                logger.info(f"  [OK] {filename} ({len(content):,} bytes)")
        except Exception as e:
            logger.error(f"  [ERROR] {filename}: {e}")
            return False

    # Generate JSON data
    logger.info("Generating JSON data...")
    try:
        summary_data = generate_cost_summary_json(data)
        json_path = DATA_DEST / "cost_summary.json"

        if dry_run:
            logger.info(f"  [DRY RUN] Would write: cost_summary.json")
        else:
            DATA_DEST.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            logger.info(f"  [OK] cost_summary.json")
    except Exception as e:
        logger.error(f"  [ERROR] cost_summary.json: {e}")
        return False

    logger.info("=" * 60)
    logger.info("BUILD COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Pages generated: {len(pages_to_generate)}")
    logger.info(f"JSON files generated: 1")

    return True


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate COST Action CA19130 pages for Narrative Digital Finance website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cost_integration.py              # Full generation
    python cost_integration.py --dry-run    # Preview without writing
    python cost_integration.py -v           # Verbose output
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without writing files'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose/debug logging'
    )

    args = parser.parse_args()

    success = build_cost_pages(
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
