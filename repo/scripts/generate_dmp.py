#!/usr/bin/env python3
"""
Generate DMP pages from single source JSON.

This script generates both dmp.html and dmp-comparison.html from
data/dmp-content.json to ensure they stay in sync.

Usage:
    python scripts/generate_dmp.py
    python scripts/generate_dmp.py --dry-run
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def load_dmp_content(json_path: Path) -> dict:
    """Load DMP content from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_dmp_html(data: dict) -> str:
    """Generate the full DMP page HTML."""
    meta = data['metadata']
    sections = data['sections']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Management Plan | Narrative Digital Finance</title>
    <meta name="description" content="SNSF-compliant Data Management Plan for Narrative Digital Finance project (Grant {meta['grant_number']}).">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #334155; padding-top: 60px; background: #f8fafc; }}
        h1 {{ font-size: 20px; text-align: center; margin-bottom: 16px; color: #0f172a; }}
        h2 {{ font-size: 14px; font-weight: 700; margin: 28px 0 12px 0; color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 6px; }}
        h3 {{ font-size: 12px; font-weight: 600; margin: 16px 0 8px 0; color: #1e40af; }}
        p {{ margin: 0 0 10px 0; }}
        ul {{ margin: 8px 0 12px 0; padding-left: 20px; }}
        li {{ margin: 4px 0; }}
        a {{ color: #3b82f6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .header-info {{ text-align: center; margin-bottom: 24px; padding: 16px; background: linear-gradient(135deg, #0f172a, #1e3a5f); color: #fff; border-radius: 8px; }}
        .header-info p {{ margin: 4px 0; color: #fff; }}
        .header-info .title {{ font-size: 11px; opacity: 0.9; }}
        .section {{ background: #fff; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .navbar {{ position: fixed; top: 0; left: 0; right: 0; height: 36px; background: #0f172a; display: flex; align-items: center; padding: 0 16px; z-index: 100; }}
        .navbar-brand {{ font-family: 'Inter', sans-serif; color: #fff; text-decoration: none; font-size: 12px; font-weight: 600; }}
        .navbar-brand span {{ color: #3b82f6; margin-right: 4px; }}
        .navbar-nav {{ display: flex; gap: 16px; margin-left: auto; }}
        .navbar-nav a {{ font-family: 'Inter', sans-serif; color: #94a3b8; text-decoration: none; font-size: 11px; transition: color 0.2s; }}
        .navbar-nav a:hover {{ color: #fff; }}
        .navbar-nav a.active {{ color: #3b82f6; }}
        .toc {{ background: #eff6ff; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3b82f6; }}
        .toc h3 {{ margin-top: 0; color: #0f172a; font-size: 13px; }}
        .toc ul {{ margin: 8px 0 0 0; padding-left: 18px; }}
        .toc li {{ margin: 3px 0; }}
        .toc a {{ color: #1e40af; font-size: 11px; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }}
        .badge-yes {{ background: #10b981; color: #fff; }}
        .badge-no {{ background: #dc2626; color: #fff; }}
        .report-footer {{ margin-top: 32px; padding: 16px 0; border-top: 1px solid #e2e8f0; text-align: center; font-size: 10px; color: #64748b; }}
        .report-footer a {{ color: #3b82f6; }}
        .back-to-top {{ position: fixed; bottom: 20px; right: 20px; background: #3b82f6; color: #fff; padding: 8px 12px; border-radius: 4px; font-size: 11px; text-decoration: none; opacity: 0.8; }}
        .back-to-top:hover {{ opacity: 1; color: #fff; }}
        @media print {{
            .navbar, .back-to-top {{ display: none; }}
            body {{ padding-top: 0; background: #fff; }}
            .section {{ box-shadow: none; border: 1px solid #ccc; }}
        }}
        @media (max-width: 600px) {{
            body {{ padding: 10px; padding-top: 50px; }}
            .section {{ padding: 12px; }}
        }}
    </style>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>

<nav class="navbar">
    <a href="index.html" class="navbar-brand"><span>NDF</span> Narrative Digital Finance</a>
    <div class="navbar-nav">
        <a href="index.html">Home</a>
        <a href="objectives.html">Objectives</a>
        <a href="report.html">Report</a>
        <a href="dmp.html" class="active">DMP</a>
        <a href="dmp-comparison.html">Compare</a>
    </div>
</nav>

<h1>Data management plan (DMP)</h1>

<div class="header-info">
    <p style="font-size: 14px; font-weight: 700;">SNSF Grant {meta['grant_number']}</p>
    <p class="title">{meta['title']}</p>
    <p>Principal Investigator: {meta['pi']}</p>
    <p>{' | '.join(meta['institutions'])}</p>
    <p style="margin-top: 8px; opacity: 0.8;">{meta['duration']}</p>
</div>

<div class="toc">
    <h3>Contents</h3>
    <ul>
'''
    # Add TOC entries
    for section in sections:
        html += f'        <li><a href="#section-{section["id"]}">{section["id"]} {section["title"]}</a></li>\n'

    html += '''    </ul>
</div>

'''

    # Generate each section
    for section in sections:
        html += f'''<!-- Section {section['id']} -->
<div class="section" id="section-{section['id']}">
    <h2>{section['id']} {section['title']}</h2>

'''
        for q in section['questions']:
            html += generate_question_html(q)

        html += '</div>\n\n'

    # Footer
    html += f'''<a href="#main-content" class="back-to-top">Back to top</a>

<div class="report-footer">
    <p>
        <a href="index.html">Narrative Digital Finance</a> |
        SNSF Grant {meta['grant_number']} |
        <a href="https://data.snf.ch/grants/grant/213370">SNSF Data Portal</a> |
        <a href="dmp-comparison.html">View Comparison</a>
    </p>
    <p style="margin-top: 8px;">Last updated: {meta['last_updated']}</p>
</div>

</body>
</html>
'''
    return html


def generate_question_html(q: dict) -> str:
    """Generate HTML for a single question in the DMP."""
    html = f'    <h3 id="section-{q["id"].replace(".", "-")}">{q["id"]} {q["title"]}</h3>\n\n'

    enhanced = q.get('enhanced', {})

    # Handle different question structures
    if isinstance(enhanced, dict):
        # Questions with structured enhanced content
        if 'intro' in enhanced:
            html += f'    <p>{enhanced["intro"]}</p>\n\n'

        if 'original_paragraph' in enhanced:
            html += f'    <p>{enhanced["original_paragraph"]}</p>\n\n'

        if 'quality_assurance' in enhanced:
            html += f'    <p><strong>Quality assurance:</strong> {enhanced["quality_assurance"]}</p>\n\n'

        if 'versioning' in enhanced:
            html += f'    <p><strong>Versioning:</strong> {enhanced["versioning"]}</p>\n\n'

        if 'collection_methods' in enhanced:
            html += f'    <p><strong>Data Collection Methods:</strong> {enhanced["collection_methods"]}</p>\n\n'

        if 'metadata_standards' in enhanced:
            html += f'    <p><strong>Metadata Standards:</strong> {enhanced["metadata_standards"]}</p>\n\n'

        if 'documentation' in enhanced:
            html += f'    <p><strong>Documentation Provided:</strong> {enhanced["documentation"]}</p>\n\n'

        if 'ethical_considerations' in enhanced:
            html += f'    <p><strong>Ethical Considerations:</strong> {enhanced["ethical_considerations"]}</p>\n\n'

        if 'data_provider_agreements' in enhanced:
            agreements = enhanced['data_provider_agreements']
            html += '    <p><strong>Data Provider Agreements:</strong> '
            parts = [f'{a["provider"]} operates under {a["terms"].lower()} with {a["restrictions"].lower()}' for a in agreements]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'ethics_approval' in enhanced:
            html += f'    <p><strong>Ethics Approval:</strong> {enhanced["ethics_approval"]}</p>\n\n'

        if 'access_control' in enhanced:
            controls = enhanced['access_control']
            html += '    <p><strong>Access Control:</strong> '
            parts = [f'{c["category"]} has {c["access"].lower()} access and is stored on {c["storage"]}' for c in controls]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'security_measures' in enhanced:
            html += f'    <p><strong>Security Measures:</strong> {enhanced["security_measures"]}</p>\n\n'

        if 'team_members' in enhanced:
            members = enhanced['team_members']
            html += '    <p><strong>Authorized Team Members:</strong> '
            parts = [f'{m["name"]} ({m["role"]})' for m in members]
            html += ', '.join(parts) + '.</p>\n\n'

        if 'copyright_framework' in enhanced:
            framework = enhanced['copyright_framework']
            html += '    <p><strong>Copyright Framework:</strong> '
            parts = [f'{f["data"]} is copyrighted by {f["holder"]} with {f["rights"].lower()} rights under {f["license"]}' for f in framework]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'publication_rights' in enhanced:
            rights = enhanced['publication_rights']
            html += '    <p><strong>Publication Rights:</strong> '
            html += ' '.join([f'<span class="badge badge-yes">Yes</span> {r}.' for r in rights.get('allowed', [])])
            html += ' '.join([f' <span class="badge badge-no">No</span> {r}.' for r in rights.get('not_allowed', [])])
            html += '</p>\n\n'

        if 'primary_storage' in enhanced:
            ps = enhanced['primary_storage']
            html += f'    <p><strong>Primary Storage:</strong> Location is {ps["location"]}. Capacity is {ps["capacity"]}. Backup schedule is {ps["backup"].lower()}. Retention is {ps["retention"].lower()}.</p>\n\n'

        if 'cloud_storage' in enhanced:
            storage = enhanced['cloud_storage']
            html += '    <p><strong>Cloud Storage:</strong> '
            parts = []
            for s in storage:
                if s['url'].startswith('http'):
                    parts.append(f'{s["platform"]} (<a href="{s["url"]}">{s["url"].replace("https://", "")}</a>) is used for {s["purpose"].lower()}')
                else:
                    parts.append(f'{s["platform"]} is used for {s["purpose"].lower()}, {s["url"]}')
            html += '. '.join(parts) + '.</p>\n\n'

        if 'backup_strategy' in enhanced:
            strategy = enhanced['backup_strategy']
            html += '    <p><strong>Backup Strategy:</strong> '
            parts = [f'{s["type"]} is backed up {s["frequency"].lower()} with {s["retention"].lower()} retention on {s["location"]}' for s in strategy]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'repository_selection' in enhanced:
            repos = enhanced['repository_selection']
            html += '    <p><strong>Repository Selection:</strong> '
            parts = [f'{r["name"]} is operated by {r["organization"]}, offers {r["features"]}' for r in repos]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'preservation_timeline' in enhanced:
            timeline = enhanced['preservation_timeline']
            html += '    <p><strong>Preservation Timeline:</strong> '
            parts = [f'At {t["milestone"].lower()}, we {t["action"].lower()} with {t["doi"]}' for t in timeline]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'archival_formats' in enhanced:
            formats = enhanced['archival_formats']
            html += f'    <p><strong>Archival File Formats (Open Standards):</strong> Data in {formats["data"]}. Documentation in {formats["documentation"]}. Code in {formats["code"]}. Images in {formats["images"]}.</p>\n\n'

        if 'retention_period' in enhanced:
            html += f'    <p><strong>Retention Period:</strong> {enhanced["retention_period"]}</p>\n\n'

        if 'current_outputs' in enhanced:
            outputs = enhanced['current_outputs']
            html += '    <p><strong>Current Outputs (Available Now):</strong> '
            parts = [f'{o["name"]} is {o["status"].lower()} on {o["repository"]} at <a href="{o["url"]}">{o["url"].replace("https://", "")}</a>' for o in outputs]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'upcoming_deposits' in enhanced:
            deposits = enhanced['upcoming_deposits']
            html += '    <p><strong>Upcoming Deposits:</strong> '
            parts = [f'{d["name"]} will be deposited on {d["repository"]} {d["timeline"].lower() if not d["timeline"][0].isupper() else d["timeline"]}' for d in deposits]
            html += '. '.join(parts) + '.</p>\n\n'

        if 'sharing_by_type' in enhanced:
            sharing = enhanced['sharing_by_type']
            html += '    <p><strong>Sharing by Data Type:</strong> '
            parts = []
            for s in sharing:
                badge = 'badge-yes' if s['shareable'] else 'badge-no'
                yn = 'Yes' if s['shareable'] else 'No'
                parts.append(f'{s["data"]}: <span class="badge {badge}">{yn}</span> ({s["reason"]})')
            html += '. '.join(parts) + '.</p>\n\n'

        if 'unrestricted' in enhanced:
            html += '    <p><strong>Unrestricted (Open Access):</strong> ' + '. '.join(enhanced['unrestricted']) + '.</p>\n\n'

        if 'restricted' in enhanced:
            html += '    <p><strong>Restricted (Cannot Share):</strong> ' + '. '.join(enhanced['restricted']) + '.</p>\n\n'

        if 'reuse_conditions' in enhanced:
            html += '    <p><strong>Reuse Conditions:</strong> ' + '. '.join(enhanced['reuse_conditions']) + '.</p>\n\n'

        if 'access_requests' in enhanced:
            email = enhanced['access_requests']
            html += f'    <p><strong>Access Requests:</strong> For restricted data, contact <a href="mailto:{email}">{email}</a> - we can facilitate contact with original data providers.</p>\n\n'

        if 'answer' in enhanced:
            badge = 'badge-yes' if enhanced['answer'] else 'badge-no'
            yn = 'Yes' if enhanced['answer'] else 'No'
            html += f'    <p><span class="badge {badge}">{yn}</span></p>\n\n'

        if 'fair_implementation' in enhanced:
            fair = enhanced['fair_implementation']
            html += f'    <p><strong>FAIR Data Principles Implementation:</strong> <strong>Findable:</strong> {fair["findable"]}. <strong>Accessible:</strong> {fair["accessible"]}. <strong>Interoperable:</strong> {fair["interoperable"]}. <strong>Reusable:</strong> {fair["reusable"]}.</p>\n\n'

        if 'repository_certification' in enhanced:
            certs = enhanced['repository_certification']
            html += '    <p><strong>Repository Certification:</strong> '
            parts = [f'{c["name"]} is operated by {c["organization"]}, {c["certification"]}' for c in certs]
            html += '. '.join(parts) + '.</p>\n\n'

        # Handle commercial/public/generated sources for Q1.1
        if 'commercial_sources' in enhanced:
            html += '    <p><strong>Commercial Data Sources (Licensed):</strong></p>\n'
            for src in enhanced['commercial_sources']:
                html += f'    <p><strong>{src["name"]}:</strong> {src["description"]}. Format: {src["format"]}. Volume: {src["volume"]}. Time range: {src["time_range"]}.</p>\n'
            html += '\n'

        if 'public_sources' in enhanced:
            html += '    <p><strong>Public Data Sources:</strong></p>\n'
            for src in enhanced['public_sources']:
                url_display = src["url"].replace("https://", "")
                html += f'    <p><strong>{src["name"]}:</strong> {src["description"]}. Format: {src["format"]}. URL: <a href="{src["url"]}">{url_display}</a></p>\n'
            html += '\n'

        if 'generated_data' in enhanced:
            html += '    <p><strong>Generated Data:</strong></p>\n'
            for src in enhanced['generated_data']:
                repo_link = f'<a href="{src["repository"]}">{src["repository"].replace("https://", "")}</a>' if src["repository"].startswith("http") else src["repository"]
                html += f'    <p><strong>{src["name"]}:</strong> {src["description"]}. Format: {src["format"]}. Volume: {src["volume"]}. Repository: {repo_link}.</p>\n'
            html += '\n'

        if 'total_volume' in enhanced:
            html += f'    <p><strong>Total estimated data volume: {enhanced["total_volume"]}</strong></p>\n\n'

    return html


def generate_comparison_html(data: dict) -> str:
    """Generate the comparison page HTML."""
    meta = data['metadata']
    sections = data['sections']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DMP Comparison | Narrative Digital Finance</title>
    <meta name="description" content="Side-by-side comparison of original vs enhanced Data Management Plan for SNSF Grant {meta['grant_number']}.">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <nav class="navbar">
        <a href="index.html" class="navbar-brand"><span>NDF</span> Narrative Digital Finance</a>
        <div class="navbar-nav">
            <a href="index.html">Home</a>
            <a href="objectives.html">Objectives</a>
            <a href="report.html">Report</a>
            <a href="dmp.html">DMP</a>
            <a href="dmp-comparison.html" style="color:#3b82f6">Compare</a>
        </div>
    </nav>

    <aside class="sidebar" aria-label="Navigation">
        <div class="sidebar-section">
            <div class="sidebar-title">Sections</div>
            <ul class="sidebar-nav">
'''

    # Sidebar navigation
    for section in sections:
        html += f'                <li><a href="#section-{section["id"]}">{section["id"]}. {section["title"].split()[0]}</a></li>\n'
        for q in section['questions']:
            q_id = q['id'].replace('.', '-')
            short_title = q['title'][:20] + '...' if len(q['title']) > 20 else q['title']
            html += f'                <li><a href="#section-{q_id}">{q["id"]} {short_title}</a></li>\n'

    html += '''            </ul>
        </div>
        <div class="sidebar-divider"></div>
        <div class="sidebar-section">
            <div class="sidebar-title">Pages</div>
            <a href="dmp.html" class="sidebar-link">Full DMP</a>
            <a href="index.html#datasets" class="sidebar-link">Datasets</a>
        </div>
    </aside>

    <main class="main" id="main-content">
        <div class="comparison-hero">
            <h1>DMP Comparison: Original vs Enhanced</h1>
            <p class="sub">SNSF Grant ''' + meta['grant_number'] + ''' | Data Management Plan Review</p>
        </div>

        <div class="container">
            <!-- Legend -->
            <div class="comparison-legend">
                <div class="legend-item">
                    <div class="legend-color legend-original"></div>
                    <span>Original (from PDF)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-enhanced"></div>
                    <span>Enhanced (SNSF-compliant)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-addition"></div>
                    <span>New content added</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color legend-improvement"></div>
                    <span>Improved detail</span>
                </div>
            </div>

'''

    # Generate each section
    for section in sections:
        html += f'''            <!-- Section {section['id']} -->
            <div class="comparison-section" id="section-{section['id']}">
                <div class="comparison-section-header">{section['id']}. {section['title']}</div>

'''
        for q in section['questions']:
            html += generate_comparison_question_html(q)

        html += '            </div>\n\n'

    # Summary and footer
    html += f'''            <!-- Summary -->
            <div class="section">
                <div class="section-title">Summary of Enhancements</div>
                <div class="grid grid-3">
                    <div class="stat-card">
                        <div class="stat-num">7</div>
                        <div class="stat-lbl">Data Sources Specified</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-num">3</div>
                        <div class="stat-lbl">Repositories with DOIs</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-num">65 GB</div>
                        <div class="stat-lbl">Total Data Volume</div>
                    </div>
                </div>
                <p style="margin-top: 16px; text-align: center;">
                    <a href="dmp.html" class="btn btn-primary">View Full Enhanced DMP</a>
                </p>
            </div>

        </div>

        <footer class="footer">
            <div class="container">
                <div class="footer-bottom">
                    Narrative Digital Finance | SNSF Grant {meta['grant_number']} |
                    <a href="https://data.snf.ch/grants/grant/213370">SNSF Data Portal</a>
                </div>
            </div>
        </footer>
    </main>
</body>
</html>
'''
    return html


def generate_comparison_question_html(q: dict) -> str:
    """Generate HTML for a single question in the comparison page."""
    q_id = q['id'].replace('.', '-')
    html = f'''                <!-- {q['id']} -->
                <div id="section-{q_id}">
                    <div class="comparison-question">{q['id']} {q['title']}</div>
                    <div class="comparison-grid">
                        <div class="comparison-column column-original">
                            <div class="column-label">Original</div>
                            <p>{q['original'].replace(chr(10), '</p><p>')}</p>
                        </div>
                        <div class="comparison-column column-enhanced">
                            <div class="column-label">Enhanced</div>
'''

    enhanced = q.get('enhanced', {})

    if isinstance(enhanced, dict):
        # Add enhanced content based on what's available
        html += generate_enhanced_comparison_content(q['id'], enhanced)
    else:
        html += f'                            <p>{enhanced}</p>\n'

    html += '''                        </div>
                    </div>
                </div>

'''
    return html


def generate_enhanced_comparison_content(q_id: str, enhanced: dict) -> str:
    """Generate enhanced column content for comparison page."""
    html = ''

    # Q1.1 - Data sources
    if 'commercial_sources' in enhanced:
        html += '                            <div class="diff-addition"><strong>Commercial Data Sources (Licensed):</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Source</th><th>Format</th><th>Volume</th></tr>\n'
        for src in enhanced['commercial_sources']:
            html += f'                                <tr><td>{src["name"]}</td><td>{src["format"]}</td><td>{src["volume"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'public_sources' in enhanced:
        html += '                            <div class="diff-addition"><strong>Public Data Sources:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Source</th><th>Format</th><th>URL</th></tr>\n'
        for src in enhanced['public_sources']:
            url_short = src["url"].replace("https://", "").replace("www.", "")
            html += f'                                <tr><td>{src["name"]}</td><td>{src["format"]}</td><td>{url_short}</td></tr>\n'
        html += '                            </table>\n'

    if 'generated_data' in enhanced:
        html += '                            <div class="diff-addition"><strong>Generated Data:</strong></div>\n'
        html += '                            <ul>\n'
        for src in enhanced['generated_data']:
            repo = src["repository"].replace("https://", "") if src["repository"].startswith("http") else src["repository"]
            html += f'                                <li>{src["name"]} ({src["volume"]}, {src["format"]}) - {repo}</li>\n'
        html += '                            </ul>\n'

    if 'total_volume' in enhanced:
        html += f'                            <div class="diff-improvement"><strong>Total: {enhanced["total_volume"]}</strong></div>\n'

    # Q1.2 - Collection methods
    if 'collection_methods' in enhanced:
        html += '                            <div class="diff-addition"><strong>Data Collection Methods:</strong></div>\n'
        html += f'                            <p>{enhanced["collection_methods"]}</p>\n'

    if 'quality_assurance' in enhanced:
        html += '                            <div class="diff-improvement"><strong>Quality Assurance:</strong></div>\n'
        html += f'                            <p>{enhanced["quality_assurance"]}</p>\n'

    if 'versioning' in enhanced:
        html += '                            <div class="diff-improvement"><strong>Versioning:</strong></div>\n'
        html += f'                            <p>{enhanced["versioning"]}</p>\n'

    # Q1.3 - Documentation
    if 'metadata_standards' in enhanced:
        html += '                            <div class="diff-addition"><strong>Metadata Standards:</strong></div>\n'
        html += f'                            <p>{enhanced["metadata_standards"]}</p>\n'

    if 'documentation' in enhanced:
        html += '                            <div class="diff-addition"><strong>Documentation Provided:</strong></div>\n'
        html += f'                            <p>{enhanced["documentation"]}</p>\n'

    # Q2.1 - Ethics
    if 'ethical_considerations' in enhanced:
        html += '                            <div class="diff-improvement"><strong>Ethical Considerations:</strong></div>\n'
        html += f'                            <p>{enhanced["ethical_considerations"]}</p>\n'

    if 'data_provider_agreements' in enhanced:
        html += '                            <div class="diff-addition"><strong>Data Provider Agreements:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Provider</th><th>Terms</th></tr>\n'
        for a in enhanced['data_provider_agreements']:
            html += f'                                <tr><td>{a["provider"]}</td><td>{a["terms"]}, {a["restrictions"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'ethics_approval' in enhanced:
        html += f'                            <p><strong>{enhanced["ethics_approval"]}</strong></p>\n'

    # Q2.2 - Access
    if 'access_control' in enhanced:
        html += '                            <div class="diff-addition"><strong>Access Control Matrix:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Data Category</th><th>Access</th><th>Storage</th></tr>\n'
        for c in enhanced['access_control']:
            html += f'                                <tr><td>{c["category"]}</td><td>{c["access"]}</td><td>{c["storage"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'security_measures' in enhanced:
        html += '                            <div class="diff-addition"><strong>Security Measures:</strong></div>\n'
        html += f'                            <p>{enhanced["security_measures"]}</p>\n'

    if 'team_members' in enhanced:
        html += '                            <div class="diff-addition"><strong>Authorized Team:</strong></div>\n'
        html += '                            <ul>\n'
        for m in enhanced['team_members']:
            html += f'                                <li>{m["name"]} ({m["role"]})</li>\n'
        html += '                            </ul>\n'

    # Q2.3 - Copyright
    if 'copyright_framework' in enhanced:
        html += '                            <div class="diff-addition"><strong>Copyright Framework:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Data</th><th>Copyright</th><th>Our Rights</th></tr>\n'
        for f in enhanced['copyright_framework']:
            html += f'                                <tr><td>{f["data"]}</td><td>{f["holder"]}</td><td>{f["rights"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'publication_rights' in enhanced:
        html += '                            <div class="diff-addition"><strong>Publication Rights:</strong></div>\n'
        html += '                            <ul>\n'
        for r in enhanced['publication_rights'].get('allowed', []):
            html += f'                                <li>{r}: Yes</li>\n'
        for r in enhanced['publication_rights'].get('not_allowed', []):
            html += f'                                <li>{r}: No</li>\n'
        html += '                            </ul>\n'

    # Q3.1 - Storage
    if 'primary_storage' in enhanced:
        ps = enhanced['primary_storage']
        html += '                            <div class="diff-improvement"><strong>Primary Storage:</strong></div>\n'
        html += '                            <ul>\n'
        html += f'                                <li><strong>Location:</strong> {ps["location"]}</li>\n'
        html += f'                                <li><strong>Capacity:</strong> {ps["capacity"]}</li>\n'
        html += f'                                <li><strong>Retention:</strong> {ps["retention"]}</li>\n'
        html += '                            </ul>\n'

    if 'cloud_storage' in enhanced:
        html += '                            <div class="diff-addition"><strong>Cloud Storage:</strong></div>\n'
        html += '                            <ul>\n'
        for s in enhanced['cloud_storage']:
            url = s["url"] if s["url"].startswith("http") else ""
            if url:
                html += f'                                <li>{s["platform"]}: <a href="{url}">{url.replace("https://", "")}</a></li>\n'
            else:
                html += f'                                <li>{s["platform"]}: {s["url"]}</li>\n'
        html += '                            </ul>\n'

    if 'backup_strategy' in enhanced:
        html += '                            <div class="diff-addition"><strong>Backup Strategy:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Type</th><th>Frequency</th><th>Retention</th></tr>\n'
        for s in enhanced['backup_strategy']:
            html += f'                                <tr><td>{s["type"]}</td><td>{s["frequency"]}</td><td>{s["retention"]} ({s["location"]})</td></tr>\n'
        html += '                            </table>\n'

    # Q3.2 - Preservation
    if 'repository_selection' in enhanced:
        html += '                            <div class="diff-addition"><strong>Repository Selection:</strong></div>\n'
        html += '                            <ul>\n'
        for r in enhanced['repository_selection']:
            html += f'                                <li><strong>{r["name"]} ({r["organization"]}):</strong> {r["features"]}</li>\n'
        html += '                            </ul>\n'

    if 'preservation_timeline' in enhanced:
        html += '                            <div class="diff-addition"><strong>Preservation Timeline:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Milestone</th><th>Action</th></tr>\n'
        for t in enhanced['preservation_timeline']:
            html += f'                                <tr><td>{t["milestone"]}</td><td>{t["action"]} ({t["doi"]})</td></tr>\n'
        html += '                            </table>\n'

    if 'archival_formats' in enhanced:
        html += '                            <div class="diff-addition"><strong>Archival File Formats:</strong></div>\n'
        html += '                            <ul>\n'
        for k, v in enhanced['archival_formats'].items():
            html += f'                                <li>{k.title()}: {v}</li>\n'
        html += '                            </ul>\n'

    if 'retention_period' in enhanced:
        html += f'                            <div class="diff-improvement"><strong>Retention:</strong> {enhanced["retention_period"]}</div>\n'

    # Q4.1 - Sharing
    if 'current_outputs' in enhanced:
        html += '                            <div class="diff-addition"><strong>Current Outputs (Available Now):</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Output</th><th>Repository</th><th>Status</th></tr>\n'
        for o in enhanced['current_outputs']:
            url_short = o["url"].replace("https://", "")
            html += f'                                <tr><td>{o["name"]}</td><td><a href="{o["url"]}">{o["repository"]}</a></td><td>{o["status"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'upcoming_deposits' in enhanced:
        html += '                            <div class="diff-addition"><strong>Upcoming Deposits:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Output</th><th>Timeline</th></tr>\n'
        for d in enhanced['upcoming_deposits']:
            html += f'                                <tr><td>{d["name"]}</td><td>{d["timeline"]}</td></tr>\n'
        html += '                            </table>\n'

    if 'sharing_by_type' in enhanced:
        html += '                            <div class="diff-addition"><strong>Sharing Restrictions:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Data</th><th>Shareable?</th><th>Reason</th></tr>\n'
        for s in enhanced['sharing_by_type']:
            yn = 'Yes' if s['shareable'] else 'No'
            html += f'                                <tr><td>{s["data"]}</td><td>{yn}</td><td>{s["reason"]}</td></tr>\n'
        html += '                            </table>\n'

    # Q4.2 - Limitations
    if 'unrestricted' in enhanced:
        html += '                            <div class="diff-improvement"><strong>Unrestricted (Open Access):</strong></div>\n'
        html += '                            <ul>\n'
        for item in enhanced['unrestricted']:
            html += f'                                <li>{item}</li>\n'
        html += '                            </ul>\n'

    if 'restricted' in enhanced:
        html += '                            <div class="diff-addition"><strong>Restricted (Cannot Share):</strong></div>\n'
        html += '                            <ul>\n'
        for item in enhanced['restricted']:
            html += f'                                <li>{item}</li>\n'
        html += '                            </ul>\n'

    if 'reuse_conditions' in enhanced:
        html += '                            <div class="diff-addition"><strong>Reuse Conditions:</strong></div>\n'
        html += '                            <ul>\n'
        for item in enhanced['reuse_conditions']:
            html += f'                                <li>{item}</li>\n'
        html += '                            </ul>\n'

    if 'access_requests' in enhanced:
        html += f'                            <p><strong>Access Requests:</strong> <a href="mailto:{enhanced["access_requests"]}">{enhanced["access_requests"]}</a></p>\n'

    # Q4.3 & 4.4 - FAIR
    if 'answer' in enhanced:
        yn = 'Yes' if enhanced['answer'] else 'No'
        html += f'                            <p><strong>Answer:</strong> {yn}</p>\n'

    if 'fair_implementation' in enhanced:
        html += '                            <div class="diff-addition"><strong>FAIR Compliance Matrix:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Principle</th><th>Implementation</th></tr>\n'
        for k, v in enhanced['fair_implementation'].items():
            html += f'                                <tr><td><strong>{k.title()}</strong></td><td>{v}</td></tr>\n'
        html += '                            </table>\n'

    if 'repository_certification' in enhanced:
        html += '                            <div class="diff-addition"><strong>Repository Certification:</strong></div>\n'
        html += '                            <table>\n'
        html += '                                <tr><th>Repository</th><th>Organization</th><th>Certification</th></tr>\n'
        for c in enhanced['repository_certification']:
            html += f'                                <tr><td>{c["name"]}</td><td>{c["organization"]}</td><td>{c["certification"]}</td></tr>\n'
        html += '                            </table>\n'
        html += '                            <div class="diff-improvement" style="margin-top: 12px;">\n'
        html += '                                <strong>SNSF Checkboxes:</strong><br>\n'
        html += '                                [x] All repositories conform to FAIR Data Principles<br>\n'
        html += '                                [x] All repositories maintained by non-profit organizations\n'
        html += '                            </div>\n'

    return html


def main():
    parser = argparse.ArgumentParser(description='Generate DMP pages from JSON')
    parser.add_argument('--dry-run', action='store_true', help='Print output without writing files')
    args = parser.parse_args()

    # Paths
    repo_dir = Path(__file__).parent.parent
    json_path = repo_dir / 'data' / 'dmp-content.json'
    dmp_path = repo_dir / 'dmp.html'
    comparison_path = repo_dir / 'dmp-comparison.html'

    print(f"Loading DMP content from {json_path}")
    data = load_dmp_content(json_path)

    # Generate DMP HTML
    print("Generating dmp.html...")
    dmp_html = generate_dmp_html(data)

    # Generate comparison HTML
    print("Generating dmp-comparison.html...")
    comparison_html = generate_comparison_html(data)

    if args.dry_run:
        print("\n--- DMP.HTML (first 2000 chars) ---")
        print(dmp_html[:2000])
        print("\n--- COMPARISON.HTML (first 2000 chars) ---")
        print(comparison_html[:2000])
    else:
        with open(dmp_path, 'w', encoding='utf-8') as f:
            f.write(dmp_html)
        print(f"Written: {dmp_path}")

        with open(comparison_path, 'w', encoding='utf-8') as f:
            f.write(comparison_html)
        print(f"Written: {comparison_path}")

    print("\nDone! Both pages generated from single source.")


if __name__ == '__main__':
    main()
