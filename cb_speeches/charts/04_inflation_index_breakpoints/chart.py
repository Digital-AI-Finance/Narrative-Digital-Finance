"""Inflation Index with PELT Structural Breakpoints"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, load_data, load_breakpoints, save_to_script_dir

apply_style()


def main():
    # Load PCA components
    df = load_data('pca_components.csv')
    inflation_index = df['PC2']

    # Load breakpoints
    breakpoints = load_breakpoints()
    break_dates = [pd.to_datetime(d) for d in breakpoints['inflation_index']['dates']]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(inflation_index.index, inflation_index.values, label='Inflation Index (PC2)',
            color=get_color('inflation'), linewidth=1.5)

    # Plot breakpoints
    for i, date in enumerate(break_dates):
        label = 'Structural Breakpoints' if i == 0 else None
        ax.axvline(x=date, color=get_color('breakpoint'), linestyle='--', linewidth=1, label=label)
        y_pos = inflation_index.min() - 0.3
        ax.text(date, y_pos, date.strftime('%Y-%m'), rotation=90, ha='center',
                va='top', fontsize=8, color=get_color('breakpoint'))

    ax.set_xlabel('Date')
    ax.set_ylabel('Inflation Index')
    ax.set_title('Inflation Index with Structural Breakpoints (PELT)')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    save_to_script_dir(fig, __file__, source_text="Source: FRED")


if __name__ == '__main__':
    main()
