"""
Rolling regression analysis for beta and R-squared calculations.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import logging

from .config import REGRESSION_WINDOW

logger = logging.getLogger(__name__)


def beta_1pred(
    factors: pd.DataFrame,
    assets: pd.DataFrame,
    window: int = REGRESSION_WINDOW,
    min_periods: Optional[int] = None,
    expanding: bool = False,
    adj_rsquared: bool = False,
    dtype: str = "float64",  # Changed from float32 to prevent precision loss
) -> Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Compute OLS betas and rolling R-squared between factors and assets.

    This function computes rolling regression coefficients (betas) and
    R-squared values between each factor and each asset.

    Parameters
    ----------
    factors : pd.DataFrame
        DataFrame of factor returns/changes (e.g., hawkish, dovish)
    assets : pd.DataFrame
        DataFrame of asset returns/changes (e.g., Macro Index, Inflation Index)
    window : int
        Rolling window size (default: 36 months)
    min_periods : int, optional
        Minimum periods for valid calculation. Defaults to window size.
    expanding : bool
        Use expanding window instead of rolling
    adj_rsquared : bool
        Calculate adjusted R-squared instead of regular R-squared
    dtype : str
        Numeric type for efficiency

    Returns
    -------
    Tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]
        - betas_dict: {factor_name -> DataFrame of rolling betas}
        - r2_dict: {factor_name -> DataFrame of rolling R-squared}
    """
    # Input validation
    if factors.empty or assets.empty:
        raise ValueError('Input DataFrames cannot be empty')
    if not factors.index.equals(assets.index):
        logger.warning('Indices do not match exactly, aligning...')
        common_idx = factors.index.intersection(assets.index)
        factors = factors.loc[common_idx]
        assets = assets.loc[common_idx]

    if min_periods is None:
        min_periods = window

    logger.info(f'Computing rolling betas with window={window} for {len(factors.columns)} factors')
    factors = factors.astype(dtype)
    assets = assets.astype(dtype)

    betas_dict: Dict[str, pd.DataFrame] = {}
    r2_dict: Dict[str, pd.DataFrame] = {}

    for fac in factors.columns:
        x = factors[fac]

        if expanding:
            cov_ax = assets.expanding(min_periods=min_periods).cov(x)
            var_x = x.expanding(min_periods=min_periods).var()
            var_y = assets.expanding(min_periods=min_periods).var()
        else:
            cov_ax = assets.rolling(window, min_periods=min_periods).cov(x)
            var_x = x.rolling(window, min_periods=min_periods).var()
            var_y = assets.rolling(window, min_periods=min_periods).var()

        # Beta = Cov(x, y) / Var(x)
        beta = cov_ax.div(var_x, axis=0)
        betas_dict[fac] = beta

        # R-squared calculation
        if adj_rsquared:
            # Adjusted R-squared = 1 - (1 - R-squared) * (n - 1) / (n - k - 1)
            n_obs = assets.rolling(window, min_periods=min_periods).count()
            raw_r2 = (cov_ax ** 2).div(var_y.mul(var_x, axis=0), axis=0)
            r2_dict[fac] = 1 - (1 - raw_r2) * (n_obs - 1) / (n_obs - 2)
        else:
            # R-squared = Cov(x, y)^2 / (Var(x) * Var(y))
            r2_dict[fac] = (cov_ax ** 2).div(var_y.mul(var_x, axis=0), axis=0)

    return betas_dict, r2_dict


def compute_rolling_analysis(
    index_series: pd.Series,
    sentiment_df: pd.DataFrame,
    window: int = REGRESSION_WINDOW,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compute full rolling regression analysis for an index vs sentiment.

    Parameters
    ----------
    index_series : pd.Series
        The macroeconomic index (e.g., PC1 or PC2)
    sentiment_df : pd.DataFrame
        Sentiment DataFrame with 'hawkish' and 'dovish' columns
    window : int
        Rolling window for regression

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        - merged_df: Merged and differenced DataFrame
        - betas_df: DataFrame of rolling betas for each factor
        - r2_df: DataFrame of rolling R-squared for each factor
    """
    # Input validation
    if index_series.empty:
        raise ValueError('Index series cannot be empty')
    if sentiment_df.empty:
        raise ValueError('Sentiment DataFrame cannot be empty')

    # Merge index and sentiment
    merged = pd.merge(
        index_series.to_frame(),
        sentiment_df,
        left_index=True,
        right_index=True,
        how="outer",
    ).ffill().dropna()

    # Take first differences
    merged_diff = merged.diff().dropna()

    # Get column names
    index_name = index_series.name if index_series.name else "Index"

    # Compute rolling regression
    betas_dict, r2_dict = beta_1pred(
        factors=merged_diff[["hawkish", "dovish"]],
        assets=merged_diff[[index_name]],
        window=window,
        expanding=False,
        adj_rsquared=False,
    )

    # Combine results into DataFrames
    betas_df = pd.DataFrame({
        "hawkish": betas_dict["hawkish"][index_name],
        "dovish": betas_dict["dovish"][index_name],
    })

    r2_df = pd.DataFrame({
        "hawkish": r2_dict["hawkish"][index_name],
        "dovish": r2_dict["dovish"][index_name],
    })

    return merged_diff, betas_df, r2_df


def compute_autocorrelations(df: pd.DataFrame, lag: int = 1) -> Dict[str, float]:
    """
    Compute autocorrelations for each column.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame
    lag : int
        Lag for autocorrelation

    Returns
    -------
    Dict[str, float]
        Dictionary of autocorrelation values
    """
    return {col: df[col].autocorr(lag=lag) for col in df.columns}


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute correlation matrix.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame

    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    return df.corr()


if __name__ == "__main__":
    # Test rolling regression
    np.random.seed(42)

    # Create test data
    dates = pd.date_range("2000-01-01", periods=200, freq="M")

    index_data = pd.Series(np.random.randn(200).cumsum(), index=dates, name="Macro Index")

    sentiment_data = pd.DataFrame({
        "hawkish": np.random.randn(200),
        "dovish": np.random.randn(200),
    }, index=dates)

    print("Computing rolling analysis...")
    merged, betas, r2 = compute_rolling_analysis(index_data, sentiment_data, window=36)

    print("\nCorrelation matrix:")
    print(compute_correlation_matrix(merged).round(4))

    print("\nAutocorrelations:")
    print(compute_autocorrelations(merged))

    print("\nBetas (last 5 rows):")
    print(betas.tail())

    print("\nR-squared (last 5 rows):")
    print(r2.tail())
