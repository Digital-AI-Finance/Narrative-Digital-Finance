"""Principal Components Over Time - PC1 (Macro Strength) and PC2 (Inflation)"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, load_data, save_to_script_dir

apply_style()


def main():
    df = load_data('pca_components.csv')

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df.index, df['PC1'], label='PC1 (Macro Strength Index)',
            color=get_color('macro'), linewidth=1.5)
    ax.plot(df.index, df['PC2'], label='PC2 (Inflation Index)',
            color=get_color('inflation'), linewidth=1.5)

    ax.set_xlabel('Date')
    ax.set_ylabel('Principal Component Value')
    ax.set_title('First Two Principal Components Over Time')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    save_to_script_dir(fig, __file__, source_text="Source: FRED")


if __name__ == '__main__':
    main()
