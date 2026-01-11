"""PCA Loadings Heatmap - Component weights on original variables"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_diverging_cmap, load_data, save_to_script_dir

apply_style()


def main():
    loadings = load_data('pca_loadings.csv')

    # Separate loadings from explained variance
    var_explained = loadings['Explained Variance']
    loadings_only = loadings.drop(columns=['Explained Variance'])

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create heatmap with colorblind-safe diverging colormap
    sns.heatmap(loadings_only, annot=True, fmt='.1f', cmap=get_diverging_cmap(), center=0,
                vmin=-100, vmax=100, ax=ax, annot_kws={'size': 11},
                linewidths=0.5, cbar_kws={'label': 'Loading (%)'})

    # Add variance explained as text on right side
    for i, (pc, var) in enumerate(var_explained.items()):
        ax.text(len(loadings_only.columns) + 0.5, i + 0.5, f'{var:.1f}%',
                ha='left', va='center', fontsize=11, fontweight='bold')

    ax.text(len(loadings_only.columns) + 0.5, -0.5, 'Var. Exp.',
            ha='left', va='bottom', fontsize=10, fontweight='bold')

    ax.set_title('PCA Loadings: Component Weights on Macroeconomic Variables')
    ax.set_xlabel('Macroeconomic Variable')
    ax.set_ylabel('Principal Component')

    save_to_script_dir(fig, __file__, source_text="Source: FRED")


if __name__ == '__main__':
    main()
