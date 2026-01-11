"""
Chart saving utilities for CB Speeches visualization.

Provides standardized chart saving with proper settings for publication.
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def save_chart(
    fig: Optional[plt.Figure] = None,
    filename: str = "chart.pdf",
    output_dir: Optional[Path] = None,
    dpi: int = 300,
    transparent: bool = False,
    close: bool = True,
    add_source: bool = True,
    source_text: str = "Source: FRED, BIS",
) -> Path:
    """
    Save a chart to PDF with standardized settings.

    Parameters
    ----------
    fig : plt.Figure, optional
        Figure to save. Uses current figure if not provided.
    filename : str
        Output filename (default: 'chart.pdf')
    output_dir : Path, optional
        Output directory. Uses the directory of the calling script if not provided.
    dpi : int
        Resolution for raster elements (default: 300)
    transparent : bool
        Whether to use transparent background (default: False)
    close : bool
        Whether to close the figure after saving (default: True)
    add_source : bool
        Whether to add source attribution (default: True)
    source_text : str
        Source attribution text

    Returns
    -------
    Path
        Path to the saved file
    """
    if fig is None:
        fig = plt.gcf()

    # Determine output directory
    if output_dir is None:
        # Use current working directory
        output_dir = Path.cwd()

    output_path = output_dir / filename

    # Add source attribution if requested
    if add_source and source_text:
        # Add source text in bottom right corner
        fig.text(
            0.99, 0.01,
            source_text,
            ha='right', va='bottom',
            fontsize=8,
            color='#666666',
            transform=fig.transFigure,
            style='italic',
        )

    # Apply tight layout to ensure nothing is cut off
    try:
        fig.tight_layout()
    except Exception:
        # tight_layout can fail with some complex layouts
        pass

    # Save the figure
    fig.savefig(
        output_path,
        dpi=dpi,
        bbox_inches='tight',
        pad_inches=0.1,
        facecolor='white' if not transparent else 'none',
        edgecolor='none',
    )

    logger.info(f"Saved chart to {output_path}")

    if close:
        plt.close(fig)

    return output_path


def save_to_script_dir(
    fig: Optional[plt.Figure] = None,
    script_path: str = __file__,
    filename: str = "chart.pdf",
    **kwargs,
) -> Path:
    """
    Save a chart to the same directory as the calling script.

    This is the recommended way to save charts, as it keeps
    each chart.pdf next to its chart.py script.

    Parameters
    ----------
    fig : plt.Figure, optional
        Figure to save
    script_path : str
        Path to the calling script (__file__)
    filename : str
        Output filename
    **kwargs
        Additional arguments passed to save_chart

    Returns
    -------
    Path
        Path to the saved file

    Example
    -------
    >>> from utils import save_to_script_dir
    >>> fig, ax = plt.subplots()
    >>> # ... create chart ...
    >>> save_to_script_dir(fig, __file__)
    """
    output_dir = Path(script_path).parent
    return save_chart(fig, filename, output_dir, **kwargs)
