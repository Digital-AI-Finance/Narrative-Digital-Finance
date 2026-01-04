"""
Generate Interactive Network Map for COST Action CA19130

Creates an SVG-based interactive map showing 55 participating countries
with hover effects, tooltips, and ITC/non-ITC classification.

Author: Prof. Dr. Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
"""

import json
from pathlib import Path

# Country data from COST Network
COUNTRY_DATA = [
    {"code": "RO", "name": "Romania", "is_itc": True, "participants": 23, "total": 71345},
    {"code": "CH", "name": "Switzerland", "is_itc": False, "participants": 19, "total": 41967},
    {"code": "IT", "name": "Italy", "is_itc": False, "participants": 17, "total": 35880},
    {"code": "AL", "name": "Albania", "is_itc": True, "participants": 17, "total": 22311},
    {"code": "TR", "name": "Turkey", "is_itc": True, "participants": 13, "total": 24593},
    {"code": "MK", "name": "North Macedonia", "is_itc": True, "participants": 11, "total": 18640},
    {"code": "NL", "name": "Netherlands", "is_itc": False, "participants": 10, "total": 20351},
    {"code": "DE", "name": "Germany", "is_itc": False, "participants": 10, "total": 19517},
    {"code": "IE", "name": "Ireland", "is_itc": False, "participants": 10, "total": 16962},
    {"code": "PL", "name": "Poland", "is_itc": True, "participants": 7, "total": 24975},
    {"code": "CZ", "name": "Czechia", "is_itc": True, "participants": 6, "total": 11296},
    {"code": "GR", "name": "Greece", "is_itc": True, "participants": 5, "total": 15564},
    {"code": "SK", "name": "Slovakia", "is_itc": True, "participants": 5, "total": 5524},
    {"code": "FR", "name": "France", "is_itc": False, "participants": 4, "total": 11664},
    {"code": "GB", "name": "United Kingdom", "is_itc": False, "participants": 4, "total": 3237},
    {"code": "XK", "name": "Kosovo", "is_itc": True, "participants": 3, "total": 8265},
    {"code": "LT", "name": "Lithuania", "is_itc": True, "participants": 3, "total": 3805},
    {"code": "ES", "name": "Spain", "is_itc": False, "participants": 3, "total": 3164},
    {"code": "HU", "name": "Hungary", "is_itc": True, "participants": 3, "total": 2670},
    {"code": "HR", "name": "Croatia", "is_itc": True, "participants": 3, "total": 1182},
    {"code": "IS", "name": "Iceland", "is_itc": False, "participants": 2, "total": 5564},
    {"code": "PT", "name": "Portugal", "is_itc": True, "participants": 2, "total": 2468},
    {"code": "LV", "name": "Latvia", "is_itc": True, "participants": 2, "total": 2231},
    {"code": "UA", "name": "Ukraine", "is_itc": True, "participants": 2, "total": 1440},
    {"code": "US", "name": "United States", "is_itc": False, "participants": 2, "total": 1325},
    {"code": "NO", "name": "Norway", "is_itc": False, "participants": 2, "total": 598},
    {"code": "CY", "name": "Cyprus", "is_itc": True, "participants": 2, "total": 406},
    {"code": "AT", "name": "Austria", "is_itc": False, "participants": 1, "total": 1467},
    {"code": "IL", "name": "Israel", "is_itc": False, "participants": 1, "total": 867},
    {"code": "LI", "name": "Liechtenstein", "is_itc": False, "participants": 1, "total": 442},
    {"code": "BE", "name": "Belgium", "is_itc": False, "participants": 1, "total": 308},
    {"code": "BG", "name": "Bulgaria", "is_itc": True, "participants": 1, "total": 197},
    {"code": "FI", "name": "Finland", "is_itc": False, "participants": 1, "total": 166},
    {"code": "RS", "name": "Serbia", "is_itc": True, "participants": 1, "total": 129},
    {"code": "EE", "name": "Estonia", "is_itc": True, "participants": 1, "total": 83},
    {"code": "BA", "name": "Bosnia and Herzegovina", "is_itc": True, "participants": 1, "total": 14},
    # Additional COST member countries (with 0 participants shown for completeness)
    {"code": "SI", "name": "Slovenia", "is_itc": True, "participants": 0, "total": 0},
    {"code": "ME", "name": "Montenegro", "is_itc": True, "participants": 0, "total": 0},
    {"code": "LU", "name": "Luxembourg", "is_itc": False, "participants": 0, "total": 0},
    {"code": "MT", "name": "Malta", "is_itc": True, "participants": 0, "total": 0},
    {"code": "DK", "name": "Denmark", "is_itc": False, "participants": 0, "total": 0},
    {"code": "SE", "name": "Sweden", "is_itc": False, "participants": 0, "total": 0},
]

# Approximate country center coordinates for Europe-focused map
COUNTRY_COORDS = {
    "AL": (20.0, 41.0), "AT": (13.3, 47.5), "BA": (17.8, 43.9), "BE": (4.4, 50.8),
    "BG": (25.5, 42.7), "CH": (8.2, 46.8), "CY": (33.4, 35.1), "CZ": (14.5, 49.8),
    "DE": (10.4, 51.2), "DK": (9.5, 56.3), "EE": (25.0, 58.6), "ES": (-3.7, 40.4),
    "FI": (25.7, 61.9), "FR": (2.2, 46.2), "GB": (-3.4, 55.4), "GR": (21.8, 39.1),
    "HR": (15.2, 45.1), "HU": (19.5, 47.2), "IE": (-8.2, 53.4), "IS": (-19.0, 65.0),
    "IT": (12.6, 41.9), "LI": (9.6, 47.2), "LT": (23.9, 55.2), "LU": (6.1, 49.8),
    "LV": (24.6, 56.9), "ME": (19.3, 42.7), "MK": (21.7, 41.5), "MT": (14.4, 35.9),
    "NL": (5.3, 52.1), "NO": (8.5, 60.5), "PL": (19.1, 51.9), "PT": (-8.2, 39.4),
    "RO": (24.9, 46.0), "RS": (21.0, 44.0), "SE": (18.6, 60.1), "SI": (14.5, 46.2),
    "SK": (19.7, 48.7), "TR": (35.2, 39.0), "UA": (31.2, 48.4), "XK": (20.9, 42.6),
    "IL": (35.0, 31.5), "US": (-95.7, 37.1),
}

def generate_network_map_html():
    """Generate the interactive network map HTML/JS code."""

    # Filter countries with participants
    active_countries = [c for c in COUNTRY_DATA if c["participants"] > 0]

    # Calculate statistics
    total_participants = sum(c["participants"] for c in active_countries)
    itc_count = sum(1 for c in active_countries if c["is_itc"])
    non_itc_count = len(active_countries) - itc_count

    html = f'''
    <!-- Network Map Section -->
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
                <span style="font-size: 11px; color: #64748b;">Circle size = participant count</span>
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
    for country in active_countries:
        if country["code"] != "CH" and country["code"] in COUNTRY_COORDS:
            coords = COUNTRY_COORDS[country["code"]]
            color = "#10b981" if country["is_itc"] else "#3b82f6"
            html += f'                    <line x1="{ch_coords[0]}" y1="{90-ch_coords[1]}" x2="{coords[0]}" y2="{90-coords[1]}" stroke="{color}" stroke-width="0.15"/>\n'

    html += '''                </g>

                <!-- Country circles -->
                <g id="countries">
'''

    # Add country circles (sorted by size so smaller ones are on top)
    for country in sorted(active_countries, key=lambda x: -x["participants"]):
        if country["code"] in COUNTRY_COORDS:
            coords = COUNTRY_COORDS[country["code"]]
            x, y = coords[0], 90 - coords[1]  # Flip Y for SVG

            # Size based on participants (min 1.5, max 5)
            size = min(5, max(1.5, country["participants"] / 5))

            color = "#10b981" if country["is_itc"] else "#3b82f6"
            itc_label = "ITC" if country["is_itc"] else "Non-ITC"

            html += f'''                    <g class="country-node" data-country="{country['code']}" data-name="{country['name']}" data-participants="{country['participants']}" data-total="{country['total']}" data-itc="{itc_label}" style="cursor: pointer;">
                        <circle cx="{x}" cy="{y}" r="{size}" fill="{color}" opacity="0.8" stroke="white" stroke-width="0.3"/>
                        <text x="{x}" y="{y + 0.5}" text-anchor="middle" font-size="1.5" fill="white" font-weight="bold" pointer-events="none">{country['code']}</text>
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
            Hover over countries to see details. Switzerland (SNSF Hub) shown with amber ring. ITC = Inclusiveness Target Countries.
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
                const participants = this.dataset.participants;
                const total = parseFloat(this.dataset.total).toLocaleString('en-US', {style: 'currency', currency: 'EUR', maximumFractionDigits: 0});
                const itc = this.dataset.itc;

                tooltipName.textContent = name + ' (' + this.dataset.country + ')';
                tooltipContent.innerHTML =
                    '<div style="margin-bottom: 4px;"><strong>Participants:</strong> ' + participants + '</div>' +
                    '<div style="margin-bottom: 4px;"><strong>Total funding:</strong> ' + total + '</div>' +
                    '<div><strong>Status:</strong> ' + itc + '</div>';

                tooltip.style.display = 'block';

                // Highlight
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

                // Keep tooltip in bounds
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


def update_network_page():
    """Update cost-network.html with the interactive map."""
    repo_dir = Path(__file__).parent.parent
    network_page = repo_dir / "cost-network.html"

    if not network_page.exists():
        print(f"Error: {network_page} not found")
        return False

    content = network_page.read_text(encoding='utf-8')

    # Generate the map HTML
    map_html = generate_network_map_html()

    # Find insertion point (after the hero section, before the first section)
    # Look for the first <section after the breadcrumb
    insertion_marker = '<div class="breadcrumb">'

    if insertion_marker in content:
        # Find the end of the breadcrumb div line
        idx = content.find(insertion_marker)
        end_of_line = content.find('\n', idx)

        # Insert the map section after the breadcrumb
        new_content = content[:end_of_line + 1] + '\n' + map_html + '\n' + content[end_of_line + 1:]

        network_page.write_text(new_content, encoding='utf-8')
        print(f"Updated {network_page}")
        return True
    else:
        print("Could not find insertion point")
        return False


if __name__ == "__main__":
    update_network_page()
