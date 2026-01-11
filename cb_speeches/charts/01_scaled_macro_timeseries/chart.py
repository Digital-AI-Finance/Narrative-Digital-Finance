"""Scaled Macroeconomic Data Time Series - Rolling 12-month standardized indicators"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

# Add parent directories to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_colorblind_palette, load_data, save_to_script_dir

# Apply consistent style
apply_style()


def main():
    # Load processed macro data using utility
    df = load_data('processed_macro.csv')

    # Get colorblind-safe palette
    colors = get_colorblind_palette(6)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, col in enumerate(df.columns):
        ax.plot(df.index, df[col], label=col, color=colors[i % len(colors)], linewidth=1.2)

    ax.set_xlabel('Date')
    ax.set_ylabel('Standardized Value (z-score)')
    ax.set_title('Scaled Macroeconomic Data (12-month rolling window)')
    ax.legend(loc='upper left', ncol=2, fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # Save using utility
    save_to_script_dir(fig, __file__, source_text="Source: FRED")


if __name__ == '__main__':
    main()
