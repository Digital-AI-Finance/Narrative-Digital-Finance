"""Rolling Betas vs Inflation Index - Hawkish and Dovish sentiment betas"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, load_data, save_to_script_dir

apply_style()


def main():
    df = load_data('rolling_results_inflation.csv')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df.index, df['hawkish_beta'], label='Hawkishness Beta',
            color=get_color('hawkish'), linewidth=1.2)
    ax.plot(df.index, df['dovish_beta'], label='Dovishness Beta',
            color=get_color('dovish'), linewidth=1.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Rolling Beta Coefficient')
    ax.set_title('Rolling Betas: CB Sentiment vs Inflation Index (36-month window)')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # Add annotation
    ax.text(0.98, 0.02, 'Note: Weak and fluctuating betas\nsuggest limited predictive relationship',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    save_to_script_dir(fig, __file__, source_text="Source: FRED, BIS")


if __name__ == '__main__':
    main()
