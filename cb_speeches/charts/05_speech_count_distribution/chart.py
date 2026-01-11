"""Monthly Speech Count Distribution - US Federal Reserve speeches over time"""
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import apply_style, get_color, save_to_script_dir

apply_style()


def main():
    # Load speech data directly from parquet (not in data folder)
    base_dir = Path(__file__).parent.parent.parent
    speeches = pd.read_parquet(base_dir / 'gigando_speeches_ner_v2.parquet')
    speeches.set_index('datetime', inplace=True)
    speeches = speeches[speeches['country_code'] == 'US']

    # Monthly counts
    monthly_counts = speeches.resample('ME').size()

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(monthly_counts.index, monthly_counts.values, width=25,
           color=get_color('primary'), alpha=0.7)

    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Speeches')
    ax.set_title('Monthly Distribution of US Federal Reserve Speeches')
    ax.grid(True, alpha=0.3, axis='y')

    # Add summary stats
    total = monthly_counts.sum()
    avg = monthly_counts.mean()
    ax.text(0.98, 0.95, f'Total: {total:,} speeches\nAvg: {avg:.1f}/month',
            transform=ax.transAxes, ha='right', va='top', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    save_to_script_dir(fig, __file__, source_text="Source: BIS")


if __name__ == '__main__':
    main()
