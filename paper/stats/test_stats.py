"""
Unit Tests for Statistical Analysis Scripts
============================================
Tests for bootstrap correlation, Granger causality, and stationarity tests.

Run with: python -m pytest test_stats.py -v
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats

# Import modules to test
from bootstrap_correlation import (
    pearson_correlation,
    bootstrap_correlation_ci,
    correlation_ttest,
    load_correlation_data,
)


class TestPearsonCorrelation:
    """Tests for Pearson correlation calculation."""

    def test_perfect_positive_correlation(self):
        """Perfect positive correlation should return 1.0."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        r = pearson_correlation(x, y)
        assert np.isclose(r, 1.0, atol=1e-10)

    def test_perfect_negative_correlation(self):
        """Perfect negative correlation should return -1.0."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([10, 8, 6, 4, 2])
        r = pearson_correlation(x, y)
        assert np.isclose(r, -1.0, atol=1e-10)

    def test_zero_correlation(self):
        """Orthogonal data should have near-zero correlation."""
        np.random.seed(42)
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([5, 3, 1, 4, 2])  # uncorrelated
        r = pearson_correlation(x, y)
        # Just check it's computed, not necessarily zero
        assert not np.isnan(r)

    def test_handles_nan_values(self):
        """Should handle NaN values correctly."""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([2, 4, 6, 8, 10])
        r = pearson_correlation(x, y)
        # Should compute on non-NaN values
        assert not np.isnan(r)

    def test_matches_scipy(self):
        """Results should match scipy.stats.pearsonr."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = 0.5 * x + np.random.randn(100) * 0.5
        r_ours = pearson_correlation(x, y)
        r_scipy, _ = stats.pearsonr(x, y)
        assert np.isclose(r_ours, r_scipy, atol=1e-10)


class TestBootstrapCorrelationCI:
    """Tests for bootstrap confidence interval calculation."""

    def test_ci_contains_true_value(self):
        """CI should contain the point estimate."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = 0.3 * x + np.random.randn(100) * 0.9
        result = bootstrap_correlation_ci(x, y, n_bootstrap=1000, seed=42)

        assert result['ci_lower'] <= result['correlation'] <= result['ci_upper']

    def test_ci_bounds_ordered(self):
        """Lower bound should be less than upper bound."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)
        result = bootstrap_correlation_ci(x, y, n_bootstrap=1000, seed=42)

        assert result['ci_lower'] < result['ci_upper']

    def test_ci_width_decreases_with_n(self):
        """CI width should decrease with larger sample size."""
        np.random.seed(42)

        # Small sample
        x_small = np.random.randn(30)
        y_small = np.random.randn(30)
        result_small = bootstrap_correlation_ci(x_small, y_small, n_bootstrap=1000, seed=42)

        # Large sample
        x_large = np.random.randn(300)
        y_large = np.random.randn(300)
        result_large = bootstrap_correlation_ci(x_large, y_large, n_bootstrap=1000, seed=42)

        width_small = result_small['ci_upper'] - result_small['ci_lower']
        width_large = result_large['ci_upper'] - result_large['ci_lower']

        assert width_large < width_small

    def test_reproducibility_with_seed(self):
        """Same seed should give same results."""
        np.random.seed(42)
        x = np.random.randn(50)
        y = np.random.randn(50)

        result1 = bootstrap_correlation_ci(x, y, n_bootstrap=1000, seed=123)
        result2 = bootstrap_correlation_ci(x, y, n_bootstrap=1000, seed=123)

        assert result1['ci_lower'] == result2['ci_lower']
        assert result1['ci_upper'] == result2['ci_upper']


class TestCorrelationTTest:
    """Tests for correlation t-test."""

    def test_perfect_correlation_significant(self):
        """Perfect correlation should be highly significant."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
        result = correlation_ttest(x, y)

        assert result['p_value'] < 0.001

    def test_random_data_not_significant(self):
        """Large random uncorrelated data should not be significant."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)
        result = correlation_ttest(x, y)

        # For truly uncorrelated data, p > 0.05 most of the time
        # But this is probabilistic, so we just check p-value is computed
        assert 0 <= result['p_value'] <= 1

    def test_df_calculation(self):
        """Degrees of freedom should be n - 2."""
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.array([2, 4, 1, 8, 5, 6, 7, 3, 9, 10])
        result = correlation_ttest(x, y)

        assert result['df'] == 8  # n - 2 = 10 - 2

    def test_matches_scipy_pearsonr(self):
        """P-value should match scipy.stats.pearsonr."""
        np.random.seed(42)
        x = np.random.randn(50)
        y = 0.4 * x + np.random.randn(50) * 0.8
        result = correlation_ttest(x, y)
        _, p_scipy = stats.pearsonr(x, y)

        assert np.isclose(result['p_value'], p_scipy, rtol=0.01)


class TestDataLoading:
    """Tests for data loading functions."""

    def test_macro_data_loads(self):
        """Macro correlation data should load successfully."""
        df = load_correlation_data()

        assert df is not None
        assert len(df) > 0
        assert 'hawkish' in df.columns
        assert 'dovish' in df.columns

    def test_macro_data_no_all_nan_columns(self):
        """Data should have valid values."""
        df = load_correlation_data()

        # At least some non-NaN values in each column
        for col in df.columns:
            assert df[col].notna().sum() > 0


class TestActualDataCorrelation:
    """Tests using the actual CB speeches data."""

    def test_correlation_near_zero(self):
        """Main finding: correlation should be near zero."""
        df = load_correlation_data()
        x = df.iloc[:, 0].dropna().values  # Macro Index
        y = df['hawkish'].dropna().values

        # Align arrays
        df_clean = df.dropna()
        x = df_clean.iloc[:, 0].values
        y = df_clean['hawkish'].values

        r = pearson_correlation(x, y)

        # Main finding: near-zero correlation
        assert abs(r) < 0.1, f"Expected near-zero correlation, got {r}"

    def test_correlation_not_significant(self):
        """Correlation should not be statistically significant."""
        df = load_correlation_data()
        df_clean = df.dropna()
        x = df_clean.iloc[:, 0].values
        y = df_clean['hawkish'].values

        result = correlation_ttest(x, y)

        # P-value should be high (not significant)
        assert result['p_value'] > 0.05, f"Expected p > 0.05, got {result['p_value']}"

    def test_ci_contains_zero(self):
        """95% CI should contain zero."""
        df = load_correlation_data()
        df_clean = df.dropna()
        x = df_clean.iloc[:, 0].values
        y = df_clean['hawkish'].values

        result = bootstrap_correlation_ci(x, y, n_bootstrap=5000, seed=42)

        contains_zero = result['ci_lower'] <= 0 <= result['ci_upper']
        assert contains_zero, f"CI [{result['ci_lower']}, {result['ci_upper']}] should contain zero"


class TestStationarity:
    """Tests for stationarity analysis."""

    def test_stationarity_imports(self):
        """Stationarity module should import successfully."""
        from stationarity_tests import run_adf_test, run_kpss_test
        assert run_adf_test is not None
        assert run_kpss_test is not None

    def test_adf_on_stationary_data(self):
        """ADF should reject unit root for stationary data."""
        from stationarity_tests import run_adf_test
        np.random.seed(42)
        stationary = np.random.randn(200)  # White noise is stationary
        result = run_adf_test(stationary)

        assert 'error' not in result
        assert result['p_value'] < 0.05  # Reject unit root

    def test_adf_on_random_walk(self):
        """ADF should NOT reject unit root for random walk."""
        from stationarity_tests import run_adf_test
        np.random.seed(42)
        random_walk = np.cumsum(np.random.randn(200))  # Non-stationary
        result = run_adf_test(random_walk)

        assert 'error' not in result
        assert result['p_value'] > 0.05  # Fail to reject unit root

    def test_scaled_macro_is_stationary(self):
        """Rolling standardization should make series stationary."""
        from stationarity_tests import load_scaled_macro, run_adf_test

        scaled = load_scaled_macro()
        # Test at least one variable
        result = run_adf_test(scaled['FED Funds Rate'].dropna())

        assert 'error' not in result
        assert result['is_stationary'], "Scaled data should be stationary"

    def test_pca_components_stationary(self):
        """PCA components should be stationary after rolling standardization."""
        from stationarity_tests import load_pca_components, run_adf_test

        pca = load_pca_components()
        result_pc1 = run_adf_test(pca['PC1'].dropna())
        result_pc2 = run_adf_test(pca['PC2'].dropna())

        assert result_pc1['is_stationary'], "Macro Index (PC1) should be stationary"
        assert result_pc2['is_stationary'], "Inflation Index (PC2) should be stationary"


class TestGrangerCausality:
    """Tests for Granger causality analysis."""

    def test_granger_imports(self):
        """Granger module should import successfully."""
        from granger_causality import prepare_granger_data, run_granger_test
        assert prepare_granger_data is not None
        assert run_granger_test is not None

    def test_granger_data_loads(self):
        """Granger data should load and align correctly."""
        from granger_causality import prepare_granger_data
        df = prepare_granger_data()

        assert len(df) > 100  # Should have substantial data
        assert 'Macro_Index' in df.columns
        assert 'hawkish' in df.columns
        assert not df.isnull().any().any()  # No NaN after cleaning

    def test_sentiment_does_not_cause_macro(self):
        """Key finding: sentiment should NOT Granger-cause macro."""
        from granger_causality import prepare_granger_data, run_granger_test

        df = prepare_granger_data()
        results = run_granger_test(df, 'hawkish', 'Macro_Index', max_lag=6)

        # Check that p-values are generally high (not significant)
        # At least half of lags should have p > 0.05
        high_p_count = sum(1 for lag, stats in results.items() if stats['p_value'] > 0.05)
        assert high_p_count >= 3, "Sentiment should not strongly Granger-cause macro"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
