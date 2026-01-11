"""
Configuration and constants for CB Speeches analysis.
"""
import os
from pathlib import Path

# =============================================================================
# Paths
# =============================================================================
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "charts"

# Raw data files
SPEECHES_PARQUET = BASE_DIR / "gigando_speeches_ner_v2.parquet"
MACRO_CSV = BASE_DIR / "macroeconomic_data.csv"

# =============================================================================
# Date Range
# =============================================================================
START_DATE = "1996-01-01"
END_DATE = "2025-05-01"

# =============================================================================
# Analysis Parameters
# =============================================================================
RANDOM_STATE = 42
ROLLING_WINDOW = 12  # months for standardization
REGRESSION_WINDOW = 36  # months (3 years) for rolling betas
PELT_PENALTY = 4  # penalty for PELT breakpoint detection
PCA_VARIANCE_THRESHOLD = 0.80  # 80% variance explained

# =============================================================================
# FRED API
# =============================================================================
FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_SERIES = {
    "FEDFUNDS": "FED Funds Rate",
    "CPIAUCNS": "CPI",
    "PPIACO": "PPI",
    "GDP": "GDP",
    "UNRATE": "Unemployment",
    "PAYEMS": "Nonfarm Payrolls",
}

# =============================================================================
# Visualization Colors (Beamer-compatible)
# =============================================================================
COLORS = {
    "MLPURPLE": "#3333B2",
    "MLLAVENDER": "#ADADE0",
    "MLBLUE": "#0066CC",
    "MLORANGE": "#FF7F0E",
    "MLGREEN": "#2CA02C",
    "MLRED": "#D62728",
    "MLGRAY": "#7F7F7F",
}

# Shorthand color variables
MLPURPLE = COLORS["MLPURPLE"]
MLLAVENDER = COLORS["MLLAVENDER"]
MLBLUE = COLORS["MLBLUE"]
MLORANGE = COLORS["MLORANGE"]
MLGREEN = COLORS["MLGREEN"]
MLRED = COLORS["MLRED"]
MLGRAY = COLORS["MLGRAY"]

# =============================================================================
# Matplotlib rcParams (Beamer-scaled fonts)
# =============================================================================
CHART_RCPARAMS = {
    "font.size": 14,
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 13,
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
}

# =============================================================================
# Output file names
# =============================================================================
OUTPUT_FILES = {
    "processed_macro": DATA_DIR / "processed_macro.csv",
    "pca_components": DATA_DIR / "pca_components.csv",
    "pca_loadings": DATA_DIR / "pca_loadings.csv",
    "breakpoints": DATA_DIR / "breakpoints.json",
    "sentiment_aggregated": DATA_DIR / "sentiment_aggregated.csv",
    "rolling_results_macro": DATA_DIR / "rolling_results_macro.csv",
    "rolling_results_inflation": DATA_DIR / "rolling_results_inflation.csv",
    "correlation_matrix": DATA_DIR / "correlation_matrix.csv",
}


# =============================================================================
# Utility Functions
# =============================================================================
def set_random_state(seed: int = RANDOM_STATE) -> None:
    """
    Set random state for reproducibility across all libraries.
    
    Parameters
    ----------
    seed : int
        Random seed value (default: RANDOM_STATE from config)
    """
    import numpy as np
    import random
    
    np.random.seed(seed)
    random.seed(seed)
