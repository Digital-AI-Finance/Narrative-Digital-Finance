"""
OpenAlex Reference Verification Framework
Verifies bibliography entries against OpenAlex.org API
Auto-fixes missing DOIs, years, and other metadata
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from difflib import SequenceMatcher

import requests

# OpenAlex API configuration
OPENALEX_BASE = "https://api.openalex.org"
OPENALEX_EMAIL = "research@digital-ai-finance.org"  # For polite pool
REQUEST_DELAY = 0.15  # 150ms between requests (well under 10/sec limit)


@dataclass
class VerificationResult:
    """Result of verifying a single reference"""
    key: str
    status: str  # OK, WARN, ERROR
    bib_entry: dict
    openalex_data: Optional[dict] = None
    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    citation_count: int = 0
    issues: list = field(default_factory=list)
    fixes: list = field(default_factory=list)
    confidence: float = 0.0


def parse_bibtex(filepath: Path) -> list[dict]:
    """Parse BibTeX file into list of entry dictionaries"""
    content = filepath.read_text(encoding='utf-8')
    entries = []

    # Simple regex-based parser for common BibTeX format
    pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
    matches = re.findall(pattern, content, re.DOTALL)

    for entry_type, key, fields_str in matches:
        entry = {'type': entry_type, 'key': key.strip()}

        # Parse fields
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
        for field_name, field_value in re.findall(field_pattern, fields_str):
            entry[field_name.lower()] = field_value.strip()

        entries.append(entry)

    return entries


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Remove LaTeX special chars, extra spaces, lowercase
    text = re.sub(r'[{}\\_]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio"""
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def extract_authors(openalex_work: dict) -> list[str]:
    """Extract author names from OpenAlex work"""
    authors = []
    for authorship in openalex_work.get('authorships', []):
        author = authorship.get('author', {})
        name = author.get('display_name', '')
        if name:
            authors.append(name)
    return authors


def search_openalex(title: str, authors: str = "") -> Optional[dict]:
    """Search OpenAlex for a work by title"""
    # Clean title for search
    search_title = normalize_text(title)

    params = {
        'search': search_title,
        'mailto': OPENALEX_EMAIL,
        'per_page': 5
    }

    try:
        response = requests.get(f"{OPENALEX_BASE}/works", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get('results', [])
        if not results:
            return None

        # Find best match by title similarity
        best_match = None
        best_score = 0

        for work in results:
            work_title = work.get('title', '')
            if not work_title:
                continue

            score = similarity(title, work_title)

            # Boost score if author names match
            if authors:
                work_authors = ' '.join(extract_authors(work))
                author_score = similarity(authors, work_authors)
                score = score * 0.7 + author_score * 0.3

            if score > best_score:
                best_score = score
                best_match = work
                best_match['_match_score'] = score

        # Only return if confidence is high enough
        if best_match and best_score > 0.6:
            return best_match

        return None

    except requests.RequestException as e:
        print(f"  API error: {e}")
        return None


def verify_reference(bib_entry: dict) -> VerificationResult:
    """Verify a single BibTeX entry against OpenAlex"""
    result = VerificationResult(
        key=bib_entry['key'],
        status='ERROR',
        bib_entry=bib_entry
    )

    title = bib_entry.get('title', '')
    authors = bib_entry.get('author', '')

    if not title:
        result.issues.append("Missing title in BibTeX")
        return result

    print(f"  Searching: {title[:60]}...")
    time.sleep(REQUEST_DELAY)

    openalex = search_openalex(title, authors)

    if not openalex:
        result.issues.append("NOT FOUND in OpenAlex")
        return result

    result.openalex_data = openalex
    result.confidence = openalex.get('_match_score', 0)
    result.openalex_id = openalex.get('id', '').replace('https://openalex.org/', '')
    result.citation_count = openalex.get('cited_by_count', 0)

    # Extract DOI
    doi = openalex.get('doi', '')
    if doi:
        result.doi = doi.replace('https://doi.org/', '')

    # Check for issues and potential fixes
    issues = []
    fixes = []

    # DOI check
    bib_doi = bib_entry.get('doi', '')
    if result.doi and not bib_doi:
        fixes.append(('doi', result.doi, 'Added missing DOI'))

    # Year check
    bib_year = bib_entry.get('year', '')
    openalex_year = str(openalex.get('publication_year', ''))
    if bib_year and openalex_year and bib_year != openalex_year:
        year_diff = abs(int(bib_year) - int(openalex_year))
        if year_diff <= 2:
            fixes.append(('year', openalex_year, f'Year corrected: {bib_year} -> {openalex_year}'))
        else:
            issues.append(f"Year mismatch: bib={bib_year}, OpenAlex={openalex_year}")

    # Title similarity check
    openalex_title = openalex.get('title', '')
    title_sim = similarity(title, openalex_title)
    if title_sim < 0.9:
        issues.append(f"Title similarity: {title_sim:.0%}")

    # Volume/Pages check
    bib_vol = bib_entry.get('volume', '')
    bib_pages = bib_entry.get('pages', '')

    # OpenAlex biblio data
    biblio = openalex.get('biblio', {})
    oa_vol = biblio.get('volume', '')
    oa_first = biblio.get('first_page', '')
    oa_last = biblio.get('last_page', '')

    if oa_vol and not bib_vol:
        fixes.append(('volume', oa_vol, 'Added missing volume'))

    if oa_first and oa_last and not bib_pages:
        pages = f"{oa_first}--{oa_last}"
        fixes.append(('pages', pages, 'Added missing pages'))

    # Add OpenAlex ID
    if result.openalex_id:
        fixes.append(('openalex', result.openalex_id, 'Added OpenAlex ID'))

    result.issues = issues
    result.fixes = fixes

    # Determine status
    if issues:
        result.status = 'WARN'
    else:
        result.status = 'OK'

    return result


def generate_updated_bibtex(entries: list[dict], results: list[VerificationResult]) -> str:
    """Generate updated BibTeX content with fixes applied"""
    # Create lookup for fixes
    fixes_by_key = {r.key: r.fixes for r in results}

    output_lines = []

    for entry in entries:
        key = entry['key']
        entry_type = entry['type']
        fixes = fixes_by_key.get(key, [])

        # Apply fixes
        updated_entry = entry.copy()
        for field, value, _ in fixes:
            updated_entry[field] = value

        # Generate BibTeX
        output_lines.append(f"@{entry_type}{{{key},")

        # Standard field order
        field_order = ['author', 'title', 'journal', 'volume', 'number', 'pages', 'year', 'doi', 'openalex']

        # Add fields in order
        added_fields = set()
        for field in field_order:
            if field in updated_entry and field not in ['type', 'key']:
                output_lines.append(f"  {field} = {{{updated_entry[field]}}},")
                added_fields.add(field)

        # Add any remaining fields
        for field, value in updated_entry.items():
            if field not in added_fields and field not in ['type', 'key']:
                output_lines.append(f"  {field} = {{{value}}},")

        output_lines.append("}")
        output_lines.append("")

    return "\n".join(output_lines)


def generate_html_report(results: list[VerificationResult]) -> str:
    """Generate HTML report of verification results"""
    ok_count = sum(1 for r in results if r.status == 'OK')
    warn_count = sum(1 for r in results if r.status == 'WARN')
    error_count = sum(1 for r in results if r.status == 'ERROR')
    total_fixes = sum(len(r.fixes) for r in results)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reference Verification Report</title>
    <style>
        :root {{
            --primary: #1a5f7a;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --bg: #f8fafc;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            background: var(--bg);
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: var(--primary); margin-bottom: 20px; }}
        .summary {{
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-width: 120px;
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; }}
        .stat-label {{ font-size: 0.9rem; color: #666; }}
        .stat-ok .stat-value {{ color: var(--success); }}
        .stat-warn .stat-value {{ color: var(--warning); }}
        .stat-error .stat-value {{ color: var(--error); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: var(--primary); color: white; }}
        tr:hover {{ background: #f8fafc; }}
        .status-ok {{ color: var(--success); font-weight: bold; }}
        .status-warn {{ color: var(--warning); font-weight: bold; }}
        .status-error {{ color: var(--error); font-weight: bold; }}
        .doi-link {{ color: var(--primary); text-decoration: none; }}
        .doi-link:hover {{ text-decoration: underline; }}
        .issues {{ font-size: 0.85rem; color: #666; }}
        .fixes {{ font-size: 0.85rem; color: var(--success); }}
        .timestamp {{ margin-top: 30px; color: #666; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Reference Verification Report</h1>

        <div class="summary">
            <div class="stat">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">Total References</div>
            </div>
            <div class="stat stat-ok">
                <div class="stat-value">{ok_count}</div>
                <div class="stat-label">Verified</div>
            </div>
            <div class="stat stat-warn">
                <div class="stat-value">{warn_count}</div>
                <div class="stat-label">Warnings</div>
            </div>
            <div class="stat stat-error">
                <div class="stat-value">{error_count}</div>
                <div class="stat-label">Errors</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_fixes}</div>
                <div class="stat-label">Auto-fixes Applied</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Citation Key</th>
                    <th>Title</th>
                    <th>Year</th>
                    <th>DOI</th>
                    <th>Citations</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
"""

    for r in results:
        status_class = f"status-{r.status.lower()}"
        title = r.bib_entry.get('title', '')[:50] + ('...' if len(r.bib_entry.get('title', '')) > 50 else '')
        year = r.bib_entry.get('year', '-')

        doi_cell = '-'
        if r.doi:
            doi_cell = f'<a href="https://doi.org/{r.doi}" class="doi-link" target="_blank">{r.doi[:25]}...</a>'

        notes = []
        if r.issues:
            notes.append(f'<span class="issues">{"; ".join(r.issues)}</span>')
        if r.fixes:
            fix_msgs = [f[2] for f in r.fixes]
            notes.append(f'<span class="fixes">{"; ".join(fix_msgs)}</span>')
        notes_html = '<br>'.join(notes) if notes else '-'

        openalex_link = ''
        if r.openalex_id:
            openalex_link = f' <a href="https://openalex.org/{r.openalex_id}" target="_blank">[OA]</a>'

        html += f"""                <tr>
                    <td class="{status_class}">{r.status}</td>
                    <td>{r.key}{openalex_link}</td>
                    <td>{title}</td>
                    <td>{year}</td>
                    <td>{doi_cell}</td>
                    <td>{r.citation_count:,}</td>
                    <td>{notes_html}</td>
                </tr>
"""

    html += f"""            </tbody>
        </table>

        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Verified against OpenAlex.org</p>
    </div>
</body>
</html>
"""
    return html


def generate_json_report(results: list[VerificationResult]) -> str:
    """Generate JSON report of verification results"""
    report = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total': len(results),
            'ok': sum(1 for r in results if r.status == 'OK'),
            'warnings': sum(1 for r in results if r.status == 'WARN'),
            'errors': sum(1 for r in results if r.status == 'ERROR'),
            'total_fixes': sum(len(r.fixes) for r in results),
            'total_citations': sum(r.citation_count for r in results)
        },
        'references': []
    }

    for r in results:
        ref = {
            'key': r.key,
            'status': r.status,
            'confidence': round(r.confidence, 3),
            'doi': r.doi,
            'openalex_id': r.openalex_id,
            'citation_count': r.citation_count,
            'issues': r.issues,
            'fixes': [{'field': f[0], 'value': f[1], 'note': f[2]} for f in r.fixes],
            'bib_entry': r.bib_entry
        }
        report['references'].append(ref)

    return json.dumps(report, indent=2)


def main():
    """Main verification workflow"""
    print("=" * 60)
    print("OpenAlex Reference Verification Framework")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    bib_path = script_dir / "bibliography.bib"

    if not bib_path.exists():
        print(f"ERROR: {bib_path} not found")
        return

    # Parse BibTeX
    print(f"\nParsing {bib_path}...")
    entries = parse_bibtex(bib_path)
    print(f"Found {len(entries)} references")

    # Verify each reference
    print("\nVerifying references against OpenAlex...")
    results = []

    for i, entry in enumerate(entries, 1):
        print(f"\n[{i}/{len(entries)}] {entry['key']}")
        result = verify_reference(entry)
        results.append(result)

        if result.status == 'OK':
            print(f"  [OK] DOI: {result.doi or 'N/A'}, Citations: {result.citation_count:,}")
        elif result.status == 'WARN':
            print(f"  [WARN] {'; '.join(result.issues)}")
            if result.fixes:
                print(f"  [FIXED] {'; '.join(f[2] for f in result.fixes)}")
        else:
            print(f"  [ERROR] {'; '.join(result.issues)}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    ok = sum(1 for r in results if r.status == 'OK')
    warn = sum(1 for r in results if r.status == 'WARN')
    err = sum(1 for r in results if r.status == 'ERROR')
    fixes = sum(len(r.fixes) for r in results)

    print(f"Total: {len(results)} | OK: {ok} | Warnings: {warn} | Errors: {err}")
    print(f"Auto-fixes applied: {fixes}")

    # Generate updated BibTeX
    if fixes > 0:
        print(f"\nUpdating {bib_path}...")
        updated_bib = generate_updated_bibtex(entries, results)
        bib_path.write_text(updated_bib, encoding='utf-8')
        print(f"  Updated with {fixes} fixes")

    # Generate reports
    html_path = script_dir / "reference_report.html"
    json_path = script_dir / "reference_report.json"

    print(f"\nGenerating reports...")
    html_path.write_text(generate_html_report(results), encoding='utf-8')
    print(f"  HTML: {html_path}")

    json_path.write_text(generate_json_report(results), encoding='utf-8')
    print(f"  JSON: {json_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
