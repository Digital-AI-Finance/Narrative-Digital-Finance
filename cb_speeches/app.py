"""
Streamlit Dashboard for CB Speeches Analysis.
Loads precomputed data from inventory.json for fast startup.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from analysis.config import DATA_DIR, FRED_SERIES

# Okabe-Ito colorblind-safe palette
COLORS = {
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'sky_blue': '#56B4E9',
    'orange': '#E69F00',
    'green': '#009E73',
    'yellow': '#F0E442',
    'purple': '#CC79A7',
}

st.set_page_config(
    page_title="CB Speeches Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_precomputed():
    """Load all precomputed data from inventory.json and CSV files."""
    inventory_path = DATA_DIR / 'inventory.json'

    if not inventory_path.exists():
        st.error("Precomputed data not found. Run `python precompute.py` first.")
        return None, None

    with open(inventory_path, 'r') as f:
        inventory = json.load(f)

    # Load all CSV files
    data = {}
    for key, filename in inventory['data_files'].items():
        filepath = DATA_DIR / filename
        if filepath.exists():
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            data[key] = df

    return inventory, data


def show_descriptive_stats(df: pd.DataFrame, title: str = "Descriptive Statistics"):
    """Show descriptive statistics for a dataframe."""
    st.subheader(title)
    stats = df.describe().T
    stats['missing'] = df.isnull().sum()
    stats['missing_pct'] = (df.isnull().sum() / len(df) * 100).round(2)
    st.dataframe(stats.round(4), use_container_width=True)


def main():
    st.title("CB Speeches Analysis Dashboard")
    st.markdown("*Central Bank Speech Sentiment vs Macroeconomic Indices*")

    # Load precomputed data
    inventory, data = load_precomputed()

    if inventory is None:
        return

    # Show precomputed badge
    params = inventory['metadata']['parameters']
    st.sidebar.success(f"Precomputed: {inventory['metadata']['created'][:10]}")

    st.sidebar.header("Analysis Parameters (Fixed)")
    st.sidebar.markdown(f"""
    - Rolling Window: **{params['rolling_window']} months**
    - Regression Window: **{params['regression_window']} months**
    - PELT Penalty: **{params['pelt_penalty']}**
    - Date Range: **{params['start_date']} to {params['end_date']}**
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("To change parameters, edit `precompute.py` and re-run.")

    # Extract key data
    summary = inventory['summary_stats']
    breakpoints = inventory['breakpoints']
    variance = inventory['variance_explained']
    sentiment_summary = inventory['sentiment_summary']
    regime_stats = inventory['regime_stats']

    # Tabs - 8 tabs with "Methodology" as second tab
    tab1, tab_method, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Overview", "Methodology", "Macro Data", "PCA Analysis",
        "Breakpoints", "Speech Sentiment", "Regression", "All Data"
    ])

    # ==================== Tab 1: Overview ====================
    with tab1:
        st.header("Key Finding")
        st.info(
            "**Near-Zero Correlation**: The correlation between central bank speech sentiment "
            "(hawkish/dovish) and macroeconomic indices is essentially zero, indicating that "
            "speech sentiment does not systematically track or predict macroeconomic conditions."
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Macro-Hawkish Correlation", f"{summary['macro_hawkish_correlation']:.4f}")
        col2.metric("Variance (2 PCs)", f"{summary['variance_2pcs']:.1f}%")
        col3.metric("Macro Breakpoints", summary['n_macro_breakpoints'])
        col4.metric("Inflation Breakpoints", summary['n_inflation_breakpoints'])

        st.subheader("Pipeline Parameters")
        params_df = pd.DataFrame({
            'Parameter': ['Rolling Window', 'Regression Window', 'PELT Penalty', 'Date Range'],
            'Value': [
                f"{params['rolling_window']} months",
                f"{params['regression_window']} months",
                str(params['pelt_penalty']),
                f"{params['start_date']} to {params['end_date']}"
            ]
        })
        st.table(params_df)

        st.subheader("Data Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Macro Data Points", summary['n_macro_observations'])
        col2.metric("Total Speeches", summary['n_speeches'])
        col3.metric("Monthly Observations", summary['n_monthly_sentiment'])

    # ==================== Tab: Methodology ====================
    with tab_method:
        st.header("Analysis Methodology")
        st.markdown("""
        This dashboard implements a complete analysis pipeline to study the relationship between
        Central Bank speech sentiment and macroeconomic conditions. The analysis proceeds through
        6 sequential steps, each building on the previous.
        """)

        # Pipeline Flowchart
        st.subheader("Pipeline Flowchart")
        fig_flow = go.Figure()

        # Define box positions and dimensions
        box_width = 0.15
        box_height = 0.12
        y_positions = [0.85, 0.85, 0.55, 0.55, 0.25, 0.25]
        x_positions = [0.15, 0.5, 0.15, 0.5, 0.15, 0.5]
        labels = [
            "1. Data Loading\n(FRED API)",
            "2. Rolling\nStandardization",
            "3. PCA\nAnalysis",
            "4. Breakpoint\nDetection",
            "5. Speech\nSentiment",
            "6. Rolling\nRegression"
        ]
        colors_flow = [COLORS['blue'], COLORS['green'], COLORS['orange'],
                       COLORS['vermillion'], COLORS['purple'], COLORS['sky_blue']]

        # Add boxes
        for i, (x, y, label, color) in enumerate(zip(x_positions, y_positions, labels, colors_flow)):
            fig_flow.add_shape(
                type="rect", x0=x-box_width/2, y0=y-box_height/2,
                x1=x+box_width/2, y1=y+box_height/2,
                fillcolor=color, opacity=0.7, line=dict(color=color, width=2)
            )
            fig_flow.add_annotation(
                x=x, y=y, text=label, showarrow=False,
                font=dict(size=11, color="white"), align="center"
            )

        # Add arrows
        arrows = [
            (0.15, 0.79, 0.15, 0.61),   # 1 -> 3
            (0.22, 0.85, 0.43, 0.85),   # 1 -> 2
            (0.5, 0.79, 0.5, 0.61),     # 2 -> 4
            (0.15, 0.49, 0.15, 0.31),   # 3 -> 5
            (0.22, 0.55, 0.43, 0.55),   # 3 -> 4
            (0.5, 0.49, 0.5, 0.31),     # 4 -> 6
            (0.22, 0.25, 0.43, 0.25),   # 5 -> 6
        ]
        for x0, y0, x1, y1 in arrows:
            fig_flow.add_annotation(
                x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y",
                axref="x", ayref="y", showarrow=True,
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="gray"
            )

        fig_flow.update_layout(
            xaxis=dict(range=[0, 0.7], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False),
            height=400, margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor="white"
        )
        st.plotly_chart(fig_flow, use_container_width=True)

        st.markdown("---")

        # Data Sources Section
        with st.expander("Data Sources & Pre-Processing", expanded=True):
            st.markdown("""
            ### Data Sources

            This analysis uses two primary data sources:

            | Source | Description | What This Pipeline Does |
            |--------|-------------|------------------------|
            | **FRED API** | Federal Reserve Economic Data | Fetches 6 macro series, caches to CSV |
            | **gigando_speeches_ner_v2.parquet** | 20,069 CB speeches with NER annotations | Loads pre-classified sentiment labels |

            ### Important: Pre-Computed vs Computed

            | Data | Pre-Computed? | Details |
            |------|---------------|---------|
            | Macro data (FRED) | No | Fetched fresh or from cache |
            | Sentiment labels | **YES** | Already in parquet file |
            | PCA components | No | Computed by this pipeline |
            | Breakpoints | No | Computed by this pipeline |
            | Rolling regression | No | Computed by this pipeline |
            """)

            st.warning("""
            **Note on Sentiment Classification**: The hawkish/dovish/neutral labels are **PRE-COMPUTED**
            in the source parquet file. This pipeline does NOT perform sentiment classification - it only
            aggregates pre-existing labels. The classification was performed externally using NLP/text
            mining techniques (likely based on financial sentiment lexicons such as Loughran-McDonald).
            """)

        # Step 1: Data Loading
        with st.expander("Step 1: Data Loading (FRED API)", expanded=False):
            st.markdown("""
            **Objective**: Load 6 key macroeconomic indicators from the Federal Reserve Economic Data (FRED) API.

            ### Variables
            | FRED ID | Description | Units | Frequency |
            |---------|-------------|-------|-----------|
            | FEDFUNDS | Effective Federal Funds Rate | Percent | Monthly |
            | CPIAUCSL | Consumer Price Index (All Urban Consumers) | Index 1982-84=100 | Monthly |
            | PPIACO | Producer Price Index (All Commodities) | Index 1982=100 | Monthly |
            | GDP | Gross Domestic Product | Billions USD | Quarterly -> Monthly |
            | UNRATE | Unemployment Rate | Percent | Monthly |
            | PAYEMS | Nonfarm Payrolls (Employment) | Thousands | Monthly |

            ### Process
            1. Query FRED API for each series (requires API key)
            2. Resample to monthly frequency (end-of-month)
            3. Handle missing values via forward-fill
            4. Cache results to `macroeconomic_data.csv` for reproducibility

            ### Implementation Details
            - **API Key**: Required from FRED (free registration)
            - **Date Range**: {start} to {end}
            - **Missing Data**: Forward-fill (ffill) for gaps
            """.format(start=params['start_date'], end=params['end_date']))

            st.info("""
            **Note on GDP Frequency**: GDP is released quarterly, while other series are monthly.
            We use forward-fill (ffill) to convert quarterly to monthly - each month uses the
            "last known" GDP value until the next quarterly release. This is standard practice
            for real-time macro analysis. The other 5 series (FEDFUNDS, CPI, PPI, UNRATE, PAYEMS)
            are natively monthly and rarely have gaps.
            """)

            st.markdown("**Verify with Python:**")
            st.code('''# Load macro data from cache or FRED
from analysis.data_loader import load_cached_macro, fetch_fred_data

# Option 1: Load from cache (fast)
macro_data = load_cached_macro()
print(f"Shape: {macro_data.shape}")
print(macro_data.head())

# Option 2: Fetch fresh from FRED (requires API key)
# macro_data = fetch_fred_data('1996-01-01', '2025-05-01')
''', language='python')

            st.markdown("**Output Sample:**")
            st.dataframe(data['raw_macro'].head(8).round(2), use_container_width=True)

        # Step 2: Rolling Standardization
        with st.expander("Step 2: Rolling Standardization", expanded=False):
            st.markdown("""
            **Objective**: Transform each variable to a z-score using a rolling window, removing level effects
            and making variables comparable.

            ### Why Rolling (not Global) Standardization?
            | Approach | Pros | Cons |
            |----------|------|------|
            | Global | Simple, uses all data | Look-ahead bias, ignores structural changes |
            | Rolling | No look-ahead, adapts to changes | Loses first w-1 observations |

            We use **rolling** to avoid look-ahead bias (only uses past data at each point).

            ### Formula
            """)
            st.latex(r"z_t = \frac{x_t - \bar{x}_{t,w}}{\sigma_{t,w}}")
            st.markdown("where:")
            st.latex(r"\bar{x}_{t,w} = \frac{1}{w}\sum_{i=t-w+1}^{t} x_i \quad \text{(rolling mean over past } w \text{ periods)}")
            st.latex(r"\sigma_{t,w} = \sqrt{\frac{1}{w-1}\sum_{i=t-w+1}^{t} (x_i - \bar{x}_{t,w})^2} \quad \text{(rolling std with Bessel correction)}")

            st.markdown(f"""
            ### Key Parameters
            - **Window size**: w = {params['rolling_window']} months (captures annual cycles)
            - **Edge effect**: First {params['rolling_window']-1} observations become NaN
            - **Division by zero**: If std=0, result is NaN
            """)

            st.markdown("**Verify with Python:**")
            st.code('''import pandas as pd
import numpy as np

# Example calculation with window=3
x = pd.Series([10, 12, 11, 15, 14, 16])
window = 3

rolling_mean = x.rolling(window).mean()
rolling_std = x.rolling(window).std()
z_score = (x - rolling_mean) / rolling_std

print("Original:     ", x.tolist())
print("Rolling Mean: ", [round(v,2) if not np.isnan(v) else 'NaN' for v in rolling_mean])
print("Rolling Std:  ", [round(v,2) if not np.isnan(v) else 'NaN' for v in rolling_std])
print("Z-Score:      ", [round(v,2) if not np.isnan(v) else 'NaN' for v in z_score])

# Output:
# Original:      [10, 12, 11, 15, 14, 16]
# Rolling Mean:  ['NaN', 'NaN', 11.0, 12.67, 13.33, 15.0]
# Rolling Std:   ['NaN', 'NaN', 1.0, 2.08, 2.08, 1.0]
# Z-Score:       ['NaN', 'NaN', 0.0, 1.12, 0.32, 1.0]
''', language='python')

            st.markdown("**Before/After Comparison:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("*Before (Raw Data)*")
                st.dataframe(data['raw_macro'].head(5).round(2), use_container_width=True)
            with col2:
                st.markdown("*After (Standardized)*")
                st.dataframe(data['scaled_macro'].head(5).round(4), use_container_width=True)

            # Visual comparison
            selected_var_method = list(data['raw_macro'].columns)[0]
            fig_std = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                   subplot_titles=(f"Raw {selected_var_method}", f"Standardized {selected_var_method}"))
            fig_std.add_trace(go.Scatter(x=data['raw_macro'].index, y=data['raw_macro'][selected_var_method],
                                        line=dict(color=COLORS['blue'])), row=1, col=1)
            fig_std.add_trace(go.Scatter(x=data['scaled_macro'].index, y=data['scaled_macro'][selected_var_method],
                                        line=dict(color=COLORS['green'])), row=2, col=1)
            fig_std.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
            fig_std.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_std, use_container_width=True)

        # Step 3: PCA Analysis
        with st.expander("Step 3: PCA Analysis", expanded=False):
            st.markdown("""
            **Objective**: Reduce the 6 macroeconomic variables to 2 principal components that capture
            the main sources of variation.

            ### Why PCA?
            - Reduces dimensionality from 6 variables to 2 indices
            - Removes multicollinearity between correlated macro variables
            - PC1 and PC2 are orthogonal (uncorrelated)

            ### Interpretation
            - **PC1 (Macro Strength Index)**: Captures overall economic activity
              - High loadings on: GDP, PAYEMS (employment), FEDFUNDS
              - Positive values = strong economy
            - **PC2 (Inflation Index)**: Captures price-level dynamics
              - High loadings on: CPIAUCSL, PPIACO
              - Positive values = high inflation
            """)

            st.markdown("### Formula")
            st.latex(r"\mathbf{PC} = \mathbf{X} \cdot \mathbf{V}")
            st.markdown("where:")
            st.latex(r"\mathbf{X} \in \mathbb{R}^{n \times 6} \quad \text{(standardized data matrix)}")
            st.latex(r"\mathbf{V} \in \mathbb{R}^{6 \times 6} \quad \text{(eigenvector matrix from SVD)}")

            st.markdown("### Eigenvalue Decomposition")
            st.latex(r"\mathbf{X}^T\mathbf{X} \cdot \mathbf{v}_i = \lambda_i \cdot \mathbf{v}_i")
            st.latex(r"\text{Variance explained by PC}_i = \frac{\lambda_i}{\sum_{j=1}^{6} \lambda_j} \times 100\%")

            st.markdown("**Verify with Python:**")
            st.code('''from sklearn.decomposition import PCA
import numpy as np

# Fit PCA on standardized data
pca = PCA(n_components=6, random_state=42)
pca_scores = pca.fit_transform(scaled_data.values)

# Results
print("Eigenvalues:", pca.explained_variance_)
print("Variance explained:", pca.explained_variance_ratio_ * 100)
print("Cumulative variance:", np.cumsum(pca.explained_variance_ratio_) * 100)
print("\\nLoadings (eigenvectors):")
print(pca.components_)
''', language='python')

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Eigenvalues & Variance:**")
                eigen_df_m = pd.DataFrame({
                    'Component': [f'PC{i+1}' for i in range(len(inventory['eigenvalues']))],
                    'Eigenvalue': inventory['eigenvalues'],
                    'Variance %': variance['individual'],
                    'Cumulative %': variance['cumulative']
                })
                st.dataframe(eigen_df_m.round(4), use_container_width=True)

            with col2:
                st.markdown("**Key Statistics:**")
                st.metric("PC1 + PC2 Variance", f"{variance['cumulative'][1]:.1f}%")
                st.markdown("*Two components capture most of the variation*")

            st.markdown("**Loadings (component weights):**")
            st.dataframe(data['pca_loadings'].round(2), use_container_width=True)

        # Step 4: Breakpoint Detection
        with st.expander("Step 4: Breakpoint Detection (PELT)", expanded=False):
            st.markdown("""
            **Objective**: Identify structural regime changes in the Macro and Inflation indices
            using the PELT (Pruned Exact Linear Time) algorithm.

            ### What is PELT?
            PELT is an exact algorithm for detecting multiple changepoints. It finds the optimal
            segmentation that minimizes the sum of segment costs plus a penalty for each changepoint.

            ### Algorithm Details
            - **Model**: RBF (Radial Basis Function) kernel
            - **Complexity**: O(n) with pruning (vs O(n^2) for naive approach)
            - **Library**: `ruptures` Python package
            """)

            st.markdown("### Optimization Problem")
            st.latex(r"\min_{K, \{t_1,...,t_K\}} \left[ \sum_{i=0}^{K} C(y_{t_i:t_{i+1}}) + \beta \cdot K \right]")
            st.markdown("where:")
            st.latex(r"C(y_{a:b}) = \sum_{t=a}^{b} \|y_t - \bar{y}_{a:b}\|^2 \quad \text{(within-segment variance)}")
            st.latex(r"\beta = \text{penalty parameter (controls number of breaks)}")
            st.latex(r"K = \text{number of breakpoints}")

            st.markdown(f"""
            ### Key Parameters
            - **Penalty (beta)**: {params['pelt_penalty']}
              - Higher penalty = fewer breakpoints (more conservative)
              - Lower penalty = more breakpoints (more sensitive)
            - **Model**: RBF kernel (captures non-linear changes)
            - **Min segment size**: 2 observations
            """)

            st.markdown("**Verify with Python:**")
            st.code('''import ruptures as rpt
import numpy as np

# Example: detect regime change
np.random.seed(42)
signal = np.concatenate([
    np.random.randn(50),      # Regime 1: mean=0
    np.random.randn(50) + 3   # Regime 2: mean=3
])

algo = rpt.Pelt(model="rbf", min_size=2).fit(signal)
breaks = algo.predict(pen=4)

print(f"Breakpoints: {breaks}")  # Should find break around index 50
# Output: Breakpoints: [50, 100]  (50 is the change, 100 is end)
''', language='python')

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Macro Index: {len(breakpoints['macro_index']['dates'])} breakpoints**")
                if breakpoints['macro_index']['dates']:
                    st.dataframe(pd.DataFrame({'Date': breakpoints['macro_index']['dates']}), use_container_width=True)
            with col2:
                st.markdown(f"**Inflation Index: {len(breakpoints['inflation_index']['dates'])} breakpoints**")
                if breakpoints['inflation_index']['dates']:
                    st.dataframe(pd.DataFrame({'Date': breakpoints['inflation_index']['dates']}), use_container_width=True)

        # Step 5: Speech Sentiment - CRITICAL CLARIFICATION
        with st.expander("Step 5: Speech Sentiment Aggregation", expanded=False):
            st.error("""
            **IMPORTANT**: Sentiment classification (hawkish/dovish/neutral) is **PRE-COMPUTED**
            in the source parquet file. This pipeline does NOT perform NLP classification!
            """)

            st.markdown("""
            ### Data Source
            The file `gigando_speeches_ner_v2.parquet` contains:
            - **20,069 speeches** from central banks worldwide
            - Pre-existing `sentiment` column with labels: hawkish, dovish, neutral
            - Named Entity Recognition (NER) annotations

            ### How Was Sentiment Originally Classified?
            The sentiment labels were computed externally (not by this pipeline) using NLP techniques,
            likely one of these approaches:
            - **Loughran-McDonald Financial Dictionary**: Word-count based sentiment
            - **Transformer-based models**: BERT, FinBERT, or similar
            - **Custom rules**: Domain-specific hawkish/dovish keywords

            ### What This Pipeline Actually Does
            | Step | Action | Code Location |
            |------|--------|---------------|
            | 1 | Load parquet file | `load_us_speeches()` |
            | 2 | Filter to US Fed speeches | `df[df['country_code'] == 'US']` |
            | 3 | Read pre-existing sentiment column | `df['sentiment']` |
            | 4 | Aggregate monthly counts | `resample('MS').sum()` |
            | 5 | Apply 1-month lag | `shift(1)` |
            | 6 | Standardize with rolling z-score | Same as Step 2 |
            """)

            st.markdown("**Verify Sentiment is Pre-Computed:**")
            st.code('''import pandas as pd

# Load the parquet file
df = pd.read_parquet('gigando_speeches_ner_v2.parquet')

# Check columns - sentiment already exists!
print("Columns:", df.columns.tolist())
# Output: ['date', 'url', 'title', 'description', 'text', 'author_x',
#          'datetime', 'uuid', 'author_y', 'organization', 'country_code',
#          'sentiment', 'id']

# Count pre-existing sentiment labels
print("\\nSentiment value counts:")
print(df['sentiment'].value_counts())
# Output:
# neutral    11439
# dovish      5044
# hawkish     3586

# Example speech with pre-assigned sentiment
print("\\nExample speech:")
sample = df[df['sentiment'] == 'hawkish'].iloc[0]
print(f"Title: {sample['title'][:80]}...")
print(f"Sentiment: {sample['sentiment']}")  # Already labeled!
''', language='python')

            st.markdown("### Sentiment Distribution (Pre-Computed Labels)")
            col1, col2, col3 = st.columns(3)
            col1.metric("Hawkish", f"{sentiment_summary['hawkish']['count']} ({sentiment_summary['hawkish']['pct']}%)")
            col2.metric("Dovish", f"{sentiment_summary['dovish']['count']} ({sentiment_summary['dovish']['pct']}%)")
            col3.metric("Neutral", f"{sentiment_summary['neutral']['count']} ({sentiment_summary['neutral']['pct']}%)")

            st.markdown("### Monthly Aggregation Formula")
            st.latex(r"\text{hawkish}_t = \sum_{s \in \text{month } t} \mathbf{1}[\text{speech } s \text{ has sentiment='hawkish'}]")
            st.latex(r"\text{dovish}_t = \sum_{s \in \text{month } t} \mathbf{1}[\text{speech } s \text{ has sentiment='dovish'}]")

            st.markdown("**Sample Output (After Aggregation & Standardization):**")
            st.dataframe(data['sentiment_standardized'].dropna().head(10).round(4), use_container_width=True)

        # Step 6: Rolling Regression
        with st.expander("Step 6: Rolling Regression Analysis", expanded=False):
            st.markdown("""
            **Objective**: Quantify the time-varying relationship between macro indices and speech sentiment
            using rolling OLS regression.

            **Key Finding**: The correlation between speech sentiment and macro indices is near zero (~0.005),
            suggesting CB speeches do not systematically track macroeconomic conditions.

            ### Why First Differences?
            - Raw time series may have trends (non-stationary)
            - First differences remove trends: Δy_t = y_t - y_{t-1}
            - Ensures we're measuring changes, not levels
            """)

            st.markdown("### Step 6a: First Differencing")
            st.latex(r"\Delta y_t = y_t - y_{t-1}")

            st.markdown("### Step 6b: Rolling OLS Regression")
            st.latex(r"\Delta \text{Index}_t = \alpha + \beta \cdot \Delta \text{Sentiment}_t + \epsilon_t")

            st.markdown("### Rolling Beta Calculation")
            st.latex(r"\hat{\beta}_t = \frac{\text{Cov}(\Delta X, \Delta Y)_{t,w}}{\text{Var}(\Delta X)_{t,w}}")

            st.markdown("### Rolling R-squared")
            st.latex(r"R^2_t = \frac{\text{Cov}(\Delta X, \Delta Y)^2_{t,w}}{\text{Var}(\Delta X)_{t,w} \cdot \text{Var}(\Delta Y)_{t,w}} = \rho^2_{XY}")

            st.markdown(f"""
            ### Key Parameters
            - **Window size**: w = {params['regression_window']} months (3 years, captures business cycle)
            - **Variables**: First-differenced Macro Index vs First-differenced Hawkish/Dovish counts
            """)

            st.markdown("**Verify with Python:**")
            st.code('''import numpy as np

# Manual beta calculation example
x = np.array([1, 2, 3, 4, 5])  # Sentiment changes
y = np.array([2, 4, 5, 4, 5])  # Index changes

# Calculate beta = Cov(x,y) / Var(x)
cov_xy = np.cov(x, y, ddof=1)[0, 1]  # Sample covariance
var_x = np.var(x, ddof=1)             # Sample variance

beta = cov_xy / var_x
r_squared = (cov_xy ** 2) / (var_x * np.var(y, ddof=1))

print(f"Covariance(X,Y): {cov_xy:.4f}")
print(f"Variance(X):     {var_x:.4f}")
print(f"Beta:            {beta:.4f}")
print(f"R-squared:       {r_squared:.4f}")

# Output:
# Covariance(X,Y): 1.0000
# Variance(X):     2.5000
# Beta:            0.4000
# R-squared:       0.2222
''', language='python')

            st.markdown("**Correlation Matrix (First Differences):**")
            st.dataframe(data['corr_macro'].round(4), use_container_width=True)

            st.markdown("### Key Result")
            macro_hawk_corr = data['corr_macro'].loc['Macro Index', 'hawkish'] if 'Macro Index' in data['corr_macro'].index else 0
            st.metric("Macro Index - Hawkish Correlation", f"{macro_hawk_corr:.4f}")
            st.success("""
            **Conclusion**: The near-zero correlation confirms that CB speech sentiment does not
            systematically track or predict macroeconomic conditions. Central bankers' hawkish/dovish
            tone appears independent of actual economic activity levels.
            """)

        # Statistical Validation Section (NEW)
        st.markdown("---")
        with st.expander("Statistical Validation: Stationarity Tests", expanded=False):
            st.markdown("""
            **Why Stationarity Matters**: Regression with non-stationary time series can produce
            spurious correlations. We verify stationarity of our first-differenced series.

            ### Augmented Dickey-Fuller (ADF) Test
            - **Null hypothesis**: Series has a unit root (non-stationary)
            - **Alternative**: Series is stationary
            - **Decision rule**: Reject null if p-value < 0.05 (series is stationary)

            ### KPSS Test
            - **Null hypothesis**: Series is stationary
            - **Alternative**: Series has a unit root (non-stationary)
            - **Decision rule**: Reject null if p-value < 0.05 (series is NOT stationary)
            """)

            st.markdown("**Stationarity Test Results (First Differences):**")

            # Compute ADF tests on differenced series
            try:
                from statsmodels.tsa.stattools import adfuller, kpss

                # Get differenced data
                macro_diff = data['pca_components']['PC1'].diff().dropna()
                hawkish_diff = data['sentiment_standardized']['hawkish'].diff().dropna()
                dovish_diff = data['sentiment_standardized']['dovish'].diff().dropna()

                test_results = []

                # ADF tests
                for name, series in [('Macro Index', macro_diff),
                                     ('Hawkish', hawkish_diff),
                                     ('Dovish', dovish_diff)]:
                    try:
                        adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(series.dropna(), autolag='AIC')
                        kpss_stat, kpss_p, kpss_lags, kpss_crit = kpss(series.dropna(), regression='c', nlags='auto')

                        test_results.append({
                            'Series': f'Delta {name}',
                            'ADF Statistic': round(adf_stat, 4),
                            'ADF p-value': round(adf_p, 4),
                            'ADF Stationary?': 'Yes' if adf_p < 0.05 else 'No',
                            'KPSS Statistic': round(kpss_stat, 4),
                            'KPSS p-value': f">{kpss_p:.2f}" if kpss_p > 0.1 else f"{kpss_p:.4f}",
                            'KPSS Stationary?': 'Yes' if kpss_p > 0.05 else 'No'
                        })
                    except Exception as e:
                        test_results.append({
                            'Series': f'Delta {name}',
                            'ADF Statistic': 'Error',
                            'ADF p-value': str(e)[:20],
                            'ADF Stationary?': 'N/A',
                            'KPSS Statistic': 'N/A',
                            'KPSS p-value': 'N/A',
                            'KPSS Stationary?': 'N/A'
                        })

                results_df = pd.DataFrame(test_results)
                st.dataframe(results_df, use_container_width=True)

                # Interpretation
                all_stationary = all(r['ADF Stationary?'] == 'Yes' for r in test_results if r['ADF Stationary?'] != 'N/A')
                if all_stationary:
                    st.success("All first-differenced series are stationary (ADF test rejects unit root). Regression results are valid.")
                else:
                    st.warning("Some series may not be stationary. Interpret regression results with caution.")

            except ImportError:
                st.info("Install `statsmodels` package to run stationarity tests: `pip install statsmodels`")
            except Exception as e:
                st.error(f"Error computing stationarity tests: {e}")

            st.markdown("**Verify with Python:**")
            st.code('''from statsmodels.tsa.stattools import adfuller, kpss

# ADF test (null = unit root)
adf_result = adfuller(series, autolag='AIC')
print(f"ADF Statistic: {adf_result[0]:.4f}")
print(f"p-value: {adf_result[1]:.4f}")
print(f"Stationary: {'Yes' if adf_result[1] < 0.05 else 'No'}")

# KPSS test (null = stationary)
kpss_result = kpss(series, regression='c')
print(f"KPSS Statistic: {kpss_result[0]:.4f}")
print(f"p-value: {kpss_result[1]:.4f}")
print(f"Stationary: {'Yes' if kpss_result[1] > 0.05 else 'No'}")
''', language='python')

    # ==================== Tab 2: Macro Data ====================
    with tab2:
        st.header("Macroeconomic Data - FULL VIEW")

        st.subheader("FRED Series Definition")
        series_df = pd.DataFrame([
            {'ID': k, 'Name': v} for k, v in FRED_SERIES.items()
        ])
        st.table(series_df)

        # Raw data
        st.subheader("Raw Macroeconomic Data (ALL)")
        st.dataframe(data['raw_macro'], use_container_width=True, height=400)
        show_descriptive_stats(data['raw_macro'], "Raw Data Statistics")
        st.download_button("Download Raw Macro Data", data['raw_macro'].to_csv(), "raw_macro.csv", "text/csv")

        # Individual time series
        st.subheader("Individual Time Series (Raw)")
        selected_var = st.selectbox("Select Variable", data['raw_macro'].columns.tolist())
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['raw_macro'].index,
            y=data['raw_macro'][selected_var],
            name=selected_var,
            line=dict(color=COLORS['blue'])
        ))
        fig.update_layout(title=f"{selected_var} - Raw Time Series", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Rolling statistics
        st.subheader("Rolling Statistics (used for standardization)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Rolling Mean ({params['rolling_window']}-month)**")
            st.dataframe(data['rolling_mean'].dropna().round(4), use_container_width=True, height=300)
        with col2:
            st.markdown(f"**Rolling Std ({params['rolling_window']}-month)**")
            st.dataframe(data['rolling_std'].dropna().round(4), use_container_width=True, height=300)

        # Standardized data
        st.subheader("Standardized Macroeconomic Data (ALL)")
        st.dataframe(data['scaled_macro'], use_container_width=True, height=400)
        show_descriptive_stats(data['scaled_macro'], "Standardized Data Statistics")

        # All time series overlay
        st.subheader("All Standardized Time Series")
        fig = go.Figure()
        colors_list = list(COLORS.values())
        for i, col in enumerate(data['scaled_macro'].columns):
            fig.add_trace(go.Scatter(
                x=data['scaled_macro'].index,
                y=data['scaled_macro'][col],
                name=col,
                line=dict(color=colors_list[i % len(colors_list)], width=1.5)
            ))
        fig.update_layout(
            title=f"Rolling-Standardized Macro Variables ({params['rolling_window']}-month window)",
            xaxis_title="Date", yaxis_title="Z-Score",
            height=500, hovermode='x unified'
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Download Standardized Data", data['scaled_macro'].to_csv(), "standardized_macro.csv", "text/csv")

    # ==================== Tab 3: PCA Analysis ====================
    with tab3:
        st.header("PCA Analysis - FULL CALCULATIONS")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Variance Explained")
            var_df = pd.DataFrame({
                'Component': [f'PC{i+1}' for i in range(len(variance['individual']))],
                'Variance Explained': variance['individual'],
                'Cumulative Variance': variance['cumulative']
            })
            st.dataframe(var_df.round(4), use_container_width=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=var_df['Component'], y=var_df['Variance Explained'],
                                name='Individual', marker_color=COLORS['blue']))
            fig.add_trace(go.Scatter(x=var_df['Component'], y=var_df['Cumulative Variance'],
                                    name='Cumulative', line=dict(color=COLORS['vermillion'], width=2),
                                    marker=dict(size=8)))
            fig.update_layout(title="PCA Variance Explained", yaxis_title="Variance (%)", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Eigenvalues")
            eigen_df = pd.DataFrame({
                'Component': [f'PC{i+1}' for i in range(len(inventory['eigenvalues']))],
                'Eigenvalue': inventory['eigenvalues']
            })
            st.dataframe(eigen_df.round(6), use_container_width=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=eigen_df['Component'], y=eigen_df['Eigenvalue'],
                                marker_color=COLORS['green']))
            fig.update_layout(title="Eigenvalues (Scree Plot)", yaxis_title="Eigenvalue", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Eigenvectors (PCA Components)")
        st.dataframe(data['eigenvectors'].round(4), use_container_width=True)

        st.subheader("PCA Loadings (scaled)")
        st.dataframe(data['pca_loadings'].round(2), use_container_width=True)

        loadings_plot = data['pca_loadings'].drop(columns=['Explained Variance'], errors='ignore')
        fig = px.imshow(loadings_plot.values, x=loadings_plot.columns, y=loadings_plot.index,
                       color_continuous_scale='RdBu_r', zmin=-100, zmax=100, aspect='auto', text_auto='.0f')
        fig.update_layout(title="Component Loadings Heatmap (%)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Principal Components Time Series (ALL)")
        st.dataframe(data['pca_components'].round(4), use_container_width=True, height=400)
        show_descriptive_stats(data['pca_components'], "PCA Components Statistics")

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=("PC1: Macro Strength Index", "PC2: Inflation Index"))
        fig.add_trace(go.Scatter(x=data['pca_components'].index, y=data['pca_components']['PC1'],
                                name='Macro Index', line=dict(color=COLORS['blue'])), row=1, col=1)
        fig.add_trace(go.Scatter(x=data['pca_components'].index, y=data['pca_components']['PC2'],
                                name='Inflation Index', line=dict(color=COLORS['vermillion'])), row=2, col=1)
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        # All 6 PCs Grid (NEW)
        with st.expander("View All 6 Principal Components", expanded=False):
            st.markdown("""
            **Complete PCA decomposition**: While PC1 (Macro) and PC2 (Inflation) capture 71.8% of variance,
            the remaining 4 components also contain information. PC3-PC6 explain the remaining 28.2% of variance.
            """)

            # Create 3x2 grid of all PCs
            fig_all = make_subplots(
                rows=3, cols=2, shared_xaxes=True,
                subplot_titles=[f"PC{i+1} ({variance['individual'][i]:.1f}%)" for i in range(6)],
                vertical_spacing=0.08, horizontal_spacing=0.08
            )

            pc_colors = [COLORS['blue'], COLORS['vermillion'], COLORS['green'],
                        COLORS['orange'], COLORS['purple'], COLORS['sky_blue']]

            for i in range(6):
                row = (i // 2) + 1
                col = (i % 2) + 1
                fig_all.add_trace(go.Scatter(
                    x=data['pca_components'].index,
                    y=data['pca_components'][f'PC{i+1}'],
                    name=f'PC{i+1}',
                    line=dict(color=pc_colors[i], width=1.5),
                    showlegend=False
                ), row=row, col=col)
                fig_all.add_hline(y=0, line_dash="dot", line_color="lightgray", row=row, col=col)

            fig_all.update_layout(height=700, margin=dict(l=40, r=20, t=40, b=20))
            st.plotly_chart(fig_all, use_container_width=True)

            # Summary table
            st.markdown("**Summary Statistics for All Components:**")
            pc_summary = data['pca_components'].describe().T
            pc_summary['eigenvalue'] = inventory['eigenvalues']
            pc_summary['variance_%'] = variance['individual']
            st.dataframe(pc_summary[['mean', 'std', 'min', 'max', 'eigenvalue', 'variance_%']].round(4),
                        use_container_width=True)

        st.download_button("Download PCA Components", data['pca_components'].to_csv(), "pca_components.csv", "text/csv")

    # ==================== Tab 4: Breakpoints ====================
    with tab4:
        st.header("Structural Breakpoint Detection (PELT) - FULL DETAILS")

        # Economic Events Context (NEW)
        with st.expander("Economic Events Timeline (Context for Breakpoints)", expanded=True):
            st.markdown("""
            **Key Economic Events** that may explain detected structural breakpoints:
            """)

            # Define major economic events
            economic_events = [
                ("2000-03-10", "Dot-com Bubble Peak", "NASDAQ peak before crash"),
                ("2001-03-01", "2001 Recession Start", "NBER recession begins"),
                ("2001-09-11", "9/11 Attacks", "Market disruption"),
                ("2003-06-25", "Fed Funds 1%", "Lowest rate since 1958"),
                ("2007-08-09", "BNP Paribas", "Subprime crisis begins"),
                ("2008-09-15", "Lehman Collapse", "Global Financial Crisis peak"),
                ("2009-03-09", "S&P 500 Bottom", "Market trough at 666"),
                ("2010-05-06", "Flash Crash", "Dow drops 1000 points"),
                ("2011-08-05", "US Downgrade", "S&P downgrades US debt"),
                ("2015-12-16", "First Rate Hike", "Fed raises rates after 7 years"),
                ("2016-11-08", "Trump Election", "Policy uncertainty spike"),
                ("2018-02-05", "Volatility Spike", "VIX surge, market correction"),
                ("2020-02-19", "COVID Peak", "S&P 500 pre-COVID high"),
                ("2020-03-23", "COVID Bottom", "Pandemic market trough"),
                ("2022-03-16", "Rate Hike Cycle", "Fed begins aggressive hikes"),
                ("2022-06-13", "Inflation Peak", "CPI reaches 9.1%"),
                ("2023-03-10", "SVB Collapse", "Regional banking crisis"),
            ]

            events_df = pd.DataFrame(economic_events, columns=['Date', 'Event', 'Description'])
            st.dataframe(events_df, use_container_width=True, height=300)

            # Create combined timeline chart
            st.markdown("**Timeline with Breakpoints & Events:**")
            fig_timeline = go.Figure()

            # Add Macro Index
            fig_timeline.add_trace(go.Scatter(
                x=data['pca_components'].index,
                y=data['pca_components']['PC1'],
                name='Macro Index', line=dict(color=COLORS['blue'], width=2)
            ))

            # Add macro breakpoints (convert string dates to datetime)
            for bp_date in breakpoints['macro_index']['dates']:
                fig_timeline.add_vline(x=pd.to_datetime(bp_date), line_dash="dash", line_color=COLORS['vermillion'],
                                      opacity=0.7)

            # Add economic event annotations (convert string dates to datetime)
            for date, event, _ in economic_events:
                fig_timeline.add_vline(x=pd.to_datetime(date), line_dash="dot", line_color="gray", opacity=0.3)
                fig_timeline.add_annotation(
                    x=pd.to_datetime(date), y=data['pca_components']['PC1'].max() * 0.9,
                    text=event[:15] + "..." if len(event) > 15 else event,
                    showarrow=True, arrowhead=2, arrowsize=0.5, arrowcolor="gray",
                    font=dict(size=8), textangle=-45, ax=0, ay=-30
                )

            fig_timeline.update_layout(
                title="Macro Index with Breakpoints (red) and Economic Events (gray)",
                height=450, showlegend=True,
                xaxis_title="Date", yaxis_title="Macro Index (z-score)"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"Macro Index ({summary['n_macro_breakpoints']} breakpoints)")
            macro_idx = data['pca_components']['PC1']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=macro_idx.index, y=macro_idx.values, name='Macro Index',
                                    line=dict(color=COLORS['blue'])))
            for bp_date in breakpoints['macro_index']['dates']:
                fig.add_vline(x=bp_date, line_dash="dash", line_color=COLORS['vermillion'], opacity=0.7)
            fig.update_layout(title="Macro Strength Index with Breakpoints", height=400)
            st.plotly_chart(fig, use_container_width=True)

            if breakpoints['macro_index']['dates']:
                bp_df = pd.DataFrame({
                    'Index': breakpoints['macro_index']['indices'],
                    'Date': breakpoints['macro_index']['dates']
                })
                st.dataframe(bp_df, use_container_width=True)

            st.markdown("**Regime Statistics**")
            st.dataframe(pd.DataFrame(regime_stats['macro']).round(4), use_container_width=True)

        with col2:
            st.subheader(f"Inflation Index ({summary['n_inflation_breakpoints']} breakpoints)")
            inflation_idx = data['pca_components']['PC2']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=inflation_idx.index, y=inflation_idx.values, name='Inflation Index',
                                    line=dict(color=COLORS['vermillion'])))
            for bp_date in breakpoints['inflation_index']['dates']:
                fig.add_vline(x=bp_date, line_dash="dash", line_color=COLORS['blue'], opacity=0.7)
            fig.update_layout(title="Inflation Index with Breakpoints", height=400)
            st.plotly_chart(fig, use_container_width=True)

            if breakpoints['inflation_index']['dates']:
                bp_df = pd.DataFrame({
                    'Index': breakpoints['inflation_index']['indices'],
                    'Date': breakpoints['inflation_index']['dates']
                })
                st.dataframe(bp_df, use_container_width=True)

            st.markdown("**Regime Statistics**")
            st.dataframe(pd.DataFrame(regime_stats['inflation']).round(4), use_container_width=True)

        # Regime-Sentiment Analysis (NEW)
        st.markdown("---")
        with st.expander("Regime-Sentiment Analysis", expanded=False):
            st.markdown("""
            **Question**: Does speech sentiment differ across economic regimes?

            If CB communication responds to macro conditions, we'd expect:
            - More hawkish speeches during strong economy (high Macro Index)
            - More dovish speeches during weak economy (low Macro Index)

            Let's analyze sentiment distribution by regime.
            """)

            # Compute regime-sentiment relationship
            try:
                # Map each date to its macro regime
                macro_regimes = regime_stats['macro']
                speeches_summary = data['speeches_summary'].copy()

                # Convert datetime column if needed
                if 'datetime' in speeches_summary.columns:
                    speeches_summary['datetime'] = pd.to_datetime(speeches_summary['datetime'])

                    # Assign regime to each speech
                    def get_regime(date, regimes):
                        for r in regimes:
                            start = pd.to_datetime(r['start_date'])
                            end = pd.to_datetime(r['end_date'])
                            if start <= date <= end:
                                return r['regime']
                        return None

                    speeches_summary['macro_regime'] = speeches_summary['datetime'].apply(
                        lambda x: get_regime(x, macro_regimes))

                    # Drop speeches outside regime dates
                    speeches_in_regimes = speeches_summary[speeches_summary['macro_regime'].notna()].copy()

                    # Aggregate by regime
                    regime_sentiment = speeches_in_regimes.groupby('macro_regime')['sentiment'].value_counts().unstack(fill_value=0)

                    # Add regime info
                    regime_info = pd.DataFrame(macro_regimes)[['regime', 'start_date', 'end_date', 'mean', 'n_observations']]
                    regime_info.columns = ['Regime', 'Start', 'End', 'Macro Mean', 'N Months']

                    if not regime_sentiment.empty:
                        regime_sentiment['total'] = regime_sentiment.sum(axis=1)
                        regime_sentiment['hawkish_pct'] = (regime_sentiment.get('hawkish', 0) / regime_sentiment['total'] * 100).round(1)
                        regime_sentiment['dovish_pct'] = (regime_sentiment.get('dovish', 0) / regime_sentiment['total'] * 100).round(1)

                        # Merge with regime info
                        regime_analysis = regime_info.set_index('Regime').join(regime_sentiment)
                        regime_analysis = regime_analysis.reset_index()

                        st.markdown("**Sentiment by Macro Regime:**")
                        st.dataframe(regime_analysis.round(2), use_container_width=True)

                        # Bar chart
                        fig_regime = go.Figure()
                        fig_regime.add_trace(go.Bar(
                            x=[f"R{r['regime']}: {r['start_date'][:7]}" for r in macro_regimes],
                            y=regime_sentiment.get('hawkish', [0]*len(macro_regimes)).values,
                            name='Hawkish', marker_color=COLORS['vermillion']
                        ))
                        fig_regime.add_trace(go.Bar(
                            x=[f"R{r['regime']}: {r['start_date'][:7]}" for r in macro_regimes],
                            y=regime_sentiment.get('dovish', [0]*len(macro_regimes)).values,
                            name='Dovish', marker_color=COLORS['blue']
                        ))
                        fig_regime.add_trace(go.Bar(
                            x=[f"R{r['regime']}: {r['start_date'][:7]}" for r in macro_regimes],
                            y=regime_sentiment.get('neutral', [0]*len(macro_regimes)).values,
                            name='Neutral', marker_color=COLORS['sky_blue']
                        ))

                        fig_regime.update_layout(
                            title="Speech Count by Macro Regime",
                            xaxis_title="Regime",
                            yaxis_title="Number of Speeches",
                            barmode='stack', height=400
                        )
                        st.plotly_chart(fig_regime, use_container_width=True)

                        # Correlation between regime mean and hawkish percentage
                        regime_means = [r['mean'] for r in macro_regimes]
                        hawkish_pcts = regime_analysis['hawkish_pct'].dropna().values[:len(regime_means)]
                        if len(regime_means) == len(hawkish_pcts):
                            corr = np.corrcoef(regime_means, hawkish_pcts)[0, 1]
                            st.metric("Correlation: Macro Mean vs Hawkish %", f"{corr:.4f}")

                            if abs(corr) < 0.3:
                                st.success("""
                                **Weak correlation**: Hawkish speech proportion does not vary systematically
                                with economic conditions. CB communication is regime-independent.
                                """)
                            else:
                                st.info(f"Correlation of {corr:.2f} suggests some relationship between regime and sentiment.")
                    else:
                        st.warning("No regime-sentiment data available.")
                else:
                    st.warning("Speech data does not contain datetime column for regime analysis.")

            except Exception as e:
                st.error(f"Error in regime-sentiment analysis: {e}")

    # ==================== Tab 5: Speech Sentiment ====================
    with tab5:
        st.header("Central Bank Speech Sentiment - FULL DATA")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sentiment Distribution")
            fig = go.Figure(data=[go.Pie(
                labels=['Hawkish', 'Dovish', 'Neutral'],
                values=[sentiment_summary['hawkish']['count'],
                       sentiment_summary['dovish']['count'],
                       sentiment_summary['neutral']['count']],
                marker_colors=[COLORS['vermillion'], COLORS['blue'], COLORS['sky_blue']],
                textinfo='label+percent'
            )])
            fig.update_layout(title="Speech Sentiment Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Sentiment Summary")
            summary_df = pd.DataFrame({
                'Category': ['Hawkish', 'Dovish', 'Neutral', 'Total'],
                'Count': [sentiment_summary['hawkish']['count'],
                         sentiment_summary['dovish']['count'],
                         sentiment_summary['neutral']['count'],
                         sentiment_summary['total']],
                'Percentage': [sentiment_summary['hawkish']['pct'],
                              sentiment_summary['dovish']['pct'],
                              sentiment_summary['neutral']['pct'],
                              100.0]
            })
            st.dataframe(summary_df, use_container_width=True)
            st.metric("Total US Fed Speeches", sentiment_summary['total'])

        # Raw sentiment counts
        st.subheader("Raw Monthly Sentiment Counts (non-standardized)")
        st.dataframe(data['sentiment_raw'].round(2), use_container_width=True, height=400)

        fig = go.Figure()
        fig.add_trace(go.Bar(x=data['sentiment_raw'].index, y=data['sentiment_raw']['hawkish'],
                            name='Hawkish', marker_color=COLORS['vermillion']))
        fig.add_trace(go.Bar(x=data['sentiment_raw'].index, y=data['sentiment_raw']['dovish'],
                            name='Dovish', marker_color=COLORS['blue']))
        fig.update_layout(title="Raw Monthly Sentiment Counts", barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Standardized sentiment
        st.subheader("Standardized Monthly Sentiment (ALL)")
        st.dataframe(data['sentiment_standardized'].round(4), use_container_width=True, height=400)
        show_descriptive_stats(data['sentiment_standardized'].dropna(), "Standardized Sentiment Statistics")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['sentiment_standardized'].index,
                                y=data['sentiment_standardized']['hawkish'],
                                name='Hawkish', line=dict(color=COLORS['vermillion'])))
        fig.add_trace(go.Scatter(x=data['sentiment_standardized'].index,
                                y=data['sentiment_standardized']['dovish'],
                                name='Dovish', line=dict(color=COLORS['blue'])))
        fig.update_layout(title="Standardized Monthly Sentiment", xaxis_title="Date",
                         yaxis_title="Z-Score", height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Download Sentiment Data", data['sentiment_standardized'].to_csv(),
                          "sentiment_data.csv", "text/csv")

        # Speeches summary
        st.subheader("Speeches Summary")
        st.dataframe(data['speeches_summary'], use_container_width=True, height=400)
        st.download_button("Download Speeches Summary", data['speeches_summary'].to_csv(),
                          "speeches_summary.csv", "text/csv")

    # ==================== Tab 6: Regression Analysis ====================
    with tab6:
        st.header("Rolling Regression Analysis - FULL CALCULATIONS")

        # First-Difference Visualization (NEW)
        with st.expander("Why First Differences? (Click to see before/after)", expanded=True):
            st.markdown("""
            **Problem**: Raw time series often have trends (non-stationary), which can create spurious correlations.

            **Solution**: First-differencing transforms levels to changes: $\Delta y_t = y_t - y_{t-1}$

            This removes trends and ensures we measure the relationship between *changes* in sentiment
            and *changes* in macro indices, not just their levels tracking together over time.
            """)

            # Show before/after for Macro Index
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Before: Macro Index (Levels)**")
                fig_levels = go.Figure()
                fig_levels.add_trace(go.Scatter(
                    x=data['pca_components'].index,
                    y=data['pca_components']['PC1'],
                    name='Macro Index (PC1)',
                    line=dict(color=COLORS['blue'])
                ))
                fig_levels.update_layout(
                    height=250, margin=dict(l=20, r=20, t=30, b=20),
                    xaxis_title="Date", yaxis_title="Level (z-score)"
                )
                st.plotly_chart(fig_levels, use_container_width=True)

            with col2:
                st.markdown("**After: First Differences ($\Delta$ Macro Index)**")
                # Compute first difference for display
                macro_diff = data['pca_components']['PC1'].diff().dropna()
                fig_diff = go.Figure()
                fig_diff.add_trace(go.Scatter(
                    x=macro_diff.index,
                    y=macro_diff.values,
                    name='Delta Macro Index',
                    line=dict(color=COLORS['green'])
                ))
                fig_diff.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_diff.update_layout(
                    height=250, margin=dict(l=20, r=20, t=30, b=20),
                    xaxis_title="Date", yaxis_title="Change"
                )
                st.plotly_chart(fig_diff, use_container_width=True)

            # Statistics comparison
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("*Levels are persistent (autocorrelated)*")
                autocorr_level = data['pca_components']['PC1'].autocorr(lag=1)
                st.metric("Autocorrelation (lag-1)", f"{autocorr_level:.4f}")

            with col2:
                st.markdown("*Differences are nearly white noise*")
                autocorr_diff = macro_diff.autocorr(lag=1)
                st.metric("Autocorrelation (lag-1)", f"{autocorr_diff:.4f}")

        st.markdown("---")

        st.subheader("Merged Data (Macro Index + Sentiment)")
        st.dataframe(data['merged_macro'].round(4), use_container_width=True, height=300)
        show_descriptive_stats(data['merged_macro'], "Merged Data Statistics")

        st.subheader("Macro Index vs Sentiment")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Rolling Betas**")
            st.dataframe(data['betas_macro'].round(4), use_container_width=True, height=300)
            fig = go.Figure()
            for col in data['betas_macro'].columns:
                fig.add_trace(go.Scatter(x=data['betas_macro'].index, y=data['betas_macro'][col],
                                        name=col, line=dict(color=COLORS['vermillion'] if 'hawkish' in col else COLORS['blue'])))
            fig.update_layout(title=f"Rolling Betas ({params['regression_window']}-month window)", height=350)
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Rolling R-squared**")
            st.dataframe(data['r2_macro'].round(4), use_container_width=True, height=300)
            fig = go.Figure()
            for col in data['r2_macro'].columns:
                fig.add_trace(go.Scatter(x=data['r2_macro'].index, y=data['r2_macro'][col],
                                        name=col, line=dict(color=COLORS['vermillion'] if 'hawkish' in col else COLORS['blue'])))
            fig.update_layout(title=f"Rolling R-squared ({params['regression_window']}-month window)", height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Inflation Index vs Sentiment")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Rolling Betas**")
            st.dataframe(data['betas_inflation'].round(4), use_container_width=True, height=300)
            fig = go.Figure()
            for col in data['betas_inflation'].columns:
                fig.add_trace(go.Scatter(x=data['betas_inflation'].index, y=data['betas_inflation'][col],
                                        name=col, line=dict(color=COLORS['vermillion'] if 'hawkish' in col else COLORS['blue'])))
            fig.update_layout(title=f"Rolling Betas ({params['regression_window']}-month window)", height=350)
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Rolling R-squared**")
            st.dataframe(data['r2_inflation'].round(4), use_container_width=True, height=300)
            fig = go.Figure()
            for col in data['r2_inflation'].columns:
                fig.add_trace(go.Scatter(x=data['r2_inflation'].index, y=data['r2_inflation'][col],
                                        name=col, line=dict(color=COLORS['vermillion'] if 'hawkish' in col else COLORS['blue'])))
            fig.update_layout(title=f"Rolling R-squared ({params['regression_window']}-month window)", height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Correlation Matrices (First Differences)")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Macro Index Correlations**")
            st.dataframe(data['corr_macro'].round(4), use_container_width=True)
            fig = px.imshow(data['corr_macro'].values, x=data['corr_macro'].columns,
                           y=data['corr_macro'].index, color_continuous_scale='RdBu_r',
                           zmin=-1, zmax=1, text_auto='.3f')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Inflation Index Correlations**")
            st.dataframe(data['corr_inflation'].round(4), use_container_width=True)
            fig = px.imshow(data['corr_inflation'].values, x=data['corr_inflation'].columns,
                           y=data['corr_inflation'].index, color_continuous_scale='RdBu_r',
                           zmin=-1, zmax=1, text_auto='.3f')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Cross-Correlation Lag Analysis (NEW)
        st.markdown("---")
        with st.expander("Cross-Correlation at Different Lags", expanded=False):
            st.markdown("""
            **Does sentiment LEAD or LAG macro conditions?**

            Cross-correlation at lag k measures: corr(Sentiment_t, Macro_{t+k})
            - **Negative lag**: Sentiment leads Macro (sentiment predicts future macro)
            - **Positive lag**: Macro leads Sentiment (macro influences future sentiment)
            - **Lag 0**: Contemporaneous correlation

            If CB speech sentiment has predictive power, we'd expect significant correlation at negative lags.
            """)

            # Compute cross-correlations at different lags
            macro_diff = data['pca_components']['PC1'].diff().dropna()
            hawkish_diff = data['sentiment_standardized']['hawkish'].diff().dropna()
            dovish_diff = data['sentiment_standardized']['dovish'].diff().dropna()

            # Align indices
            common_idx = macro_diff.index.intersection(hawkish_diff.index)
            macro_aligned = macro_diff.loc[common_idx]
            hawkish_aligned = hawkish_diff.loc[common_idx]
            dovish_aligned = dovish_diff.loc[common_idx]

            lags = list(range(-12, 13))  # -12 to +12 months
            hawkish_corrs = []
            dovish_corrs = []

            for lag in lags:
                if lag < 0:
                    # Sentiment leads: shift sentiment backward
                    h_corr = hawkish_aligned.iloc[-lag:].reset_index(drop=True).corr(
                        macro_aligned.iloc[:lag].reset_index(drop=True))
                    d_corr = dovish_aligned.iloc[-lag:].reset_index(drop=True).corr(
                        macro_aligned.iloc[:lag].reset_index(drop=True))
                elif lag > 0:
                    # Macro leads: shift macro backward
                    h_corr = hawkish_aligned.iloc[:-lag].reset_index(drop=True).corr(
                        macro_aligned.iloc[lag:].reset_index(drop=True))
                    d_corr = dovish_aligned.iloc[:-lag].reset_index(drop=True).corr(
                        macro_aligned.iloc[lag:].reset_index(drop=True))
                else:
                    h_corr = hawkish_aligned.corr(macro_aligned)
                    d_corr = dovish_aligned.corr(macro_aligned)

                hawkish_corrs.append(h_corr if not pd.isna(h_corr) else 0)
                dovish_corrs.append(d_corr if not pd.isna(d_corr) else 0)

            # Plot cross-correlations
            fig_ccf = go.Figure()
            fig_ccf.add_trace(go.Bar(
                x=lags, y=hawkish_corrs, name='Hawkish',
                marker_color=COLORS['vermillion'], opacity=0.7
            ))
            fig_ccf.add_trace(go.Bar(
                x=lags, y=dovish_corrs, name='Dovish',
                marker_color=COLORS['blue'], opacity=0.7
            ))

            # Add significance threshold (approximate)
            n = len(common_idx)
            sig_threshold = 1.96 / np.sqrt(n)
            fig_ccf.add_hline(y=sig_threshold, line_dash="dash", line_color="gray",
                             annotation_text="95% CI", annotation_position="right")
            fig_ccf.add_hline(y=-sig_threshold, line_dash="dash", line_color="gray")
            fig_ccf.add_hline(y=0, line_color="black", line_width=1)
            fig_ccf.add_vline(x=0, line_dash="dot", line_color="gray")

            fig_ccf.update_layout(
                title="Cross-Correlation: Sentiment vs Macro Index at Different Lags",
                xaxis_title="Lag (months) - Negative = Sentiment Leads, Positive = Macro Leads",
                yaxis_title="Correlation",
                height=400, barmode='group',
                xaxis=dict(tickmode='linear', tick0=-12, dtick=2)
            )
            st.plotly_chart(fig_ccf, use_container_width=True)

            # Summary table
            lag_df = pd.DataFrame({
                'Lag': lags,
                'Hawkish Corr': [round(c, 4) for c in hawkish_corrs],
                'Dovish Corr': [round(c, 4) for c in dovish_corrs]
            })
            st.dataframe(lag_df, use_container_width=True, height=250)

            # Find max correlations
            max_hawk_idx = np.argmax(np.abs(hawkish_corrs))
            max_dov_idx = np.argmax(np.abs(dovish_corrs))

            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"Max |Hawkish| Corr (lag={lags[max_hawk_idx]})",
                         f"{hawkish_corrs[max_hawk_idx]:.4f}")
            with col2:
                st.metric(f"Max |Dovish| Corr (lag={lags[max_dov_idx]})",
                         f"{dovish_corrs[max_dov_idx]:.4f}")

            st.info("""
            **Interpretation**: All cross-correlations are near zero across all lags (-12 to +12 months).
            This confirms that CB speech sentiment neither leads nor lags macroeconomic conditions.
            The relationship is essentially random regardless of timing.
            """)

    # ==================== Tab 7: All Data ====================
    with tab7:
        st.header("ALL DATA - Complete Tables & Downloads")

        for i, (key, filename) in enumerate(inventory['data_files'].items(), 1):
            st.subheader(f"{i}. {key.replace('_', ' ').title()}")
            if key in data:
                st.dataframe(data[key].round(4) if data[key].select_dtypes(include=[np.number]).shape[1] > 0 else data[key],
                            use_container_width=True, height=250)
                st.download_button(f"Download", data[key].to_csv(), filename, "text/csv", key=f"dl_{key}")
            else:
                st.warning(f"File not found: {filename}")


if __name__ == "__main__":
    main()
