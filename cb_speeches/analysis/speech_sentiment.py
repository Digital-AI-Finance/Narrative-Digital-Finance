"""
Central Bank speech sentiment analysis and aggregation.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import logging

from .config import (
    SPEECHES_PARQUET,
    START_DATE,
    END_DATE,
    ROLLING_WINDOW,
)

logger = logging.getLogger(__name__)

# Valid sentiment values
VALID_SENTIMENTS = {"hawkish", "dovish", "neutral"}


def load_us_speeches(filepath: Optional[Path] = None) -> pd.DataFrame:
    """
    Load US Federal Reserve speeches from parquet file.

    Parameters
    ----------
    filepath : Path, optional
        Path to parquet file. Uses default if not provided.

    Returns
    -------
    pd.DataFrame
        DataFrame with US speeches, indexed by datetime

    Raises
    ------
    FileNotFoundError
        If the parquet file does not exist
    ValueError
        If required columns are missing or sentiment values are invalid
    """
    if filepath is None:
        filepath = SPEECHES_PARQUET

    # Validate file exists
    if not filepath.exists():
        raise FileNotFoundError(f"Speeches file not found: {filepath}")

    # Load parquet
    df = pd.read_parquet(filepath)
    logger.info(f"Loaded {len(df)} total speeches from {filepath}")

    # Validate required columns
    required_cols = {"datetime", "country_code", "sentiment"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Set datetime index
    df.set_index("datetime", inplace=True)

    # Filter for US speeches
    df = df[df["country_code"] == "US"]
    logger.info(f"Filtered to {len(df)} US speeches")

    # Validate sentiment values exist
    if "sentiment" not in df.columns:
        raise ValueError("'sentiment' column missing from data")

    # Check for unexpected sentiment values
    unique_sentiments = set(df["sentiment"].dropna().unique())
    unexpected = unique_sentiments - VALID_SENTIMENTS
    if unexpected:
        logger.warning(f"Unexpected sentiment values found: {unexpected}")

    # Validate hawkish/dovish sentiments exist
    hawkish_count = (df["sentiment"] == "hawkish").sum()
    dovish_count = (df["sentiment"] == "dovish").sum()

    if hawkish_count == 0:
        logger.warning("No 'hawkish' sentiment values found in data")
    if dovish_count == 0:
        logger.warning("No 'dovish' sentiment values found in data")

    logger.info(f"Sentiment distribution: hawkish={hawkish_count}, dovish={dovish_count}")

    # Create binary sentiment columns
    df["hawkish"] = (df["sentiment"] == "hawkish").astype(int)
    df["dovish"] = (df["sentiment"] == "dovish").astype(int)

    return df


def aggregate_monthly_sentiment(
    speeches: pd.DataFrame,
    start_date: str = START_DATE,
    end_date: str = END_DATE,
    shift_periods: int = 1,
    standardize: bool = True,
    window: int = ROLLING_WINDOW,
) -> pd.DataFrame:
    """
    Aggregate speech sentiment to monthly frequency.

    Parameters
    ----------
    speeches : pd.DataFrame
        DataFrame with speech data (must have 'hawkish' and 'dovish' columns)
    start_date : str
        Start date for reindexing
    end_date : str
        End date for reindexing
    shift_periods : int
        Number of periods to shift forward (to avoid lookahead bias)
    standardize : bool
        Whether to apply rolling standardization
    window : int
        Rolling window for standardization

    Returns
    -------
    pd.DataFrame
        Monthly aggregated sentiment DataFrame
    """
    # Extract sentiment columns
    cb_sentiment = speeches[["hawkish", "dovish"]].copy()

    # Convert index to date (removing time component)
    cb_sentiment.index = cb_sentiment.index.date

    # Aggregate by date (sum within each day)
    cb_sentiment = cb_sentiment.groupby(cb_sentiment.index).sum()

    # Reindex to full date range
    full_range = pd.date_range(start_date, end_date, freq="D")
    cb_sentiment = cb_sentiment.reindex(full_range).fillna(0.0)

    # Resample to month-start and shift to avoid lookahead bias
    cb_sentiment = cb_sentiment.resample("MS").sum()

    if shift_periods > 0:
        cb_sentiment = cb_sentiment.shift(shift_periods)

    # Apply rolling standardization
    if standardize:
        rolling_mean = cb_sentiment.rolling(window=window).mean()
        rolling_std = cb_sentiment.rolling(window=window).std()
        rolling_std = rolling_std.replace(0, np.nan)
        cb_sentiment = (cb_sentiment - rolling_mean) / rolling_std

    return cb_sentiment


def get_monthly_speech_counts(
    speeches: pd.DataFrame,
) -> pd.Series:
    """
    Get monthly speech count distribution.

    Parameters
    ----------
    speeches : pd.DataFrame
        DataFrame with speech data

    Returns
    -------
    pd.Series
        Monthly speech counts
    """
    return speeches.resample("ME").size()


def get_sentiment_summary(speeches: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary statistics of speech sentiment.

    Parameters
    ----------
    speeches : pd.DataFrame
        DataFrame with speech data

    Returns
    -------
    pd.DataFrame
        Summary statistics
    """
    total = len(speeches)
    hawkish = speeches["hawkish"].sum()
    dovish = speeches["dovish"].sum()
    neutral = total - hawkish - dovish

    return pd.DataFrame({
        "Count": [hawkish, dovish, neutral, total],
        "Percentage": [
            hawkish / total * 100,
            dovish / total * 100,
            neutral / total * 100,
            100.0,
        ],
    }, index=["Hawkish", "Dovish", "Neutral", "Total"])


if __name__ == "__main__":
    # Test speech sentiment analysis
    print("Loading US speeches...")
    speeches = load_us_speeches()
    print(f"Loaded {len(speeches)} US speeches")

    print("\nSentiment summary:")
    print(get_sentiment_summary(speeches))

    print("\nAggregating monthly sentiment...")
    monthly = aggregate_monthly_sentiment(speeches)
    print(f"\nMonthly sentiment shape: {monthly.shape}")
    print(monthly.dropna().head(10))
