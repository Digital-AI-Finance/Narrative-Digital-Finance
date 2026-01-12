"""
Granger Causality Tests for CB Speech Sentiment and Macro Indices
=================================================================
Tests whether sentiment Granger-causes macro changes and vice versa.

Author: Statistical analysis for Taibi (2025) paper
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests
from pathlib import Path
import json
import warnings

# Suppress verbose output from grangercausalitytests
warnings.filterwarnings('ignore')

# Data paths
DATA_DIR = Path(__file__).parent.parent.parent / "cb_speeches" / "data"


def load_pca_data():
    """Load PCA components data."""
    pca_path = DATA_DIR / "pca_components.csv"
    df = pd.read_csv(pca_path, index_col=0, parse_dates=True)
    return df


def load_sentiment_data():
    """Load sentiment data."""
    sentiment_path = DATA_DIR / "sentiment_standardized.csv"
    df = pd.read_csv(sentiment_path, index_col=0, parse_dates=True)
    return df


def prepare_granger_data():
    """
    Prepare aligned data for Granger causality tests.
    Returns DataFrame with Macro Index, Inflation Index, hawkish, dovish.
    """
    pca = load_pca_data()
    sentiment = load_sentiment_data()

    # Rename columns
    pca = pca.rename(columns={'PC1': 'Macro_Index', 'PC2': 'Inflation_Index'})

    # Merge on date index
    df = pca[['Macro_Index', 'Inflation_Index']].join(sentiment[['hawkish', 'dovish']], how='inner')

    # Drop rows with any NaN
    df = df.dropna()

    return df


def run_granger_test(data, cause_col, effect_col, max_lag=12):
    """
    Run Granger causality test.

    Parameters
    ----------
    data : DataFrame
        Data containing the time series
    cause_col : str
        Column name for potential cause variable
    effect_col : str
        Column name for effect variable
    max_lag : int
        Maximum number of lags to test

    Returns
    -------
    dict with test results for each lag
    """
    # Prepare data as 2D array: [effect, cause]
    test_data = data[[effect_col, cause_col]].values

    # Run Granger test
    try:
        results = grangercausalitytests(test_data, maxlag=max_lag, verbose=False)
    except Exception as e:
        return {"error": str(e)}

    # Extract F-test results
    output = {}
    for lag in range(1, max_lag + 1):
        if lag in results:
            f_test = results[lag][0]['ssr_ftest']
            output[lag] = {
                'f_statistic': float(f_test[0]),
                'p_value': float(f_test[1]),
                'df_denom': int(f_test[2]),
                'df_num': int(f_test[3])
            }

    return output


def run_bidirectional_granger(data, var1, var2, max_lag=12):
    """
    Run bidirectional Granger causality tests.

    Tests: var1 -> var2 and var2 -> var1

    Returns dict with results for both directions.
    """
    results = {
        f'{var1}_causes_{var2}': run_granger_test(data, var1, var2, max_lag),
        f'{var2}_causes_{var1}': run_granger_test(data, var2, var1, max_lag)
    }
    return results


def summarize_granger_results(results, significance_level=0.05):
    """
    Summarize Granger causality results.

    Returns summary with min p-value and significance across lags.
    """
    summary = {}

    for direction, lag_results in results.items():
        if 'error' in lag_results:
            summary[direction] = {'error': lag_results['error']}
            continue

        # Find minimum p-value across lags
        min_p = 1.0
        min_p_lag = None
        significant_lags = []

        for lag, stats in lag_results.items():
            p = stats['p_value']
            if p < min_p:
                min_p = p
                min_p_lag = lag
            if p < significance_level:
                significant_lags.append(lag)

        summary[direction] = {
            'min_p_value': min_p,
            'min_p_lag': min_p_lag,
            'significant_lags': significant_lags,
            'any_significant': len(significant_lags) > 0,
            'num_lags_tested': len(lag_results)
        }

    return summary


def run_full_granger_analysis(max_lag=12):
    """Run complete Granger causality analysis."""

    print("=" * 70)
    print("GRANGER CAUSALITY ANALYSIS")
    print("=" * 70)
    print(f"Testing bidirectional causality between sentiment and macro indices")
    print(f"Max lags: {max_lag}")
    print()

    # Load and prepare data
    df = prepare_granger_data()
    print(f"Sample size: {len(df)} observations")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print()

    all_results = {}

    # Test pairs
    test_pairs = [
        ('hawkish', 'Macro_Index'),
        ('dovish', 'Macro_Index'),
        ('hawkish', 'Inflation_Index'),
        ('dovish', 'Inflation_Index'),
    ]

    for sentiment, index in test_pairs:
        print("-" * 50)
        print(f"Testing: {sentiment} <-> {index}")
        print("-" * 50)

        results = run_bidirectional_granger(df, sentiment, index, max_lag)
        summary = summarize_granger_results(results)

        all_results[f'{sentiment}_{index}'] = {
            'full_results': results,
            'summary': summary
        }

        # Print summary
        for direction, summ in summary.items():
            if 'error' in summ:
                print(f"  {direction}: ERROR - {summ['error']}")
                continue

            sig_str = "SIGNIFICANT" if summ['any_significant'] else "Not significant"
            print(f"  {direction}:")
            print(f"    Min p-value: {summ['min_p_value']:.4f} at lag {summ['min_p_lag']}")
            print(f"    Significant at 5%: {sig_str}")
            if summ['significant_lags']:
                print(f"    Significant lags: {summ['significant_lags']}")
        print()

    # Overall summary
    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print()
    print("| Direction                              | Min p-value | Sig. at 5% |")
    print("|" + "-" * 40 + "|" + "-" * 13 + "|" + "-" * 12 + "|")

    for pair_key, pair_data in all_results.items():
        for direction, summ in pair_data['summary'].items():
            if 'error' not in summ:
                sig = "Yes" if summ['any_significant'] else "No"
                print(f"| {direction:<38} | {summ['min_p_value']:>11.4f} | {sig:>10} |")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    # Check if any direction is significant
    any_significant = False
    for pair_key, pair_data in all_results.items():
        for direction, summ in pair_data['summary'].items():
            if 'error' not in summ and summ['any_significant']:
                any_significant = True
                break

    if not any_significant:
        print("Key Finding: NO significant Granger causality in either direction.")
        print("Neither sentiment Granger-causes macro indices, nor vice versa.")
        print("This confirms the near-zero contemporaneous correlation finding.")
    else:
        print("Some significant Granger causality relationships detected.")
        print("See detailed results above.")

    return all_results


def save_results(results, output_path=None):
    """Save results to JSON file."""
    if output_path is None:
        output_path = Path(__file__).parent / "granger_results.json"

    # Extract just summaries for cleaner output
    output = {}
    for pair_key, pair_data in results.items():
        output[pair_key] = pair_data['summary']

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    results = run_full_granger_analysis(max_lag=12)
    save_results(results)
