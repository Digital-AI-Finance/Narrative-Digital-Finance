"""Macro Strength Index with PELT Structural Breakpoints"""
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
    macro_index = df['PC1']

    # Load breakpoints
    breakpoints = load_breakpoints()
    break_dates = [pd.to_datetime(d) for d in breakpoints['macro_index']['dates']]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(macro_index.index, macro_index.values, label='Macro Strength Index (PC1)',
            color=get_color('macro'), linewidth=1.5)

    # Plot breakpoints
    for i, date in enumerate(break_dates):
        label = 'Structural Breakpoints' if i == 0 else None
        ax.axvline(x=date, color=get_color('breakpoint'), linestyle='--', linewidth=1, label=label)
        y_pos = macro_index.min() - 0.5
        ax.text(date, y_pos, date.strftime('%Y-%m'), rotation=90, ha='center',
                va='top', fontsize=9, color=get_color('breakpoint'))

    ax.set_xlabel('Date')
    ax.set_ylabel('Macro Strength Index')
    ax.set_title('Macro Strength Index with Structural Breakpoints (PELT)')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    save_to_script_dir(fig, __file__, source_text="Source: FRED")


if __name__ == '__main__':
    main()
