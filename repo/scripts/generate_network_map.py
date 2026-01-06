"""
Generate Interactive Network Map for COST Action CA19130

Reads data directly from COST_Network source repository and generates
an SVG-based interactive map with verified statistics.

Author: Prof. Dr. Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

# Source data path
COST_DATA_SOURCE = Path(r"D:\Joerg\Research\slides\COST_Network\data")
REPO_DIR = Path(__file__).parent.parent

# Country code mappings (source uses different codes)
CODE_MAPPING = {
    "EL": "GR",  # Greece
    "UK": "GB",  # United Kingdom
    "KV": "XK",  # Kosovo
}

# Country name to ISO code mapping
NAME_TO_CODE = {
    "Albania": "AL", "Austria": "AT", "Belgium": "BE", "Bosnia and Herzegovina": "BA",
    "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY", "Czech Republic": "CZ",
    "Czechia": "CZ", "Denmark": "DK", "Estonia": "EE", "Finland": "FI",
    "France": "FR", "Germany": "DE", "Greece": "GR", "Hungary": "HU",
    "Iceland": "IS", "Ireland": "IE", "Israel": "IL", "Italy": "IT",
    "Kosovo*": "XK", "Latvia": "LV", "Liechtenstein": "LI", "Lithuania": "LT",
    "Luxembourg": "LU", "Malta": "MT", "Moldova": "MD", "Montenegro": "ME",
    "Netherlands": "NL", "North Macedonia": "MK", "Norway": "NO", "Poland": "PL",
    "Portugal": "PT", "Romania": "RO", "Serbia": "RS", "Slovakia": "SK",
    "Slovenia": "SI", "Spain": "ES", "Sweden": "SE", "Switzerland": "CH",
    "T\u00fcrkiye": "TR", "Turkey": "TR", "Ukraine": "UA", "United Kingdom": "GB",
    "United States": "US", "New Zealand": "NZ", "Singapore": "SG",
    "Taiwan": "TW", "Vietnam": "VN", "Nigeria": "NG", "Algeria": "DZ",
    "United Arab Emirates": "AE",
}

# ITC (Inclusiveness Target Countries) list
ITC_COUNTRIES = {
    "AL", "BA", "BG", "CY", "CZ", "EE", "GR", "HR", "HU", "LT", "LV",
    "MD", "ME", "MK", "MT", "PL", "PT", "RO", "RS", "SI", "SK", "TR", "UA", "XK"
}

# Country coordinates for European map (lon, lat)
COUNTRY_COORDS = {
    "AL": (20.0, 41.0), "AT": (13.3, 47.5), "BA": (17.8, 43.9), "BE": (4.4, 50.8),
    "BG": (25.5, 42.7), "CH": (8.2, 46.8), "CY": (33.4, 35.1), "CZ": (14.5, 49.8),
    "DE": (10.4, 51.2), "DK": (9.5, 56.3), "EE": (25.0, 58.6), "ES": (-3.7, 40.4),
    "FI": (25.7, 61.9), "FR": (2.2, 46.2), "GB": (-3.4, 55.4), "GR": (21.8, 39.1),
    "HR": (15.2, 45.1), "HU": (19.5, 47.2), "IE": (-8.2, 53.4), "IS": (-19.0, 65.0),
    "IT": (12.6, 41.9), "LI": (9.6, 47.2), "LT": (23.9, 55.2), "LU": (6.1, 49.8),
    "LV": (24.6, 56.9), "MD": (28.8, 47.0), "ME": (19.3, 42.7), "MK": (21.7, 41.5),
    "MT": (14.4, 35.9), "NL": (5.3, 52.1), "NO": (8.5, 60.5), "PL": (19.1, 51.9),
    "PT": (-8.2, 39.4), "RO": (24.9, 46.0), "RS": (21.0, 44.0), "SE": (18.6, 60.1),
    "SI": (14.5, 46.2), "SK": (19.7, 48.7), "TR": (35.2, 39.0), "UA": (31.2, 48.4),
    "XK": (20.9, 42.6), "IL": (35.0, 31.5), "US": (-95.7, 37.1),
}

# Country names
COUNTRY_NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium",
    "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "ES": "Spain",
    "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece",
    "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IS": "Iceland",
    "IT": "Italy", "LI": "Liechtenstein", "LT": "Lithuania", "LU": "Luxembourg",
    "LV": "Latvia", "MD": "Moldova", "ME": "Montenegro", "MK": "North Macedonia",
    "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UA": "Ukraine",
    "XK": "Kosovo", "IL": "Israel", "US": "United States",
}


@dataclass
class CountryStats:
    """Statistics for a single country."""
    code: str
    name: str
    is_itc: bool
    wg_members: int = 0
    financial_participants: int = 0
    total_funding: float = 0.0

    @property
    def display_participants(self) -> int:
        """Use WG members as the participant count."""
        return self.wg_members


@dataclass
class NetworkStats:
    """Overall network statistics."""
    total_wg_members: int
    unique_wg_members: int
    total_countries: int
    itc_countries: int
    non_itc_countries: int
    total_funding: float
    countries: Dict[str, CountryStats]


def load_source_data() -> NetworkStats:
    """Load and validate data from COST_Network source."""

    if not COST_DATA_SOURCE.exists():
        raise FileNotFoundError(f"COST data source not found: {COST_DATA_SOURCE}")

    countries: Dict[str, CountryStats] = {}

    # Load WG members for participant counts by country
    wg_file = COST_DATA_SOURCE / "wg_members.json"
    if wg_file.exists():
        with open(wg_file, 'r', encoding='utf-8') as f:
            wg_data = json.load(f)

        wgs = wg_data.get('workingGroups', {})
        country_members: Dict[str, set] = {}

        for wg_key, wg_info in wgs.items():
            members = wg_info.get('members', [])
            for member in members:
                if isinstance(member, dict):
                    country_name = member.get('country', '')
                    member_name = member.get('name', '')
                    if country_name and member_name:
                        # Skip invalid entries
                        if country_name in ['Unknown', 'International Organisations']:
                            continue
                        code = NAME_TO_CODE.get(country_name)
                        if code:
                            if code not in country_members:
                                country_members[code] = set()
                            country_members[code].add(member_name)

        # Create country stats from WG data
        for code, members in country_members.items():
            name = COUNTRY_NAMES.get(code, code)
            is_itc = code in ITC_COUNTRIES
            countries[code] = CountryStats(
                code=code,
                name=name,
                is_itc=is_itc,
                wg_members=len(members)
            )

    # Load financial statistics
    fin_file = COST_DATA_SOURCE / "country_statistics_full.json"
    if fin_file.exists():
        with open(fin_file, 'r', encoding='utf-8') as f:
            fin_data = json.load(f)

        for entry in fin_data:
            code = entry.get('code', '')
            if not code:
                continue
            # Map to standard codes
            code = CODE_MAPPING.get(code, code)

            if code in countries:
                countries[code].financial_participants = entry.get('unique_participant_count', 0)
                countries[code].total_funding = entry.get('total_amount', 0.0)
            else:
                # Country with financial data but no WG members (shouldn't happen)
                name = COUNTRY_NAMES.get(code, code)
                is_itc = code in ITC_COUNTRIES
                countries[code] = CountryStats(
                    code=code,
                    name=name,
                    is_itc=is_itc,
                    financial_participants=entry.get('unique_participant_count', 0),
                    total_funding=entry.get('total_amount', 0.0)
                )

    # Calculate totals
    total_wg = sum(c.wg_members for c in countries.values())
    itc_count = sum(1 for c in countries.values() if c.is_itc and c.wg_members > 0)
    non_itc_count = sum(1 for c in countries.values() if not c.is_itc and c.wg_members > 0)
    total_funding = sum(c.total_funding for c in countries.values())
    active_countries = sum(1 for c in countries.values() if c.wg_members > 0)

    return NetworkStats(
        total_wg_members=total_wg,
        unique_wg_members=total_wg,  # Already deduplicated
        total_countries=active_countries,
        itc_countries=itc_count,
        non_itc_countries=non_itc_count,
        total_funding=total_funding,
        countries=countries
    )


def generate_map_html(stats: NetworkStats) -> str:
    """Generate the interactive network map HTML/JS code."""

    # Filter to countries with coordinates and participants
    active_countries = [
        c for c in stats.countries.values()
        if c.wg_members > 0 and c.code in COUNTRY_COORDS
    ]

    # Sort by participant count for layering
    active_countries.sort(key=lambda x: -x.wg_members)

    itc_count = sum(1 for c in active_countries if c.is_itc)
    non_itc_count = len(active_countries) - itc_count

    html = f'''
    <!-- Network Map Section - Auto-generated from COST_Network data -->
    <section class="section" id="network-map" style="margin-bottom: 24px;">
        <div class="section-title" style="font-size: 15px; font-weight: 600; color: var(--color-dark); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--color-primary);">
            Interactive Network Map
        </div>

        <div style="display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #3b82f6; border-radius: 50%;"></div>
                <span style="font-size: 11px;">Non-ITC Countries ({non_itc_count})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 16px; height: 16px; background: #10b981; border-radius: 50%;"></div>
                <span style="font-size: 11px;">ITC Countries ({itc_count})</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 11px; color: #64748b;">Circle size = WG member count</span>
            </div>
        </div>

        <div id="map-container" style="position: relative; width: 100%; height: 450px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 8px; overflow: hidden;">
            <svg id="network-map-svg" viewBox="-30 25 100 55" preserveAspectRatio="xMidYMid meet" style="width: 100%; height: 100%;">
                <!-- Grid lines -->
                <defs>
                    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                        <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#cbd5e1" stroke-width="0.1"/>
                    </pattern>
                </defs>
                <rect x="-30" y="25" width="100" height="55" fill="url(#grid)"/>

                <!-- Connection lines to Switzerland (hub) -->
                <g id="connections" opacity="0.3">
'''

    # Add connection lines from each country to Switzerland
    ch_coords = COUNTRY_COORDS.get("CH", (8.2, 46.8))
    ch_x, ch_y = ch_coords[0], 90 - ch_coords[1]

    for country in active_countries:
        if country.code != "CH" and country.code in COUNTRY_COORDS:
            coords = COUNTRY_COORDS[country.code]
            x, y = coords[0], 90 - coords[1]
            color = "#10b981" if country.is_itc else "#3b82f6"
            html += f'                    <line x1="{ch_x}" y1="{ch_y}" x2="{x}" y2="{y}" stroke="{color}" stroke-width="0.15"/>\n'

    html += '''                </g>

                <!-- Country circles -->
                <g id="countries">
'''

    # Add country circles
    max_members = max(c.wg_members for c in active_countries) if active_countries else 1

    for country in active_countries:
        if country.code in COUNTRY_COORDS:
            coords = COUNTRY_COORDS[country.code]
            x, y = coords[0], 90 - coords[1]

            # Size based on members (min 1.5, max 5)
            size = 1.5 + (country.wg_members / max_members) * 3.5

            color = "#10b981" if country.is_itc else "#3b82f6"
            itc_label = "ITC" if country.is_itc else "Non-ITC"

            html += f'''                    <g class="country-node" data-country="{country.code}" data-name="{country.name}" data-members="{country.wg_members}" data-funding="{country.total_funding:.0f}" data-itc="{itc_label}" style="cursor: pointer;">
                        <circle cx="{x}" cy="{y}" r="{size:.1f}" fill="{color}" opacity="0.8" stroke="white" stroke-width="0.3"/>
                        <text x="{x}" y="{y + 0.5}" text-anchor="middle" font-size="1.5" fill="white" font-weight="bold" pointer-events="none">{country.code}</text>
                    </g>
'''

    html += '''                </g>

                <!-- Switzerland highlight -->
                <g id="hub-marker">
                    <circle cx="8.2" cy="43.2" r="6" fill="none" stroke="#f59e0b" stroke-width="0.4" stroke-dasharray="1"/>
                    <text x="8.2" y="38" text-anchor="middle" font-size="2" fill="#f59e0b" font-weight="bold">SNSF Hub</text>
                </g>
            </svg>

            <!-- Tooltip -->
            <div id="map-tooltip" style="display: none; position: absolute; background: white; padding: 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; z-index: 100; min-width: 180px;">
                <div id="tooltip-name" style="font-weight: 600; font-size: 14px; margin-bottom: 8px;"></div>
                <div id="tooltip-content" style="font-size: 12px; color: #475569;"></div>
            </div>
        </div>

        <p style="font-size: 10px; color: #64748b; margin-top: 12px; text-align: center;">
            Data source: COST Action CA19130 (wg_members.json, country_statistics_full.json). Switzerland (SNSF Hub) shown with amber ring.
        </p>
    </section>

    <script>
    (function() {
        const tooltip = document.getElementById('map-tooltip');
        const tooltipName = document.getElementById('tooltip-name');
        const tooltipContent = document.getElementById('tooltip-content');
        const container = document.getElementById('map-container');

        document.querySelectorAll('.country-node').forEach(node => {
            node.addEventListener('mouseenter', function(e) {
                const name = this.dataset.name;
                const members = this.dataset.members;
                const funding = parseFloat(this.dataset.funding);
                const fundingStr = funding > 0 ? funding.toLocaleString('en-US', {style: 'currency', currency: 'EUR', maximumFractionDigits: 0}) : 'N/A';
                const itc = this.dataset.itc;

                tooltipName.textContent = name + ' (' + this.dataset.country + ')';
                tooltipContent.innerHTML =
                    '<div style="margin-bottom: 4px;"><strong>WG Members:</strong> ' + members + '</div>' +
                    '<div style="margin-bottom: 4px;"><strong>Total funding:</strong> ' + fundingStr + '</div>' +
                    '<div><strong>Status:</strong> ' + itc + '</div>';

                tooltip.style.display = 'block';
                this.querySelector('circle').setAttribute('opacity', '1');
                this.querySelector('circle').setAttribute('stroke-width', '0.6');
            });

            node.addEventListener('mouseleave', function() {
                tooltip.style.display = 'none';
                this.querySelector('circle').setAttribute('opacity', '0.8');
                this.querySelector('circle').setAttribute('stroke-width', '0.3');
            });

            node.addEventListener('mousemove', function(e) {
                const rect = container.getBoundingClientRect();
                let x = e.clientX - rect.left + 15;
                let y = e.clientY - rect.top + 15;
                if (x + 200 > rect.width) x = e.clientX - rect.left - 195;
                if (y + 100 > rect.height) y = e.clientY - rect.top - 105;
                tooltip.style.left = x + 'px';
                tooltip.style.top = y + 'px';
            });
        });
    })();
    </script>
'''

    return html


def update_network_page(stats: NetworkStats) -> bool:
    """Update cost-network.html with the interactive map and correct stats."""
    network_page = REPO_DIR / "cost-network.html"

    if not network_page.exists():
        print(f"Error: {network_page} not found")
        return False

    content = network_page.read_text(encoding='utf-8')

    # Generate the map HTML
    map_html = generate_map_html(stats)

    # Remove existing map section if present
    map_pattern = r'<!-- Network Map Section.*?</script>\s*\n'
    content = re.sub(map_pattern, '', content, flags=re.DOTALL)

    # Find insertion point (after breadcrumb)
    insertion_marker = '<div class="breadcrumb">'
    if insertion_marker in content:
        idx = content.find(insertion_marker)
        end_of_line = content.find('\n', idx)
        new_content = content[:end_of_line + 1] + '\n' + map_html + '\n' + content[end_of_line + 1:]

        # Update hero stats with correct numbers
        new_content = re.sub(
            r'(\d+)\+?\s*Researchers',
            f'{stats.unique_wg_members}+ Researchers',
            new_content
        )
        new_content = re.sub(
            r'(\d+)\s*Countries',
            f'{stats.total_countries} Countries',
            new_content
        )

        network_page.write_text(new_content, encoding='utf-8')
        print(f"Updated {network_page}")
        print(f"  - Total WG members: {stats.unique_wg_members}")
        print(f"  - Countries: {stats.total_countries} ({stats.itc_countries} ITC, {stats.non_itc_countries} non-ITC)")
        print(f"  - Total funding: EUR {stats.total_funding:,.0f}")
        return True
    else:
        print("Could not find insertion point")
        return False


def get_stats_summary() -> dict:
    """Get a summary of stats for testing."""
    stats = load_source_data()
    return {
        'unique_wg_members': stats.unique_wg_members,
        'total_countries': stats.total_countries,
        'itc_countries': stats.itc_countries,
        'non_itc_countries': stats.non_itc_countries,
        'total_funding': stats.total_funding,
        'countries_with_data': len([c for c in stats.countries.values() if c.wg_members > 0])
    }


if __name__ == "__main__":
    print("Loading COST Action CA19130 network data...")
    stats = load_source_data()
    print(f"\nNetwork Statistics:")
    print(f"  Total WG members: {stats.unique_wg_members}")
    print(f"  Countries: {stats.total_countries}")
    print(f"  ITC countries: {stats.itc_countries}")
    print(f"  Non-ITC countries: {stats.non_itc_countries}")
    print(f"  Total funding: EUR {stats.total_funding:,.0f}")
    print(f"\nUpdating cost-network.html...")
    update_network_page(stats)
