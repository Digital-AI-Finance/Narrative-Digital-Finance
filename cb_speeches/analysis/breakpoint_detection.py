"""
Structural breakpoint detection using PELT algorithm.
"""
import pandas as pd
import numpy as np
import ruptures as rpt
from typing import List, Tuple, Dict
import json
import logging

from .config import PELT_PENALTY

logger = logging.getLogger(__name__)


def detect_breakpoints(
    series: pd.Series,
    penalty: float = PELT_PENALTY,
    model: str = "rbf",
    min_size: int = 2,
) -> Tuple[List[int], List[pd.Timestamp]]:
    """
    Detect structural breakpoints using PELT algorithm.

    Parameters
    ----------
    series : pd.Series
        Time series data (must have datetime index)
    penalty : float
        Penalty parameter controlling number of breaks (higher = fewer breaks)
    model : str
        Cost model for PELT ('rbf', 'l1', 'l2', 'linear', etc.)
    min_size : int
        Minimum segment length

    Returns
    -------
    Tuple[List[int], List[pd.Timestamp]]
        - List of break indices
        - List of break dates
    """
    # Input validation
    if series.empty:
        raise ValueError('Input series cannot be empty')
    if not isinstance(series.index, pd.DatetimeIndex):
        logger.warning('Series index is not DatetimeIndex, results may be unexpected')

    # Fit PELT algorithm
    logger.info(f'Detecting breakpoints with penalty={penalty}, model={model}')
    algo = rpt.Pelt(model=model, min_size=min_size).fit(series.values)

    # Predict breakpoints (exclude the last one which is just the end)
    breaks = algo.predict(pen=penalty)[:-1]

    # Convert indices to dates
    break_dates = [series.index[i - 1] for i in breaks]

    return breaks, break_dates


def detect_multiple_breakpoints(
    data: Dict[str, pd.Series],
    penalty: float = PELT_PENALTY,
    model: str = "rbf",
) -> Dict[str, Dict]:
    """
    Detect breakpoints for multiple series.

    Parameters
    ----------
    data : Dict[str, pd.Series]
        Dictionary mapping names to series
    penalty : float
        Penalty parameter for PELT
    model : str
        Cost model for PELT

    Returns
    -------
    Dict[str, Dict]
        Dictionary with breakpoint info for each series
    """
    results = {}

    for name, series in data.items():
        breaks, break_dates = detect_breakpoints(series, penalty=penalty, model=model)
        results[name] = {
            "indices": breaks,
            "dates": [d.isoformat() if hasattr(d, 'isoformat') else str(d) for d in break_dates],
            "n_breaks": len(breaks),
        }

    return results


def save_breakpoints(breakpoints: Dict, filepath: str) -> None:
    """
    Save breakpoints to JSON file.

    Parameters
    ----------
    breakpoints : Dict
        Breakpoint results from detect_multiple_breakpoints
    filepath : str
        Output file path
    """
    with open(filepath, "w") as f:
        json.dump(breakpoints, f, indent=2)
    logger.info(f'Saved breakpoints to {filepath}')


def load_breakpoints(filepath: str) -> Dict:
    """
    Load breakpoints from JSON file.

    Parameters
    ----------
    filepath : str
        Input file path

    Returns
    -------
    Dict
        Breakpoint data
    """
    with open(filepath, "r") as f:
        return json.load(f)


def get_regime_periods(
    series: pd.Series,
    break_dates: List[pd.Timestamp],
) -> pd.DataFrame:
    """
    Get regime periods based on breakpoints.

    Parameters
    ----------
    series : pd.Series
        Original time series
    break_dates : List[pd.Timestamp]
        List of breakpoint dates

    Returns
    -------
    pd.DataFrame
        DataFrame with regime info (start, end, mean, std)
    """
    all_dates = [series.index[0]] + break_dates + [series.index[-1]]

    regimes = []
    for i in range(len(all_dates) - 1):
        start = all_dates[i]
        end = all_dates[i + 1]
        segment = series.loc[start:end]

        regimes.append({
            "Regime": i + 1,
            "Start": start,
            "End": end,
            "Duration (months)": len(segment),
            "Mean": segment.mean(),
            "Std": segment.std(),
        })

    return pd.DataFrame(regimes)


if __name__ == "__main__":
    # Test breakpoint detection
    np.random.seed(42)

    # Create test data with regime changes
    dates = pd.date_range("2000-01-01", periods=300, freq="M")

    # Create data with clear regime changes
    data = np.concatenate([
        np.random.randn(100) + 0,    # Regime 1
        np.random.randn(100) + 3,    # Regime 2
        np.random.randn(100) - 2,    # Regime 3
    ])

    series = pd.Series(data, index=dates, name="Test Series")

    print("Detecting breakpoints...")
    breaks, break_dates = detect_breakpoints(series, penalty=4)

    print(f"\nFound {len(breaks)} breakpoints:")
    for date in break_dates:
        print(f"  - {date.strftime('%Y-%m-%d')}")

    print("\nRegime periods:")
    regimes = get_regime_periods(series, break_dates)
    print(regimes)
