"""
Precompute all analysis results and save to JSON inventory + CSV files.
Run this script to generate cached data for fast Streamlit loading.
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from analysis.config import (
    DATA_DIR, START_DATE, END_DATE, FRED_SERIES,
)
from analysis.data_loader import load_cached_macro
from analysis.preprocessing import rolling_standardize
from analysis.pca_analysis import fit_pca, get_loadings, get_variance_explained
from analysis.breakpoint_detection import detect_breakpoints
from analysis.speech_sentiment import load_us_speeches, aggregate_monthly_sentiment, get_sentiment_summary
from analysis.rolling_regression import compute_rolling_analysis, compute_correlation_matrix

# Default parameters
ROLLING_WINDOW = 12
REGRESSION_WINDOW = 36
PELT_PENALTY = 4

# Output directory
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(exist_ok=True)


def save_csv(df: pd.DataFrame, name: str) -> str:
    """Save DataFrame to CSV and return filename."""
    filename = f"{name}.csv"
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath)
    print(f"  Saved: {filename}")
    return filename


def compute_regime_stats(series: pd.Series, break_indices: list) -> list:
    """Compute statistics for each regime."""
    regime_stats = []
    indices = [0] + list(break_indices) + [len(series)]

    for i in range(len(indices) - 1):
        segment = series.iloc[indices[i]:indices[i+1]]
        if len(segment) > 0:
            regime_stats.append({
                'regime': i + 1,
                'start_idx': indices[i],
                'end_idx': indices[i+1],
                'start_date': segment.index[0].strftime('%Y-%m-%d'),
                'end_date': segment.index[-1].strftime('%Y-%m-%d'),
                'n_observations': len(segment),
                'mean': float(segment.mean()),
                'std': float(segment.std()),
                'min': float(segment.min()),
                'max': float(segment.max())
            })

    return regime_stats


def main():
    """Run full pipeline and save all results."""
    print("=" * 60)
    print("PRECOMPUTING CB SPEECHES ANALYSIS")
    print("=" * 60)
    start_time = datetime.now()

    inventory = {
        'metadata': {
            'created': start_time.isoformat(),
            'parameters': {
                'rolling_window': ROLLING_WINDOW,
                'regression_window': REGRESSION_WINDOW,
                'pelt_penalty': PELT_PENALTY,
                'start_date': START_DATE,
                'end_date': END_DATE
            },
            'fred_series': FRED_SERIES
        },
        'data_files': {},
        'summary_stats': {},
        'breakpoints': {},
        'eigenvalues': [],
        'variance_explained': {},
        'sentiment_summary': {},
        'regime_stats': {},
        'descriptive_stats': {}
    }

    # Step 1: Load macro data
    print("\n[1/6] Loading macroeconomic data...")
    macro_data = load_cached_macro()
    inventory['data_files']['raw_macro'] = save_csv(macro_data, 'raw_macro')
    inventory['summary_stats']['n_macro_observations'] = len(macro_data)
    inventory['descriptive_stats']['raw_macro'] = macro_data.describe().to_dict()

    # Step 2: Rolling standardization
    print("\n[2/6] Computing rolling standardization...")
    scaled_data = rolling_standardize(macro_data, window=ROLLING_WINDOW)
    rolling_mean = macro_data.rolling(window=ROLLING_WINDOW).mean()
    rolling_std = macro_data.rolling(window=ROLLING_WINDOW).std()

    inventory['data_files']['scaled_macro'] = save_csv(scaled_data, 'scaled_macro')
    inventory['data_files']['rolling_mean'] = save_csv(rolling_mean, 'rolling_mean')
    inventory['data_files']['rolling_std'] = save_csv(rolling_std, 'rolling_std')
    inventory['descriptive_stats']['scaled_macro'] = scaled_data.describe().to_dict()

    # Step 3: PCA
    print("\n[3/6] Running PCA analysis...")
    pca, pca_df = fit_pca(scaled_data)
    loadings = get_loadings(pca, list(macro_data.columns))
    variance_explained = get_variance_explained(pca)

    eigenvectors = pd.DataFrame(
        pca.components_,
        columns=macro_data.columns,
        index=[f'PC{i+1}' for i in range(len(pca.components_))]
    )

    inventory['data_files']['pca_components'] = save_csv(pca_df, 'pca_components')
    inventory['data_files']['pca_loadings'] = save_csv(loadings, 'pca_loadings')
    inventory['data_files']['eigenvectors'] = save_csv(eigenvectors, 'eigenvectors')

    inventory['eigenvalues'] = pca.explained_variance_.tolist()
    inventory['variance_explained'] = {
        'individual': (pca.explained_variance_ratio_ * 100).tolist(),
        'cumulative': (np.cumsum(pca.explained_variance_ratio_) * 100).tolist()
    }
    inventory['summary_stats']['variance_2pcs'] = float(np.cumsum(pca.explained_variance_ratio_)[1] * 100)
    inventory['descriptive_stats']['pca_components'] = pca_df.describe().to_dict()

    macro_index = pca_df['PC1'].rename('Macro Index')
    inflation_index = pca_df['PC2'].rename('Inflation Index')

    # Step 4: Breakpoints
    print("\n[4/6] Detecting structural breakpoints...")
    break_indices_macro, break_dates_macro = detect_breakpoints(macro_index, penalty=PELT_PENALTY)
    break_indices_inflation, break_dates_inflation = detect_breakpoints(inflation_index, penalty=PELT_PENALTY)

    inventory['breakpoints']['macro_index'] = {
        'indices': break_indices_macro,
        'dates': [d.strftime('%Y-%m-%d') for d in break_dates_macro]
    }
    inventory['breakpoints']['inflation_index'] = {
        'indices': break_indices_inflation,
        'dates': [d.strftime('%Y-%m-%d') for d in break_dates_inflation]
    }
    inventory['summary_stats']['n_macro_breakpoints'] = len(break_dates_macro)
    inventory['summary_stats']['n_inflation_breakpoints'] = len(break_dates_inflation)

    # Regime statistics
    inventory['regime_stats']['macro'] = compute_regime_stats(macro_index, break_indices_macro)
    inventory['regime_stats']['inflation'] = compute_regime_stats(inflation_index, break_indices_inflation)

    # Step 5: Speech sentiment
    print("\n[5/6] Processing speech sentiment...")
    speeches = load_us_speeches()
    sentiment_summary = get_sentiment_summary(speeches)

    cb_sentiment = aggregate_monthly_sentiment(
        speeches, START_DATE, END_DATE,
        shift_periods=1, standardize=True, window=ROLLING_WINDOW
    )
    cb_sentiment_raw = aggregate_monthly_sentiment(
        speeches, START_DATE, END_DATE,
        shift_periods=1, standardize=False, window=ROLLING_WINDOW
    )

    inventory['data_files']['sentiment_standardized'] = save_csv(cb_sentiment, 'sentiment_standardized')
    inventory['data_files']['sentiment_raw'] = save_csv(cb_sentiment_raw, 'sentiment_raw')

    # Save speeches summary (not full data - too large for JSON)
    speeches_summary = speeches.reset_index()[['datetime', 'sentiment', 'hawkish', 'dovish']].copy()
    speeches_summary['datetime'] = speeches_summary['datetime'].astype(str)
    inventory['data_files']['speeches_summary'] = save_csv(speeches_summary, 'speeches_summary')

    inventory['summary_stats']['n_speeches'] = len(speeches)
    inventory['summary_stats']['n_monthly_sentiment'] = len(cb_sentiment.dropna())

    # Sentiment breakdown
    hawkish_count = int(sentiment_summary.loc['Hawkish', 'Count'])
    dovish_count = int(sentiment_summary.loc['Dovish', 'Count'])
    neutral_count = int(sentiment_summary.loc['Neutral', 'Count'])
    total = hawkish_count + dovish_count + neutral_count

    inventory['sentiment_summary'] = {
        'hawkish': {'count': hawkish_count, 'pct': round(hawkish_count / total * 100, 2)},
        'dovish': {'count': dovish_count, 'pct': round(dovish_count / total * 100, 2)},
        'neutral': {'count': neutral_count, 'pct': round(neutral_count / total * 100, 2)},
        'total': total
    }
    inventory['descriptive_stats']['sentiment_standardized'] = cb_sentiment.dropna().describe().to_dict()

    # Step 6: Rolling regression
    print("\n[6/6] Computing rolling regressions...")
    merged_macro, betas_macro, r2_macro = compute_rolling_analysis(
        macro_index, cb_sentiment, window=REGRESSION_WINDOW
    )
    merged_inflation, betas_inflation, r2_inflation = compute_rolling_analysis(
        inflation_index, cb_sentiment, window=REGRESSION_WINDOW
    )

    corr_macro = compute_correlation_matrix(merged_macro)
    corr_inflation = compute_correlation_matrix(merged_inflation)

    inventory['data_files']['merged_macro'] = save_csv(merged_macro, 'merged_macro')
    inventory['data_files']['merged_inflation'] = save_csv(merged_inflation, 'merged_inflation')
    inventory['data_files']['betas_macro'] = save_csv(betas_macro, 'betas_macro')
    inventory['data_files']['betas_inflation'] = save_csv(betas_inflation, 'betas_inflation')
    inventory['data_files']['r2_macro'] = save_csv(r2_macro, 'r2_macro')
    inventory['data_files']['r2_inflation'] = save_csv(r2_inflation, 'r2_inflation')
    inventory['data_files']['corr_macro'] = save_csv(corr_macro, 'corr_macro')
    inventory['data_files']['corr_inflation'] = save_csv(corr_inflation, 'corr_inflation')

    # Key correlation stat
    macro_hawkish_corr = float(corr_macro.loc['Macro Index', 'hawkish'])
    inventory['summary_stats']['macro_hawkish_correlation'] = round(macro_hawkish_corr, 4)

    # Correlation matrices as nested dicts
    inventory['correlations'] = {
        'macro': corr_macro.to_dict(),
        'inflation': corr_inflation.to_dict()
    }

    # Save inventory JSON
    print("\n" + "=" * 60)
    print("Saving inventory.json...")
    inventory_path = OUTPUT_DIR / 'inventory.json'
    with open(inventory_path, 'w') as f:
        json.dump(inventory, f, indent=2)
    print(f"  Saved: inventory.json")

    # Summary
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("PRECOMPUTATION COMPLETE")
    print("=" * 60)
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Files created: {len(inventory['data_files']) + 1}")
    print(f"\nKey statistics:")
    print(f"  - Macro observations: {inventory['summary_stats']['n_macro_observations']}")
    print(f"  - Total speeches: {inventory['summary_stats']['n_speeches']}")
    print(f"  - Variance (2 PCs): {inventory['summary_stats']['variance_2pcs']:.1f}%")
    print(f"  - Macro breakpoints: {inventory['summary_stats']['n_macro_breakpoints']}")
    print(f"  - Inflation breakpoints: {inventory['summary_stats']['n_inflation_breakpoints']}")
    print(f"  - Macro-Hawkish correlation: {inventory['summary_stats']['macro_hawkish_correlation']:.4f}")

    return inventory


if __name__ == '__main__':
    inventory = main()
