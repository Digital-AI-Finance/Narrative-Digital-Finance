"""Combined Inflation Index and CB Sentiment - Dual-axis visualization"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, load_data, load_breakpoints, save_to_script_dir

apply_style()


def main():
    # Load data
    pca_df = load_data('pca_components.csv')
    sentiment = load_data('sentiment_aggregated.csv')

    # Load breakpoints
    breakpoints = load_breakpoints()
    break_dates = [pd.to_datetime(d) for d in breakpoints['inflation_index']['dates']]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot inflation index on primary axis
    ax1.plot(pca_df.index, pca_df['PC2'], label='Inflation Index',
             color=get_color('inflation'), linewidth=1.5)

    # Plot breakpoints
    for date in break_dates:
        ax1.axvline(x=date, color=get_color('gray_medium'), linestyle='--', linewidth=0.8, alpha=0.5)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Inflation Index (PC2)', color=get_color('inflation'))
    ax1.tick_params(axis='y', labelcolor=get_color('inflation'))

    # Create secondary axis for sentiment
    ax2 = ax1.twinx()

    # Align sentiment to PCA dates
    sentiment_aligned = sentiment.reindex(pca_df.index, method='ffill').dropna()

    ax2.plot(sentiment_aligned.index, sentiment_aligned['hawkish'],
             label='Hawkishness', color=get_color('hawkish'), linewidth=1, alpha=0.8)
    ax2.plot(sentiment_aligned.index, sentiment_aligned['dovish'],
             label='Dovishness', color=get_color('dovish'), linewidth=1, alpha=0.8)

    ax2.set_ylabel('Sentiment Score (standardized)', color=get_color('policy'))
    ax2.tick_params(axis='y', labelcolor=get_color('policy'))

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

    ax1.set_title('Inflation Index with CB Speech Sentiment')
    ax1.grid(True, alpha=0.3)

    save_to_script_dir(fig, __file__, source_text="Source: FRED, BIS")


if __name__ == '__main__':
    main()
