"""
Stationarity Tests (ADF and KPSS) for Macroeconomic Variables
=============================================================
Tests for unit roots in macro variables and PCA components.

Author: Statistical analysis for Taibi (2025) paper
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
from pathlib import Path
import json
import warnings

warnings.filterwarnings('ignore')

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "cb_speeches" / "data"


def load_raw_macro():
    """Load raw macroeconomic data."""
    raw_path = DATA_DIR / "raw_macro.csv"
    df = pd.read_csv(raw_path, index_col=0, parse_dates=True)
    return df


def load_scaled_macro():
    """Load standardized macroeconomic data."""
    scaled_path = DATA_DIR / "scaled_macro.csv"
    df = pd.read_csv(scaled_path, index_col=0, parse_dates=True)
    return df


def load_pca_components():
    """Load PCA components."""
    pca_path = DATA_DIR / "pca_components.csv"
    df = pd.read_csv(pca_path, index_col=0, parse_dates=True)
    return df


def run_adf_test(series, regression='c', maxlag=None):
    """
    Run Augmented Dickey-Fuller test for unit root.

    H0: Series has a unit root (non-stationary)
    H1: Series is stationary

    Parameters
    ----------
    series : array-like
        Time series data
    regression : str
        'c' = constant only, 'ct' = constant + trend, 'n' = none
    maxlag : int or None
        Maximum lag to consider (None = automatic)

    Returns
    -------
    dict with test results
    """
    # Clean NaN values
    series = pd.Series(series).dropna()

    if len(series) < 20:
        return {"error": "Insufficient data for ADF test"}

    try:
        result = adfuller(series, regression=regression, maxlag=maxlag, autolag='AIC')
        return {
            'adf_statistic': float(result[0]),
            'p_value': float(result[1]),
            'lags_used': int(result[2]),
            'n_obs': int(result[3]),
            'critical_values': {k: float(v) for k, v in result[4].items()},
            'is_stationary': result[1] < 0.05  # Reject H0 at 5%
        }
    except Exception as e:
        return {"error": str(e)}


def run_kpss_test(series, regression='c', nlags='auto'):
    """
    Run KPSS test for stationarity.

    H0: Series is stationary
    H1: Series has a unit root (non-stationary)

    Note: KPSS and ADF have opposite null hypotheses!

    Parameters
    ----------
    series : array-like
        Time series data
    regression : str
        'c' = constant only, 'ct' = constant + trend

    Returns
    -------
    dict with test results
    """
    # Clean NaN values
    series = pd.Series(series).dropna()

    if len(series) < 20:
        return {"error": "Insufficient data for KPSS test"}

    try:
        result = kpss(series, regression=regression, nlags=nlags)
        return {
            'kpss_statistic': float(result[0]),
            'p_value': float(result[1]),
            'lags_used': int(result[2]),
            'critical_values': {k: float(v) for k, v in result[3].items()},
            'is_stationary': result[1] > 0.05  # Fail to reject H0 at 5%
        }
    except Exception as e:
        return {"error": str(e)}


def interpret_stationarity(adf_result, kpss_result):
    """
    Interpret combined ADF and KPSS results.

    | ADF    | KPSS   | Interpretation                    |
    |--------|--------|-----------------------------------|
    | Reject | Fail   | Stationary (both agree)          |
    | Fail   | Reject | Non-stationary (both agree)      |
    | Reject | Reject | Trend-stationary (ADF says stat) |
    | Fail   | Fail   | Inconclusive                     |

    Returns interpretation string.
    """
    if 'error' in adf_result or 'error' in kpss_result:
        return "ERROR in tests"

    adf_reject = adf_result['p_value'] < 0.05  # Reject unit root
    kpss_reject = kpss_result['p_value'] < 0.05  # Reject stationarity

    if adf_reject and not kpss_reject:
        return "STATIONARY (both tests agree)"
    elif not adf_reject and kpss_reject:
        return "NON-STATIONARY (both tests agree)"
    elif adf_reject and kpss_reject:
        return "TREND-STATIONARY (may need differencing)"
    else:
        return "INCONCLUSIVE (tests disagree)"


def test_series_stationarity(series, name="Series"):
    """
    Run both ADF and KPSS tests on a series.

    Returns dict with all results.
    """
    adf = run_adf_test(series)
    kpss = run_kpss_test(series)
    interpretation = interpret_stationarity(adf, kpss)

    return {
        'name': name,
        'adf': adf,
        'kpss': kpss,
        'interpretation': interpretation
    }


def run_full_stationarity_analysis():
    """Run stationarity tests on all relevant series."""

    print("=" * 70)
    print("STATIONARITY TESTS (ADF and KPSS)")
    print("=" * 70)
    print()

    results = {}

    # Test raw macro variables
    print("-" * 50)
    print("RAW MACROECONOMIC VARIABLES (Levels)")
    print("-" * 50)

    raw_macro = load_raw_macro()
    for col in raw_macro.columns:
        res = test_series_stationarity(raw_macro[col], f"Raw {col}")
        results[f'raw_{col}'] = res

        print(f"\n{col}:")
        if 'error' not in res['adf']:
            print(f"  ADF: stat={res['adf']['adf_statistic']:.4f}, p={res['adf']['p_value']:.4f}")
        if 'error' not in res['kpss']:
            print(f"  KPSS: stat={res['kpss']['kpss_statistic']:.4f}, p={res['kpss']['p_value']:.4f}")
        print(f"  Interpretation: {res['interpretation']}")

    # Test standardized macro variables
    print("\n" + "-" * 50)
    print("STANDARDIZED MACROECONOMIC VARIABLES (Rolling z-scores)")
    print("-" * 50)

    scaled_macro = load_scaled_macro()
    for col in scaled_macro.columns:
        res = test_series_stationarity(scaled_macro[col], f"Scaled {col}")
        results[f'scaled_{col}'] = res

        print(f"\n{col}:")
        if 'error' not in res['adf']:
            print(f"  ADF: stat={res['adf']['adf_statistic']:.4f}, p={res['adf']['p_value']:.4f}")
        if 'error' not in res['kpss']:
            print(f"  KPSS: stat={res['kpss']['kpss_statistic']:.4f}, p={res['kpss']['p_value']:.4f}")
        print(f"  Interpretation: {res['interpretation']}")

    # Test PCA components
    print("\n" + "-" * 50)
    print("PRINCIPAL COMPONENTS")
    print("-" * 50)

    pca = load_pca_components()
    for col in ['PC1', 'PC2']:
        res = test_series_stationarity(pca[col], f"PCA {col}")
        results[f'pca_{col}'] = res

        name = "Macro Index" if col == "PC1" else "Inflation Index"
        print(f"\n{col} ({name}):")
        if 'error' not in res['adf']:
            print(f"  ADF: stat={res['adf']['adf_statistic']:.4f}, p={res['adf']['p_value']:.4f}")
        if 'error' not in res['kpss']:
            print(f"  KPSS: stat={res['kpss']['kpss_statistic']:.4f}, p={res['kpss']['p_value']:.4f}")
        print(f"  Interpretation: {res['interpretation']}")

    # Test first differences of PCA components
    print("\n" + "-" * 50)
    print("FIRST DIFFERENCES OF PRINCIPAL COMPONENTS")
    print("-" * 50)

    for col in ['PC1', 'PC2']:
        diff_series = pca[col].diff().dropna()
        res = test_series_stationarity(diff_series, f"D.{col}")
        results[f'diff_{col}'] = res

        name = "D.Macro Index" if col == "PC1" else "D.Inflation Index"
        print(f"\n{name}:")
        if 'error' not in res['adf']:
            print(f"  ADF: stat={res['adf']['adf_statistic']:.4f}, p={res['adf']['p_value']:.4f}")
        if 'error' not in res['kpss']:
            print(f"  KPSS: stat={res['kpss']['kpss_statistic']:.4f}, p={res['kpss']['p_value']:.4f}")
        print(f"  Interpretation: {res['interpretation']}")

    # Summary table
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print()
    print("| Variable           | ADF p-val | KPSS p-val | Conclusion          |")
    print("|" + "-" * 20 + "|" + "-" * 11 + "|" + "-" * 12 + "|" + "-" * 21 + "|")

    for key, res in results.items():
        var_name = res['name'][:18]
        if 'error' not in res['adf'] and 'error' not in res['kpss']:
            adf_p = f"{res['adf']['p_value']:.4f}"
            kpss_p = f"{res['kpss']['p_value']:.4f}"
            interp = res['interpretation'][:19]
            print(f"| {var_name:<18} | {adf_p:>9} | {kpss_p:>10} | {interp:<19} |")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    print("ADF Test: H0 = unit root (non-stationary). Reject if p < 0.05.")
    print("KPSS Test: H0 = stationary. Reject if p < 0.05.")
    print()
    print("Key Finding:")
    print("- Raw macro variables are generally non-stationary (as expected)")
    print("- Rolling standardization makes series more stationary")
    print("- PCA components (Macro/Inflation indices) should be checked")
    print("- First differences are typically stationary")

    return results


def save_results(results, output_path=None):
    """Save results to JSON file."""
    if output_path is None:
        output_path = Path(__file__).parent / "stationarity_results.json"

    # Clean results for JSON serialization
    clean_results = {}
    for key, res in results.items():
        clean_results[key] = {
            'name': res['name'],
            'interpretation': res['interpretation']
        }
        if 'error' not in res['adf']:
            clean_results[key]['adf_p_value'] = float(res['adf']['p_value'])
            clean_results[key]['adf_statistic'] = float(res['adf']['adf_statistic'])
            clean_results[key]['adf_stationary'] = bool(res['adf']['is_stationary'])
        if 'error' not in res['kpss']:
            clean_results[key]['kpss_p_value'] = float(res['kpss']['p_value'])
            clean_results[key]['kpss_statistic'] = float(res['kpss']['kpss_statistic'])
            clean_results[key]['kpss_stationary'] = bool(res['kpss']['is_stationary'])

    with open(output_path, 'w') as f:
        json.dump(clean_results, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    results = run_full_stationarity_analysis()
    save_results(results)
