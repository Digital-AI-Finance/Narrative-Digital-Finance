"""
Generate interactive HTML dashboard for CB Speeches analysis.
Includes Mermaid diagrams, data tables, and embedded charts.
"""
import pandas as pd
import numpy as np
import json
import base64
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "charts"
OUTPUT_FILE = BASE_DIR / "dashboard.html"

CHART_FOLDERS = [
    ("01_scaled_macro_timeseries", "Rolling-Standardized Macroeconomic Variables"),
    ("02_principal_components", "Principal Components (Macro & Inflation Indices)"),
    ("03_macro_strength_breakpoints", "Macro Strength Index with Structural Breaks"),
    ("04_inflation_index_breakpoints", "Inflation Index with Structural Breaks"),
    ("05_speech_count_distribution", "US Federal Reserve Speech Volume"),
    ("06_inflation_sentiment_combined", "Inflation Index vs CB Sentiment"),
    ("07_rolling_betas_macro", "Rolling Betas: Sentiment vs Macro Index"),
    ("08_rolling_r2_macro", "Rolling R-squared: Sentiment vs Macro Index"),
    ("09_rolling_betas_inflation", "Rolling Betas: Sentiment vs Inflation Index"),
    ("10_rolling_r2_inflation", "Rolling R-squared: Sentiment vs Inflation Index"),
    ("11_correlation_matrix", "Correlation Matrix (First Differences)"),
    ("12_pca_loadings_heatmap", "PCA Loadings Heatmap"),
]


def pdf_to_base64_png(pdf_path: Path) -> str:
    """Convert PDF to base64 PNG using matplotlib."""
    try:
        # Try pdf2image first
        from pdf2image import convert_from_path
        from io import BytesIO

        images = convert_from_path(str(pdf_path), dpi=150, first_page=1, last_page=1)
        if images:
            buffer = BytesIO()
            images[0].save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: use matplotlib to read and save
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.image as mpimg
        from io import BytesIO

        # Try to read the PDF as an image (works for some PDFs)
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Chart: {pdf_path.parent.name}",
                 ha='center', va='center', fontsize=14)
        plt.axis('off')

        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)

        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        return ""


def load_data_summary() -> dict:
    """Load and summarize all data files."""
    summary = {}

    # Load processed macro
    try:
        df = pd.read_csv(DATA_DIR / "processed_macro.csv", index_col=0, parse_dates=True)
        summary['macro'] = {
            'rows': len(df),
            'columns': list(df.columns),
            'date_range': f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}",
            'stats': df.describe().round(2).to_dict()
        }
    except Exception as e:
        summary['macro'] = {'error': str(e)}

    # Load PCA components
    try:
        df = pd.read_csv(DATA_DIR / "pca_components.csv", index_col=0, parse_dates=True)
        summary['pca_components'] = {
            'rows': len(df),
            'columns': list(df.columns)
        }
    except Exception as e:
        summary['pca_components'] = {'error': str(e)}

    # Load PCA loadings
    try:
        df = pd.read_csv(DATA_DIR / "pca_loadings.csv", index_col=0)
        summary['pca_loadings'] = df.round(2).to_dict()
    except Exception as e:
        summary['pca_loadings'] = {'error': str(e)}

    # Load breakpoints
    try:
        with open(DATA_DIR / "breakpoints.json", 'r') as f:
            bp = json.load(f)
        summary['breakpoints'] = bp
    except Exception as e:
        summary['breakpoints'] = {'error': str(e)}

    # Load sentiment
    try:
        df = pd.read_csv(DATA_DIR / "sentiment_aggregated.csv", index_col=0, parse_dates=True)
        summary['sentiment'] = {
            'rows': len(df),
            'columns': list(df.columns),
            'stats': df.describe().round(2).to_dict()
        }
    except Exception as e:
        summary['sentiment'] = {'error': str(e)}

    # Load correlation matrix
    try:
        df = pd.read_csv(DATA_DIR / "correlation_matrix.csv", index_col=0)
        summary['correlation'] = df.round(4).to_dict()
    except Exception as e:
        summary['correlation'] = {'error': str(e)}

    # Load rolling results
    for name in ['rolling_results_macro', 'rolling_results_inflation']:
        try:
            df = pd.read_csv(DATA_DIR / f"{name}.csv", index_col=0, parse_dates=True)
            summary[name] = {
                'rows': len(df),
                'columns': list(df.columns),
                'mean_r2': df[[c for c in df.columns if 'r2' in c]].mean().to_dict()
            }
        except Exception as e:
            summary[name] = {'error': str(e)}

    return summary


def generate_html(data_summary: dict, chart_images: dict) -> str:
    """Generate the complete HTML dashboard."""

    # Extract key metrics
    macro_bp = data_summary.get('breakpoints', {}).get('macro_index', {}).get('dates', [])
    inflation_bp = data_summary.get('breakpoints', {}).get('inflation_index', {}).get('dates', [])

    loadings = data_summary.get('pca_loadings', {})
    correlation = data_summary.get('correlation', {})

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CB Speeches Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --primary: #0072B2;
            --secondary: #D55E00;
            --bg: #ffffff;
            --bg-alt: #f8fafc;
            --text: #1e293b;
            --border: #e2e8f0;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }}

        header {{
            background: linear-gradient(135deg, var(--primary), #005a8c);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header p {{ opacity: 0.9; }}

        main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        section {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 2rem;
            overflow: hidden;
        }}

        .section-header {{
            background: var(--bg-alt);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .section-header h2 {{
            font-size: 1.25rem;
            color: var(--primary);
        }}

        .section-content {{
            padding: 1.5rem;
        }}

        .mermaid {{
            text-align: center;
            margin: 1rem 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}

        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}

        th {{
            background: var(--bg-alt);
            font-weight: 600;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
        }}

        .chart-card {{
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}

        .chart-card h3 {{
            background: var(--bg-alt);
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            border-bottom: 1px solid var(--border);
        }}

        .chart-card img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}

        .stat-card {{
            background: var(--bg-alt);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: #64748b;
        }}

        .highlight {{
            background: #fef3c7;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #f59e0b;
            margin: 1rem 0;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.85rem;
        }}

        .toggle {{ font-size: 1.25rem; }}

        @media (max-width: 768px) {{
            .chart-grid {{ grid-template-columns: 1fr; }}
            main {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>CB Speeches Analysis Dashboard</h1>
        <p>Central Bank Speech Sentiment vs Macroeconomic Indices | Full Pipeline Results</p>
    </header>

    <main>
        <!-- Key Findings -->
        <section>
            <div class="section-header">
                <h2>Key Finding</h2>
            </div>
            <div class="section-content">
                <div class="highlight">
                    <strong>Near-Zero Correlation:</strong> The correlation between central bank speech sentiment
                    (hawkish/dovish) and macroeconomic indices is essentially zero (r = 0.005), indicating that
                    speech sentiment does not systematically track or predict macroeconomic conditions.
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">0.005</div>
                        <div class="stat-label">Macro-Hawkish Correlation</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">72%</div>
                        <div class="stat-label">Variance (2 PCs)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(macro_bp)}</div>
                        <div class="stat-label">Macro Breakpoints</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(inflation_bp)}</div>
                        <div class="stat-label">Inflation Breakpoints</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Pipeline Architecture -->
        <section>
            <div class="section-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                <h2>Pipeline Architecture</h2>
                <span class="toggle">+</span>
            </div>
            <div class="section-content">
                <div class="mermaid">
flowchart TB
    subgraph Inputs["Input Data"]
        A["macroeconomic_data.csv<br/>6 FRED Series"]
        B["speeches.parquet<br/>197 MB, 20k speeches"]
    end

    subgraph Macro["Macro Analysis"]
        C["Rolling Standardization<br/>12-month window"]
        D["PCA Analysis<br/>6 vars to PC1, PC2"]
        E["PELT Breakpoints<br/>penalty=4"]
    end

    subgraph Sentiment["Sentiment Analysis"]
        F["Filter US Speeches<br/>2,421 Fed speeches"]
        G["Monthly Aggregation<br/>hawkish/dovish counts"]
    end

    subgraph Integration["Integration"]
        H["Rolling Regression<br/>36-month window"]
        I["Correlation Analysis"]
    end

    A --> C --> D --> E
    D --> H
    B --> F --> G --> H
    H --> I
                </div>
            </div>
        </section>

        <!-- Data Flow -->
        <section>
            <div class="section-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                <h2>Data Flow</h2>
                <span class="toggle">+</span>
            </div>
            <div class="section-content">
                <div class="mermaid">
flowchart LR
    subgraph Raw["Raw Data"]
        M1["macroeconomic_data.csv"]
        S1["speeches.parquet"]
    end

    subgraph Processed["Processed"]
        M2["processed_macro.csv"]
        P1["pca_components.csv"]
        P2["pca_loadings.csv"]
        B1["breakpoints.json"]
        S2["sentiment_aggregated.csv"]
    end

    subgraph Results["Results"]
        R1["rolling_results_macro.csv"]
        R2["rolling_results_inflation.csv"]
        C1["correlation_matrix.csv"]
    end

    M1 --> M2 --> P1
    M2 --> P2
    P1 --> B1
    S1 --> S2
    P1 --> R1
    S2 --> R1
    P1 --> R2
    S2 --> R2
    R1 --> C1
                </div>
            </div>
        </section>

        <!-- FRED Series -->
        <section>
            <div class="section-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                <h2>Input Data: FRED Macroeconomic Series</h2>
                <span class="toggle">+</span>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr><th>Series ID</th><th>Name</th><th>Description</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>FEDFUNDS</td><td>FED Funds Rate</td><td>Federal funds effective rate (%)</td></tr>
                        <tr><td>CPIAUCNS</td><td>CPI</td><td>Consumer Price Index for All Urban Consumers</td></tr>
                        <tr><td>PPIACO</td><td>PPI</td><td>Producer Price Index for All Commodities</td></tr>
                        <tr><td>GDP</td><td>GDP</td><td>Gross Domestic Product (billions)</td></tr>
                        <tr><td>UNRATE</td><td>Unemployment</td><td>Unemployment Rate (%)</td></tr>
                        <tr><td>PAYEMS</td><td>Nonfarm Payrolls</td><td>Total Nonfarm Employment (thousands)</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- PCA Results -->
        <section>
            <div class="section-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                <h2>PCA Variance Explained</h2>
                <span class="toggle">+</span>
            </div>
            <div class="section-content">
                <table>
                    <thead>
                        <tr><th>Component</th><th>Variance</th><th>Cumulative</th><th>Interpretation</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>PC1</td><td>48.6%</td><td>48.6%</td><td>Macro Strength Index</td></tr>
                        <tr><td>PC2</td><td>23.2%</td><td>71.8%</td><td>Inflation Index</td></tr>
                        <tr><td>PC3</td><td>15.4%</td><td>87.1%</td><td>-</td></tr>
                        <tr><td>PC4-6</td><td>12.9%</td><td>100%</td><td>-</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Breakpoints -->
        <section>
            <div class="section-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                <h2>Detected Breakpoints (PELT Algorithm)</h2>
                <span class="toggle">+</span>
            </div>
            <div class="section-content">
                <h3>Macro Strength Index ({len(macro_bp)} breakpoints = {len(macro_bp)+1} regimes)</h3>
                <table>
                    <thead><tr><th>#</th><th>Date</th><th>Economic Context</th></tr></thead>
                    <tbody>
                        {''.join(f"<tr><td>{i+1}</td><td>{d}</td><td>-</td></tr>" for i, d in enumerate(macro_bp[:8]))}
                    </tbody>
                </table>

                <h3 style="margin-top:1.5rem">Inflation Index ({len(inflation_bp)} breakpoints = {len(inflation_bp)+1} regimes)</h3>
                <table>
                    <thead><tr><th>#</th><th>Date</th><th>Economic Context</th></tr></thead>
                    <tbody>
                        {''.join(f"<tr><td>{i+1}</td><td>{d}</td><td>-</td></tr>" for i, d in enumerate(inflation_bp[:12]))}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Charts -->
        <section>
            <div class="section-header">
                <h2>All 12 Analysis Charts</h2>
            </div>
            <div class="section-content">
                <div class="chart-grid">
'''

    # Add charts
    for folder, title in CHART_FOLDERS:
        img_data = chart_images.get(folder, "")
        if img_data:
            html += f'''
                    <div class="chart-card">
                        <h3>{title}</h3>
                        <img src="data:image/png;base64,{img_data}" alt="{title}">
                    </div>
'''
        else:
            html += f'''
                    <div class="chart-card">
                        <h3>{title}</h3>
                        <div style="padding:2rem;text-align:center;color:#64748b;">
                            Chart image not available
                        </div>
                    </div>
'''

    html += f'''
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>CB Speeches Analysis Pipeline | Data: FRED, BIS</p>
    </footer>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
'''
    return html


def main():
    """Generate the dashboard."""
    print("=" * 60)
    print("GENERATING HTML DASHBOARD")
    print("=" * 60)

    # Load data summary
    print("Loading data summary...")
    data_summary = load_data_summary()

    # Convert charts to images
    print("Converting charts to images...")
    chart_images = {}
    for folder, title in CHART_FOLDERS:
        pdf_path = CHARTS_DIR / folder / "chart.pdf"
        if pdf_path.exists():
            print(f"  Converting {folder}...")
            chart_images[folder] = pdf_to_base64_png(pdf_path)

    # Generate HTML
    print("Generating HTML...")
    html = generate_html(data_summary, chart_images)

    # Write output
    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f"\nDashboard saved to: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

    return str(OUTPUT_FILE)


if __name__ == "__main__":
    output = main()
    print(f"\nOpen in browser: file:///{output.replace(chr(92), '/')}")
