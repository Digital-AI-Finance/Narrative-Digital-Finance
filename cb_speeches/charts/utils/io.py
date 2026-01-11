"""
Data loading utilities for CB Speeches charts.

Provides standardized data loading with error handling and path resolution.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Data directory relative to project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = _PROJECT_ROOT / "cb_speeches" / "data"


def get_data_path(filename: str) -> Path:
    """
    Get the full path to a data file.

    Parameters
    ----------
    filename : str
        Name of the data file (e.g., 'pca_components.csv')

    Returns
    -------
    Path
        Full path to the data file
    """
    return DATA_DIR / filename


def load_data(
    filename: str,
    index_col: Optional[int] = 0,
    parse_dates: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load a CSV data file with standardized settings.

    Parameters
    ----------
    filename : str
        Name of the data file (e.g., 'pca_components.csv')
    index_col : int, optional
        Column to use as index (default: 0)
    parse_dates : bool
        Whether to parse dates in the index (default: True)
    **kwargs
        Additional arguments passed to pd.read_csv

    Returns
    -------
    pd.DataFrame
        Loaded data

    Raises
    ------
    FileNotFoundError
        If the data file does not exist
    """
    filepath = get_data_path(filename)

    if not filepath.exists():
        raise FileNotFoundError(
            f"Data file not found: {filepath}\n"
            f"Run the analysis pipeline first: python -m cb_speeches.analysis.run_all"
        )

    try:
        df = pd.read_csv(
            filepath,
            index_col=index_col,
            parse_dates=parse_dates,
            **kwargs,
        )
        logger.debug(f"Loaded {len(df)} rows from {filename}")
        return df
    except Exception as e:
        logger.error(f"Failed to load {filename}: {e}")
        raise


def load_breakpoints(filename: str = "breakpoints.json") -> Dict[str, Any]:
    """
    Load breakpoint data from JSON.

    Parameters
    ----------
    filename : str
        Name of the breakpoints file

    Returns
    -------
    Dict[str, Any]
        Breakpoint data
    """
    import json

    filepath = get_data_path(filename)

    if not filepath.exists():
        raise FileNotFoundError(f"Breakpoints file not found: {filepath}")

    with open(filepath, 'r') as f:
        return json.load(f)


def get_available_data_files() -> list:
    """
    List all available data files.

    Returns
    -------
    list
        List of available data file names
    """
    if not DATA_DIR.exists():
        return []
    return [f.name for f in DATA_DIR.glob("*.csv")]
