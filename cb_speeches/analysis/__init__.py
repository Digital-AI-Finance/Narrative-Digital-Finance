"""
CB Speeches Analysis Module
===========================

Modular Python scripts for analyzing Central Bank speeches and macroeconomic data.

Key Finding: Near-zero correlation (0.005) between CB speech sentiment and macro indices.
"""

from .config import (
    RANDOM_STATE,
    ROLLING_WINDOW,
    REGRESSION_WINDOW,
    PELT_PENALTY,
    PCA_VARIANCE_THRESHOLD,
    DATA_DIR,
    CHARTS_DIR,
    OUTPUT_FILES,
    FRED_SERIES,
    set_random_state,
)
from .data_loader import fetch_fred_data, load_cached_macro
from .preprocessing import rolling_standardize, first_difference, align_dataframes
from .pca_analysis import fit_pca, get_loadings, get_components, get_variance_explained
from .breakpoint_detection import detect_breakpoints, detect_multiple_breakpoints, save_breakpoints
from .speech_sentiment import load_us_speeches, aggregate_monthly_sentiment
from .rolling_regression import beta_1pred, compute_rolling_analysis

__version__ = "1.0.0"

__all__ = [
    # Config
    "RANDOM_STATE",
    "ROLLING_WINDOW",
    "REGRESSION_WINDOW",
    "PELT_PENALTY",
    "PCA_VARIANCE_THRESHOLD",
    "DATA_DIR",
    "CHARTS_DIR",
    "OUTPUT_FILES",
    "FRED_SERIES",
    "set_random_state",
    # Data loading
    "fetch_fred_data",
    "load_cached_macro",
    # Preprocessing
    "rolling_standardize",
    "first_difference",
    "align_dataframes",
    # PCA
    "fit_pca",
    "get_loadings",
    "get_components",
    "get_variance_explained",
    # Breakpoint detection
    "detect_breakpoints",
    "detect_multiple_breakpoints",
    "save_breakpoints",
    # Sentiment
    "load_us_speeches",
    "aggregate_monthly_sentiment",
    # Rolling regression
    "beta_1pred",
    "compute_rolling_analysis",
]
