"""
Data loading utilities for FRED macroeconomic data.
"""
import pandas as pd
from fredapi import Fred
from pathlib import Path
from typing import Optional, Dict, List
import logging

from .config import (
    FRED_API_KEY,
    FRED_SERIES,
    START_DATE,
    END_DATE,
    MACRO_CSV,
)

logger = logging.getLogger(__name__)


def fetch_fred_data(
    start: str = START_DATE,
    end: str = END_DATE,
    api_key: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch macroeconomic data from FRED API.

    Parameters
    ----------
    start : str
        Start date in YYYY-MM-DD format
    end : str
        End date in YYYY-MM-DD format
    api_key : str, optional
        FRED API key. Uses environment variable if not provided.

    Returns
    -------
    pd.DataFrame
        DataFrame with macroeconomic indicators, indexed by date
    """
    if api_key is None:
        api_key = FRED_API_KEY

    if api_key is None:
        raise ValueError(
            "FRED API key not found. Set FRED_API_KEY environment variable "
            "or pass api_key parameter."
        )

    try:
        fred = Fred(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize FRED API: {e}")
        raise RuntimeError(f"FRED API initialization failed: {e}")

    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime("today") if end is None else pd.to_datetime(end)

    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    start_refined = start_date.strftime("%m/%d/%Y")
    end_refined = end_date.strftime("%m/%d/%Y")

    # Fetch each series with error handling
    series_list: List[pd.Series] = []
    failed_series: List[str] = []

    for series_id, series_name in FRED_SERIES.items():
        try:
            series = fred.get_series(series_id, start_refined, end_refined)
            series.name = series_name
            series_list.append(series)
            logger.debug(f"Successfully fetched {series_name} ({series_id})")
        except Exception as e:
            logger.warning(f"Failed to fetch {series_name} ({series_id}): {e}")
            failed_series.append(series_id)

    if not series_list:
        raise RuntimeError(f"Failed to fetch any FRED series. Failed: {failed_series}")

    if failed_series:
        logger.warning(f"Partially loaded data. Missing series: {failed_series}")

    # Merge all series with outer join
    df = series_list[0].to_frame()
    for series in series_list[1:]:
        df = pd.merge(
            df,
            series.to_frame(),
            left_index=True,
            right_index=True,
            how="outer",
        )

    # Forward fill missing values
    df = df.ffill()

    # Set proper datetime index
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"

    logger.info(f"Fetched {len(df)} rows, {len(df.columns)} columns from FRED")
    return df


def load_cached_macro(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Load cached macroeconomic data from CSV.

    Parameters
    ----------
    filepath : Path, optional
        Path to CSV file. Uses default if not provided.

    Returns
    -------
    pd.DataFrame
        DataFrame with macroeconomic indicators
    """
    if filepath is None:
        filepath = MACRO_CSV

    df = pd.read_csv(filepath)

    # Try to find the date column
    date_cols = ["date", "Date", "datetime", "Datetime", "index"]
    date_col = None
    for col in date_cols:
        if col in df.columns:
            date_col = col
            break

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col)
    else:
        # If no date column, generate monthly dates from START_DATE
        # This handles the case where the original notebook saved without index
        dates = pd.date_range(start=START_DATE, periods=len(df), freq="MS")
        df.index = dates

    df.index.name = "date"

    return df


def save_macro_data(df: pd.DataFrame, filepath: Optional[Path] = None) -> None:
    """
    Save macroeconomic data to CSV.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save
    filepath : Path, optional
        Output path. Uses default if not provided.
    """
    if filepath is None:
        filepath = MACRO_CSV

    df.to_csv(filepath, index=True)
    logger.info(f"Saved macroeconomic data to {filepath}")


if __name__ == "__main__":
    # Test data loading
    print("Fetching FRED data...")
    df = fetch_fred_data()
    print(f"Loaded {len(df)} rows, columns: {list(df.columns)}")
    print(df.head())
    print(df.tail())
