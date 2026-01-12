# Central Bank Speeches Analysis Pipeline

Analyzing the relationship between Federal Reserve speech sentiment and macroeconomic conditions using PCA, structural break detection, and rolling regression.

**Key Finding:** Near-zero correlation (0.005) between CB speech sentiment and macroeconomic indices.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full analysis pipeline
python -c "from analysis.run_all import run_pipeline; run_pipeline(use_cached=True, verbose=True)"

# Generate all charts
cd charts && python run_all_charts.py

# Launch interactive dashboard
streamlit run app.py
```

## Project Structure

```
cb_speeches/
├── analysis/           # Core analysis modules
│   ├── config.py       # Configuration and parameters
│   ├── run_all.py      # Master pipeline orchestrator
│   ├── data_loader.py  # FRED API / CSV loading
│   ├── preprocessing.py # Rolling standardization
│   ├── pca_analysis.py # PCA dimensionality reduction
│   ├── breakpoint_detection.py  # PELT algorithm
│   ├── speech_sentiment.py      # Sentiment aggregation
│   └── rolling_regression.py    # Rolling betas and R-squared
├── charts/             # Chart generation scripts
│   ├── 01_scaled_macro_timeseries/
│   ├── 02_principal_components/
│   ├── ...
│   └── run_all_charts.py
├── data/               # Output data files
├── tests/              # Unit tests
├── app.py              # Streamlit dashboard
└── requirements.txt    # Python dependencies
```

## Pipeline Overview

The analysis pipeline consists of 6 sequential steps:

1. **Data Loading** - Load FRED macroeconomic data and CB speeches
2. **Preprocessing** - 12-month rolling standardization
3. **PCA Analysis** - Extract Macro Strength Index (PC1) and Inflation Index (PC2)
4. **Breakpoint Detection** - PELT algorithm identifies structural breaks
5. **Sentiment Aggregation** - Monthly hawkish/dovish counts from speeches
6. **Rolling Regression** - 36-month rolling betas and R-squared

## Data Sources

| Source | Description | Period |
|--------|-------------|--------|
| FRED | Fed Funds Rate, CPI, PPI, GDP, Unemployment, Nonfarm Payrolls | 1996-2025 |
| BIS/Gigando | 2,421 US Federal Reserve speeches with sentiment labels | 1996-2025 |

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| ROLLING_WINDOW | 12 | Months for standardization |
| REGRESSION_WINDOW | 36 | Months for rolling regression |
| PELT_PENALTY | 4 | Breakpoint detection sensitivity |
| RANDOM_STATE | 42 | Reproducibility seed |

## Output Files

### Core Results (data/)

| File | Description |
|------|-------------|
| `pca_components.csv` | PC1 (Macro Index), PC2 (Inflation Index), PC3-6 |
| `pca_loadings.csv` | Component weights on each macro variable |
| `breakpoints.json` | PELT-detected structural break dates |
| `sentiment_standardized.csv` | Monthly hawkish/dovish standardized counts |
| `correlation_matrix.csv` | First-difference correlations |
| `inventory.json` | Complete analysis summary with all statistics |

### Charts (charts/)

12 publication-ready figures covering:
- Scaled macroeconomic time series
- Principal components over time
- Structural breakpoints (Macro and Inflation indices)
- Speech sentiment distribution
- Rolling regression results (betas, R-squared)
- Correlation matrix heatmap
- PCA loadings heatmap

## Running Tests

```bash
cd cb_speeches
python -m pytest tests/ -v
```

## Requirements

- Python 3.9+
- FRED API key (optional, for fresh macro data download)

Set FRED API key:
```bash
export FRED_API_KEY="your_api_key_here"
```

## Citation

```bibtex
@article{taibi2025cbspeeches,
  title={Central Bank Communication and Macroeconomic Conditions:
         A PCA-Based Framework for Analyzing Narrative-Reality Disconnect},
  author={Taibi, Gabin},
  journal={Working Paper},
  year={2025},
  institution={University of Zurich}
}
```

## License

Part of the SNSF Narrative Digital Finance project (Grant IZCOZ0_213370).

## Links

- [Project Website](https://digital-ai-finance.github.io/Narrative-Digital-Finance/cb-speeches/)
- [GitHub Repository](https://github.com/Digital-AI-Finance/Narrative-Digital-Finance-CB-Speeches)
