"""Correlation Matrix Heatmap - Macro/Inflation Index vs Sentiment"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_diverging_cmap, load_data, save_to_script_dir

apply_style()


def main():
    # Load all data
    pca_df = load_data('pca_components.csv')
    sentiment = load_data('sentiment_aggregated.csv')

    # Merge and compute correlation
    merged = pd.merge(
        pca_df[['PC1', 'PC2']].rename(columns={'PC1': 'Macro Index', 'PC2': 'Inflation Index'}),
        sentiment,
        left_index=True, right_index=True, how='outer'
    ).ffill().dropna()

    # First differences for correlation
    merged_diff = merged.diff().dropna()
    corr = merged_diff.corr()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Create heatmap
    sns.heatmap(corr, annot=True, fmt='.3f', cmap=get_diverging_cmap(), center=0,
                vmin=-1, vmax=1, square=True, ax=ax,
                annot_kws={'size': 11}, linewidths=0.5)

    ax.set_title('Correlation Matrix: Macro Indices vs CB Sentiment\n(First Differences)')

    save_to_script_dir(fig, __file__, source_text="Source: FRED, BIS")


if __name__ == '__main__':
    main()
