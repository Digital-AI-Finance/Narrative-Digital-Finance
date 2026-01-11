"""
Master pipeline script to run the complete CB Speeches analysis.

This script reproduces the analysis from the Jupyter notebook and saves
all intermediate outputs to the data folder.
"""
import sys
from pathlib import Path
import logging
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from analysis.config import (
    DATA_DIR,
    MACRO_CSV,
    START_DATE,
    END_DATE,
    ROLLING_WINDOW,
    REGRESSION_WINDOW,
    PELT_PENALTY,
    PCA_VARIANCE_THRESHOLD,
    OUTPUT_FILES,
)
from analysis.data_loader import load_cached_macro, fetch_fred_data, save_macro_data
from analysis.preprocessing import rolling_standardize, first_difference
from analysis.pca_analysis import (
    fit_pca,
    get_loadings,
    get_n_components_threshold,
    get_variance_explained,
)
from analysis.breakpoint_detection import (
    detect_breakpoints,
    detect_multiple_breakpoints,
    save_breakpoints,
    get_regime_periods,
)
from analysis.speech_sentiment import (
    load_us_speeches,
    aggregate_monthly_sentiment,
    get_sentiment_summary,
)
from analysis.rolling_regression import (
    compute_rolling_analysis,
    compute_autocorrelations,
    compute_correlation_matrix,
)


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_pipeline(use_cached: bool = True, verbose: bool = True) -> Dict[str, Any]:
    """
    Run the complete analysis pipeline.

    Parameters
    ----------
    use_cached : bool
        Whether to use cached macro data (True) or fetch from FRED (False)
    verbose : bool
        Print progress information

    Returns
    -------
    dict
        Dictionary containing all analysis results
    """
    ensure_data_dir()
    results: Dict[str, Any] = {}
    errors: list = []

    # =========================================================================
    # Step 1: Load Macroeconomic Data
    # =========================================================================
    try:
        logger.info("=" * 60)
        logger.info("Step 1: Loading Macroeconomic Data")
        logger.info("=" * 60)

        if use_cached and MACRO_CSV.exists():
            logger.info(f"Loading cached data from {MACRO_CSV}")
            macro_data = load_cached_macro()
        else:
            logger.info("Fetching data from FRED API...")
            macro_data = fetch_fred_data(START_DATE, END_DATE)
            save_macro_data(macro_data)

        logger.info(f"Loaded {len(macro_data)} rows, columns: {list(macro_data.columns)}")
        results["macro_data"] = macro_data
    except Exception as e:
        logger.error(f"Step 1 FAILED: {e}")
        errors.append(("Step 1: Load Macro Data", str(e)))
        raise RuntimeError(f"Pipeline cannot continue without macro data: {e}")

    # =========================================================================
    # Step 2: Rolling Standardization
    # =========================================================================
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Step 2: Rolling Standardization")
        logger.info("=" * 60)

        scaled_data = rolling_standardize(macro_data, window=ROLLING_WINDOW)
        logger.info(f"Scaled data shape: {scaled_data.shape}")

        # Save processed macro data
        scaled_data.to_csv(OUTPUT_FILES["processed_macro"])
        logger.info(f"Saved to {OUTPUT_FILES['processed_macro']}")
        results["scaled_data"] = scaled_data
    except Exception as e:
        logger.error(f"Step 2 FAILED: {e}")
        errors.append(("Step 2: Rolling Standardization", str(e)))
        raise RuntimeError(f"Pipeline cannot continue without scaled data: {e}")

    # =========================================================================
    # Step 3: PCA Analysis
    # =========================================================================
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Step 3: PCA Analysis")
        logger.info("=" * 60)

        pca, pca_df = fit_pca(scaled_data)
        loadings = get_loadings(pca, list(macro_data.columns))
        n_components = get_n_components_threshold(pca, PCA_VARIANCE_THRESHOLD)
        variance_explained = get_variance_explained(pca)

        logger.info(f"Number of components for {PCA_VARIANCE_THRESHOLD*100}% variance: {n_components}")
        logger.info(f"Variance explained:\n{variance_explained}")
        logger.info(f"Loadings:\n{loadings.round(2)}")

        # Save PCA results
        pca_df.to_csv(OUTPUT_FILES["pca_components"])
        loadings.to_csv(OUTPUT_FILES["pca_loadings"])
        logger.info(f"Saved components to {OUTPUT_FILES['pca_components']}")
        logger.info(f"Saved loadings to {OUTPUT_FILES['pca_loadings']}")

        results["pca"] = pca
        results["pca_df"] = pca_df
        results["loadings"] = loadings
        results["variance_explained"] = variance_explained

        # Extract indices
        macro_index = pca_df["PC1"]
        macro_index.name = "Macro Index"
        inflation_index = pca_df["PC2"]
        inflation_index.name = "Inflation Index"

        results["macro_index"] = macro_index
        results["inflation_index"] = inflation_index
    except Exception as e:
        logger.error(f"Step 3 FAILED: {e}")
        errors.append(("Step 3: PCA Analysis", str(e)))
        raise RuntimeError(f"Pipeline cannot continue without PCA: {e}")

    # =========================================================================
    # Step 4: Breakpoint Detection
    # =========================================================================
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Step 4: Breakpoint Detection (PELT)")
        logger.info("=" * 60)

        # Detect breakpoints for both indices
        breaks_macro, break_dates_macro = detect_breakpoints(macro_index, penalty=PELT_PENALTY)
        breaks_inflation, break_dates_inflation = detect_breakpoints(inflation_index, penalty=PELT_PENALTY)

        logger.info(f"Macro Index breakpoints ({len(breaks_macro)}):")
        for date in break_dates_macro:
            logger.info(f"  - {date.strftime('%Y-%m-%d')}")

        logger.info(f"Inflation Index breakpoints ({len(breaks_inflation)}):")
        for date in break_dates_inflation:
            logger.info(f"  - {date.strftime('%Y-%m-%d')}")

        # Save breakpoints
        breakpoints = {
            "macro_index": {
                "indices": breaks_macro,
                "dates": [d.strftime("%Y-%m-%d") for d in break_dates_macro],
            },
            "inflation_index": {
                "indices": breaks_inflation,
                "dates": [d.strftime("%Y-%m-%d") for d in break_dates_inflation],
            },
        }
        save_breakpoints(breakpoints, OUTPUT_FILES["breakpoints"])

        results["break_dates_macro"] = break_dates_macro
        results["break_dates_inflation"] = break_dates_inflation
    except Exception as e:
        logger.error(f"Step 4 FAILED: {e}")
        errors.append(("Step 4: Breakpoint Detection", str(e)))
        # Non-critical - continue without breakpoints
        logger.warning("Continuing without breakpoint analysis...")
        results["break_dates_macro"] = []
        results["break_dates_inflation"] = []

    # =========================================================================
    # Step 5: Speech Sentiment Analysis
    # =========================================================================
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Step 5: Speech Sentiment Analysis")
        logger.info("=" * 60)

        speeches = load_us_speeches()
        sentiment_summary = get_sentiment_summary(speeches)

        logger.info(f"Loaded {len(speeches)} US speeches")
        logger.info(f"Sentiment distribution:\n{sentiment_summary}")

        # Aggregate monthly sentiment
        cb_sentiment = aggregate_monthly_sentiment(
            speeches,
            start_date=START_DATE,
            end_date=END_DATE,
            shift_periods=1,
            standardize=True,
            window=ROLLING_WINDOW,
        )

        # Save sentiment data
        cb_sentiment.to_csv(OUTPUT_FILES["sentiment_aggregated"])
        logger.info(f"Saved sentiment to {OUTPUT_FILES['sentiment_aggregated']}")

        results["speeches"] = speeches
        results["cb_sentiment"] = cb_sentiment
    except Exception as e:
        logger.error(f"Step 5 FAILED: {e}")
        errors.append(("Step 5: Speech Sentiment", str(e)))
        raise RuntimeError(f"Pipeline cannot continue without sentiment data: {e}")

    # =========================================================================
    # Step 6: Rolling Regression Analysis
    # =========================================================================
    try:
        logger.info("\n" + "=" * 60)
        logger.info("Step 6: Rolling Regression Analysis")
        logger.info("=" * 60)

        # Macro Index vs Sentiment
        logger.info("--- Macro Index vs Sentiment ---")

        merged_macro, betas_macro, r2_macro = compute_rolling_analysis(
            macro_index, cb_sentiment, window=REGRESSION_WINDOW
        )

        autocorr_macro = compute_autocorrelations(merged_macro)
        corr_macro = compute_correlation_matrix(merged_macro)

        logger.info("Autocorrelations:")
        for col, val in autocorr_macro.items():
            logger.info(f"  {col}: {val:.4f}")
        logger.info(f"Correlation matrix:\n{corr_macro.round(4)}")

        # Inflation Index vs Sentiment
        logger.info("--- Inflation Index vs Sentiment ---")

        merged_inflation, betas_inflation, r2_inflation = compute_rolling_analysis(
            inflation_index, cb_sentiment, window=REGRESSION_WINDOW
        )

        autocorr_inflation = compute_autocorrelations(merged_inflation)
        corr_inflation = compute_correlation_matrix(merged_inflation)

        logger.info("Autocorrelations:")
        for col, val in autocorr_inflation.items():
            logger.info(f"  {col}: {val:.4f}")
        logger.info(f"Correlation matrix:\n{corr_inflation.round(4)}")

        # Save rolling results
        rolling_macro = pd.concat([betas_macro.add_suffix("_beta"), r2_macro.add_suffix("_r2")], axis=1)
        rolling_inflation = pd.concat([betas_inflation.add_suffix("_beta"), r2_inflation.add_suffix("_r2")], axis=1)

        rolling_macro.to_csv(OUTPUT_FILES["rolling_results_macro"])
        rolling_inflation.to_csv(OUTPUT_FILES["rolling_results_inflation"])

        logger.info(f"Saved macro rolling results to {OUTPUT_FILES['rolling_results_macro']}")
        logger.info(f"Saved inflation rolling results to {OUTPUT_FILES['rolling_results_inflation']}")

        results["merged_macro"] = merged_macro
        results["betas_macro"] = betas_macro
        results["r2_macro"] = r2_macro
        results["corr_macro"] = corr_macro

        results["merged_inflation"] = merged_inflation
        results["betas_inflation"] = betas_inflation
        results["r2_inflation"] = r2_inflation
        results["corr_inflation"] = corr_inflation

        # Save correlation matrix
        corr_macro.to_csv(OUTPUT_FILES["correlation_matrix"])
    except Exception as e:
        logger.error(f"Step 6 FAILED: {e}")
        errors.append(("Step 6: Rolling Regression", str(e)))
        raise RuntimeError(f"Pipeline cannot continue without regression analysis: {e}")

    # =========================================================================
    # Summary
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 60)

    # Report any errors that occurred
    if errors:
        logger.warning(f"\n{len(errors)} step(s) had issues:")
        for step, err in errors:
            logger.warning(f"  - {step}: {err}")

    logger.info("\nKey Findings:")
    logger.info(f"  - PCA: {n_components} components explain {PCA_VARIANCE_THRESHOLD*100}% variance")
    logger.info(f"  - Macro breakpoints: {len(results.get('break_dates_macro', []))}")
    logger.info(f"  - Inflation breakpoints: {len(results.get('break_dates_inflation', []))}")
    logger.info(f"  - Macro-Hawkish correlation: {corr_macro.loc['Macro Index', 'hawkish']:.4f}")
    logger.info(f"  - Macro-Dovish correlation: {corr_macro.loc['Macro Index', 'dovish']:.4f}")
    logger.info(f"  - Inflation-Hawkish correlation: {corr_inflation.loc['Inflation Index', 'hawkish']:.4f}")
    logger.info(f"  - Inflation-Dovish correlation: {corr_inflation.loc['Inflation Index', 'dovish']:.4f}")

    logger.info("\nOutput files:")
    for name, path in OUTPUT_FILES.items():
        status = "OK" if path.exists() else "MISSING"
        logger.info(f"  [{status}] {path}")

    results["errors"] = errors
    return results


if __name__ == "__main__":
    try:
        results = run_pipeline(use_cached=True, verbose=True)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
