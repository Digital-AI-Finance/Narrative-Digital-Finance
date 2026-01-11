"""
Principal Component Analysis for macroeconomic index construction.
"""
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from typing import Tuple, Optional
import logging

from .config import RANDOM_STATE, PCA_VARIANCE_THRESHOLD

logger = logging.getLogger(__name__)


def fit_pca(
    data: pd.DataFrame,
    n_components: Optional[int] = None,
    random_state: int = RANDOM_STATE,
) -> Tuple[PCA, pd.DataFrame]:
    """
    Fit PCA on standardized data and transform.

    Parameters
    ----------
    data : pd.DataFrame
        Standardized input data (should already be scaled)
    n_components : int, optional
        Number of components. If None, keeps all components.
    random_state : int
        Random state for reproducibility

    Returns
    -------
    Tuple[PCA, pd.DataFrame]
        Fitted PCA object and transformed data as DataFrame
    """
    # Input validation
    if data.empty:
        raise ValueError('Input DataFrame cannot be empty')
    if data.isnull().all().any():
        logger.warning('Some columns contain all NaN values')

    pca = PCA(n_components=n_components, random_state=random_state)

    # Fit and transform
    logger.info(f'Fitting PCA with {n_components or "all"} components on {len(data)} samples')
    pca_data = pca.fit_transform(data.values)

    # Create DataFrame with proper column names and index
    pca_cols = [f"PC{i+1}" for i in range(pca.n_components_)]
    pca_df = pd.DataFrame(pca_data, columns=pca_cols, index=data.index)

    return pca, pca_df


def get_loadings(pca: PCA, feature_names: list) -> pd.DataFrame:
    """
    Extract PCA loadings as a DataFrame.

    Parameters
    ----------
    pca : PCA
        Fitted PCA object
    feature_names : list
        Names of original features

    Returns
    -------
    pd.DataFrame
        Loadings DataFrame with components as rows and features as columns
    """
    pca_cols = [f"PC{i+1}" for i in range(pca.n_components_)]

    loadings = pd.DataFrame(
        pca.components_ * 100,  # Scale to percentages
        index=pca_cols,
        columns=feature_names,
    )

    # Add explained variance as a column
    loadings["Explained Variance"] = pca.explained_variance_ratio_ * 100

    return loadings


def get_components(pca_df: pd.DataFrame, components: list = None) -> pd.DataFrame:
    """
    Extract specific principal components.

    Parameters
    ----------
    pca_df : pd.DataFrame
        DataFrame with all PCA components
    components : list, optional
        List of component names to extract (e.g., ['PC1', 'PC2'])

    Returns
    -------
    pd.DataFrame
        DataFrame with selected components
    """
    if components is None:
        components = ["PC1", "PC2"]

    return pca_df[components]


def get_n_components_threshold(
    pca: PCA,
    threshold: float = PCA_VARIANCE_THRESHOLD,
) -> int:
    """
    Get number of components explaining a given variance threshold.

    Parameters
    ----------
    pca : PCA
        Fitted PCA object
    threshold : float
        Variance threshold (0-1)

    Returns
    -------
    int
        Number of components needed
    """
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumulative_variance >= threshold) + 1
    return int(n_components)


def get_variance_explained(pca: PCA) -> pd.DataFrame:
    """
    Get variance explained by each component.

    Parameters
    ----------
    pca : PCA
        Fitted PCA object

    Returns
    -------
    pd.DataFrame
        DataFrame with variance statistics
    """
    pca_cols = [f"PC{i+1}" for i in range(pca.n_components_)]

    return pd.DataFrame({
        "Component": pca_cols,
        "Variance Explained": pca.explained_variance_ratio_ * 100,
        "Cumulative Variance": np.cumsum(pca.explained_variance_ratio_) * 100,
    })


if __name__ == "__main__":
    # Test PCA analysis
    np.random.seed(RANDOM_STATE)

    # Create test data
    dates = pd.date_range("2020-01-01", periods=100, freq="M")
    data = pd.DataFrame(
        {
            "A": np.random.randn(100),
            "B": np.random.randn(100),
            "C": np.random.randn(100),
        },
        index=dates,
    )

    print("Fitting PCA...")
    pca, pca_df = fit_pca(data)

    print("\nVariance explained:")
    print(get_variance_explained(pca))

    print("\nLoadings:")
    print(get_loadings(pca, list(data.columns)))

    print(f"\nComponents for 80% variance: {get_n_components_threshold(pca, 0.8)}")
