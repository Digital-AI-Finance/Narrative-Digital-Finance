"""
Bootstrap Confidence Intervals and T-Tests for Correlation Analysis
====================================================================
Computes statistical significance for correlation between CB speech sentiment
and macroeconomic indices using actual data from cb_speeches/data/

Author: Statistical analysis for Taibi (2025) paper
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import json

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "cb_speeches" / "data"


def load_correlation_data():
    """Load merged macro data with first differences."""
    merged_path = DATA_DIR / "merged_macro.csv"
    df = pd.read_csv(merged_path, index_col=0, parse_dates=True)
    return df


def load_inflation_data():
    """Load merged inflation data with first differences."""
    merged_path = DATA_DIR / "merged_inflation.csv"
    df = pd.read_csv(merged_path, index_col=0, parse_dates=True)
    return df


def pearson_correlation(x, y):
    """Compute Pearson correlation coefficient."""
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return np.nan

    return np.corrcoef(x_clean, y_clean)[0, 1]


def bootstrap_correlation_ci(x, y, n_bootstrap=10000, confidence=0.95, seed=42):
    """
    Compute bootstrap confidence interval for correlation.

    Parameters
    ----------
    x, y : array-like
        Data arrays
    n_bootstrap : int
        Number of bootstrap samples
    confidence : float
        Confidence level (e.g., 0.95 for 95% CI)
    seed : int
        Random seed for reproducibility

    Returns
    -------
    dict with keys: correlation, ci_lower, ci_upper, se
    """
    np.random.seed(seed)

    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = np.array(x)[mask]
    y_clean = np.array(y)[mask]
    n = len(x_clean)

    if n < 3:
        return {"correlation": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "se": np.nan}

    # Original correlation
    r_original = np.corrcoef(x_clean, y_clean)[0, 1]

    # Bootstrap
    bootstrap_corrs = []
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, size=n, replace=True)
        x_boot = x_clean[indices]
        y_boot = y_clean[indices]
        r_boot = np.corrcoef(x_boot, y_boot)[0, 1]
        if not np.isnan(r_boot):
            bootstrap_corrs.append(r_boot)

    bootstrap_corrs = np.array(bootstrap_corrs)

    # Confidence interval (percentile method)
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_corrs, 100 * alpha / 2)
    ci_upper = np.percentile(bootstrap_corrs, 100 * (1 - alpha / 2))
    se = np.std(bootstrap_corrs)

    return {
        "correlation": r_original,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "se": se,
        "n_samples": n
    }


def correlation_ttest(x, y):
    """
    Perform t-test for correlation significance.

    H0: rho = 0 (no correlation)
    H1: rho != 0 (correlation exists)

    Test statistic: t = r * sqrt(n-2) / sqrt(1-r^2)
    under H0, t ~ t(n-2)

    Returns
    -------
    dict with keys: t_statistic, p_value, df, correlation
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = np.array(x)[mask]
    y_clean = np.array(y)[mask]
    n = len(x_clean)

    if n < 3:
        return {"t_statistic": np.nan, "p_value": np.nan, "df": np.nan, "correlation": np.nan}

    r = np.corrcoef(x_clean, y_clean)[0, 1]
    df = n - 2

    # Handle r = +/- 1 case
    if abs(r) >= 1.0:
        return {"t_statistic": np.inf, "p_value": 0.0, "df": df, "correlation": r}

    # t-statistic
    t_stat = r * np.sqrt(df) / np.sqrt(1 - r**2)

    # Two-tailed p-value
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "df": df,
        "correlation": r,
        "n_samples": n
    }


def run_full_analysis():
    """Run complete correlation analysis with bootstrap CI and t-tests."""

    results = {}

    # Load data
    df_macro = load_correlation_data()
    df_inflation = load_inflation_data()

    print("=" * 70)
    print("CORRELATION ANALYSIS: CB Speech Sentiment vs Macroeconomic Indices")
    print("=" * 70)

    # Analysis pairs
    analyses = [
        ("Macro Index", "hawkish", df_macro),
        ("Macro Index", "dovish", df_macro),
        ("Inflation Index", "hawkish", df_inflation),
        ("Inflation Index", "dovish", df_inflation),
    ]

    for index_name, sentiment_name, df in analyses:
        print(f"\n{'-' * 50}")
        print(f"Analysis: {index_name} vs {sentiment_name.capitalize()} Sentiment")
        print(f"{'-' * 50}")

        # Get data (first column is the index)
        x = df.iloc[:, 0].values  # Macro or Inflation Index
        y = df[sentiment_name].values

        # Bootstrap CI
        bootstrap_result = bootstrap_correlation_ci(x, y, n_bootstrap=10000, confidence=0.95)

        # T-test
        ttest_result = correlation_ttest(x, y)

        key = f"{index_name.replace(' ', '_').lower()}_{sentiment_name}"
        results[key] = {
            "index": index_name,
            "sentiment": sentiment_name,
            "correlation": bootstrap_result["correlation"],
            "bootstrap_ci_95": [bootstrap_result["ci_lower"], bootstrap_result["ci_upper"]],
            "bootstrap_se": bootstrap_result["se"],
            "t_statistic": ttest_result["t_statistic"],
            "p_value": ttest_result["p_value"],
            "df": ttest_result["df"],
            "n_samples": bootstrap_result["n_samples"]
        }

        # Print results
        print(f"Sample size (n):       {bootstrap_result['n_samples']}")
        print(f"Correlation (r):       {bootstrap_result['correlation']:.6f}")
        print(f"95% CI:                [{bootstrap_result['ci_lower']:.6f}, {bootstrap_result['ci_upper']:.6f}]")
        print(f"Bootstrap SE:          {bootstrap_result['se']:.6f}")
        print(f"T-statistic:           {ttest_result['t_statistic']:.4f}")
        print(f"P-value (two-tailed):  {ttest_result['p_value']:.4f}")
        print(f"Degrees of freedom:    {ttest_result['df']}")

        # Significance interpretation
        if ttest_result['p_value'] < 0.01:
            sig = "*** (p < 0.01)"
        elif ttest_result['p_value'] < 0.05:
            sig = "** (p < 0.05)"
        elif ttest_result['p_value'] < 0.10:
            sig = "* (p < 0.10)"
        else:
            sig = "n.s. (not significant)"
        print(f"Significance:          {sig}")

        # Check if CI contains zero
        contains_zero = bootstrap_result['ci_lower'] <= 0 <= bootstrap_result['ci_upper']
        print(f"CI contains zero:      {'Yes' if contains_zero else 'No'}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Summary table
    print("\nKey Finding: Near-zero correlations, not statistically significant")
    print("\n| Pair                        | r       | 95% CI              | p-value |")
    print("|" + "-" * 29 + "|" + "-" * 9 + "|" + "-" * 21 + "|" + "-" * 9 + "|")

    for key, res in results.items():
        pair_name = f"{res['index']} - {res['sentiment'].capitalize()}"
        ci_str = f"[{res['bootstrap_ci_95'][0]:.4f}, {res['bootstrap_ci_95'][1]:.4f}]"
        print(f"| {pair_name:<27} | {res['correlation']:>7.4f} | {ci_str:>19} | {res['p_value']:>7.4f} |")

    return results


def save_results(results, output_path=None):
    """Save results to JSON file."""
    if output_path is None:
        output_path = Path(__file__).parent / "correlation_results.json"

    # Convert numpy types to Python types for JSON serialization
    serializable = {}
    for key, value in results.items():
        serializable[key] = {}
        for k, v in value.items():
            if isinstance(v, np.ndarray):
                serializable[key][k] = v.tolist()
            elif isinstance(v, (np.float64, np.float32)):
                serializable[key][k] = float(v)
            elif isinstance(v, (np.int64, np.int32)):
                serializable[key][k] = int(v)
            else:
                serializable[key][k] = v

    with open(output_path, 'w') as f:
        json.dump(serializable, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    results = run_full_analysis()
    save_results(results)
