"""Rolling R-squared vs Macro Index - Explanatory power of sentiment"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, load_data, save_to_script_dir

apply_style()


def main():
    df = load_data('rolling_results_macro.csv')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df.index, df['hawkish_r2'], label='Hawkishness R-squared',
            color=get_color('hawkish'), linewidth=1.2)
    ax.plot(df.index, df['dovish_r2'], label='Dovishness R-squared',
            color=get_color('dovish'), linewidth=1.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Rolling R-squared')
    ax.set_title('Rolling R-squared: CB Sentiment vs Macro Strength Index')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, max(0.1, df[['hawkish_r2', 'dovish_r2']].max().max() * 1.2))

    # Add annotation
    mean_r2 = df[['hawkish_r2', 'dovish_r2']].mean().mean()
    ax.text(0.98, 0.95, f'Average R-squared: {mean_r2:.4f}\n(near-zero explanatory power)',
            transform=ax.transAxes, ha='right', va='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    save_to_script_dir(fig, __file__, source_text="Source: FRED, BIS")


if __name__ == '__main__':
    main()
