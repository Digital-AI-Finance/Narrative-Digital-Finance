"""
Data preprocessing utilities for rolling standardization.
"""
import pandas as pd
import numpy as np
from typing import Optional, List
import logging

from .config import ROLLING_WINDOW

logger = logging.getLogger(__name__)


def rolling_standardize(
    df: pd.DataFrame,
    window: int = ROLLING_WINDOW,
    min_periods: Optional[int] = None,
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Apply rolling window standardization (z-score normalization).

    Formula: (x - rolling_mean) / rolling_std

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with numeric columns
    window : int
        Rolling window size in periods (default: 12 months)
    min_periods : int, optional
        Minimum periods for valid calculation. Defaults to window size.
    drop_na : bool
        Whether to drop NaN values after transformation

    Returns
    -------
    pd.DataFrame
        Standardized DataFrame
    """
    # Input validation
    if df.empty:
        raise ValueError('Input DataFrame cannot be empty')
    if window <= 0:
        raise ValueError('Window size must be positive')

    if min_periods is None:
        min_periods = window

    logger.info(f'Applying rolling standardization with window={window}')
    rolling_mean = df.rolling(window=window, min_periods=min_periods).mean()
    rolling_std = df.rolling(window=window, min_periods=min_periods).std()

    # Avoid division by zero
    rolling_std = rolling_std.replace(0, np.nan)

    scaled_df = (df - rolling_mean) / rolling_std

    if drop_na:
        scaled_df = scaled_df.dropna()

    return scaled_df


def first_difference(df: pd.DataFrame, drop_na: bool = True) -> pd.DataFrame:
    """
    Compute first differences of a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    drop_na : bool
        Whether to drop NaN values

    Returns
    -------
    pd.DataFrame
        First-differenced DataFrame
    """
    # Input validation
    if df.empty:
        raise ValueError('Input DataFrame cannot be empty')

    diff_df = df.diff()

    if drop_na:
        diff_df = diff_df.dropna()

    return diff_df


def align_dataframes(*dfs: pd.DataFrame, how: str = "inner") -> list:
    """
    Align multiple DataFrames to common index.

    Parameters
    ----------
    *dfs : pd.DataFrame
        DataFrames to align
    how : str
        Join method ('inner', 'outer')

    Returns
    -------
    list
        List of aligned DataFrames
    """
    if len(dfs) < 2:
        return list(dfs)

    # Input validation
    for i, df in enumerate(dfs):
        if df.empty:
            logger.warning(f'DataFrame at position {i} is empty')

    # Get common index
    if how == "inner":
        common_idx = dfs[0].index
        for df in dfs[1:]:
            common_idx = common_idx.intersection(df.index)
    else:  # outer
        common_idx = dfs[0].index
        for df in dfs[1:]:
            common_idx = common_idx.union(df.index)

    common_idx = common_idx.sort_values()

    return [df.reindex(common_idx) for df in dfs]


if __name__ == "__main__":
    # Test preprocessing
    import numpy as np

    # Create test data
    dates = pd.date_range("2020-01-01", periods=100, freq="M")
    data = pd.DataFrame(
        {
            "A": np.random.randn(100).cumsum(),
            "B": np.random.randn(100).cumsum(),
        },
        index=dates,
    )

    print("Original data:")
    print(data.head(15))

    print("\nStandardized data:")
    scaled = rolling_standardize(data, window=12)
    print(scaled.head())
    print(f"\nMean of standardized data: {scaled.mean().round(3).to_dict()}")
    print(f"Std of standardized data: {scaled.std().round(3).to_dict()}")
