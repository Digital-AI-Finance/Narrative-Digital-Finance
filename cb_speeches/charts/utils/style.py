"""
Shared matplotlib style configuration for CB Speeches charts.

All charts use these standardized rcParams for consistency.
Font sizes are scaled up 1.4x for Beamer slides (displayed at 55-65% width).
"""

import matplotlib.pyplot as plt
from typing import Dict, Any

# Standardized rcParams for all charts
# Scaled for Beamer slides displayed at ~60% width
RCPARAMS: Dict[str, Any] = {
    # Font sizes (scaled up for slide readability)
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,

    # Figure settings
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'figure.facecolor': 'white',

    # Axes settings
    'axes.facecolor': 'white',
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.grid': False,
    'axes.spines.top': False,
    'axes.spines.right': False,

    # Grid settings (when enabled)
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,

    # Legend settings
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '#cccccc',

    # Line settings
    'lines.linewidth': 1.5,
    'lines.markersize': 6,

    # Save settings
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'savefig.facecolor': 'white',

    # PDF settings
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
}


def apply_style() -> None:
    """
    Apply the standardized style to matplotlib.

    Call this at the beginning of each chart script to ensure
    consistent styling across all visualizations.

    Example
    -------
    >>> from utils import apply_style
    >>> apply_style()
    >>> fig, ax = plt.subplots()
    """
    plt.rcParams.update(RCPARAMS)


def get_rcparams() -> Dict[str, Any]:
    """
    Get a copy of the standard rcParams dictionary.

    Returns
    -------
    Dict[str, Any]
        Copy of the rcParams configuration
    """
    return RCPARAMS.copy()
