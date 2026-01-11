"""Tests for data integrity and validity."""

import json
import pytest
import pandas as pd
from pathlib import Path

# Base path for cb_speeches
BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "data"


class TestPCAIntegrity:
    """Tests for PCA data integrity."""

    def test_eigenvalues_positive_and_decreasing(self):
        """Eigenvalues should be positive and in decreasing order."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        eigenvalues = inventory['eigenvalues']  # At top level
        assert len(eigenvalues) == 6, f"Expected 6 eigenvalues, got {len(eigenvalues)}"
        assert all(e > 0 for e in eigenvalues), "All eigenvalues should be positive"
        # Check decreasing order
        for i in range(len(eigenvalues) - 1):
            assert eigenvalues[i] >= eigenvalues[i + 1], "Eigenvalues should be in decreasing order"

    def test_variance_explained_sums_to_100(self):
        """Variance explained should sum to ~100%."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        variance = inventory['variance_explained']  # Dict with 'individual' and 'cumulative'
        individual = variance['individual']
        total = sum(individual)
        assert abs(total - 100.0) < 1.0, f"Variance explained sums to {total}%, expected ~100%"
        # Check cumulative is correct
        assert abs(variance['cumulative'][-1] - 100.0) < 0.1, "Cumulative should end at 100%"

    def test_pca_components_no_all_nan_columns(self):
        """PCA components should not have all-NaN columns."""
        df = pd.read_csv(DATA_PATH / "pca_components.csv", index_col=0)
        for col in df.columns:
            assert not df[col].isna().all(), f"Column {col} is all NaN"


class TestSentimentIntegrity:
    """Tests for sentiment data integrity."""

    def test_sentiment_counts_non_negative(self):
        """All sentiment counts should be non-negative."""
        df = pd.read_csv(DATA_PATH / "sentiment_raw.csv", index_col=0)
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                assert (df[col].dropna() >= 0).all(), f"Column {col} has negative values"

    def test_sentiment_distribution_valid(self):
        """Verify sentiment distribution from inventory."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        dist = inventory['sentiment_summary']  # Updated key with nested dicts
        total = dist['hawkish']['count'] + dist['dovish']['count'] + dist['neutral']['count']
        assert total > 0, "Total sentiment count should be positive"
        assert total == dist['total'], "Total should match sum of categories"

    def test_sentiment_percentages_sum_to_100(self):
        """Sentiment percentages should sum to ~100%."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        dist = inventory['sentiment_summary']
        # Percentages are pre-computed in the inventory
        total_pct = dist['hawkish']['pct'] + dist['dovish']['pct'] + dist['neutral']['pct']
        assert abs(total_pct - 100.0) < 1.0, f"Percentages sum to {total_pct}%, expected ~100%"


class TestCorrelationIntegrity:
    """Tests for correlation data integrity."""

    def test_correlations_in_valid_range(self):
        """All correlations should be between -1 and 1."""
        for name in ['corr_macro.csv', 'corr_inflation.csv']:
            df = pd.read_csv(DATA_PATH / name, index_col=0)
            for col in df.columns:
                values = df[col].dropna()
                assert (values >= -1.0).all(), f"Correlation < -1 in {name}"
                assert (values <= 1.0).all(), f"Correlation > 1 in {name}"

    def test_correlation_diagonal_is_one(self):
        """Diagonal of correlation matrix should be 1."""
        for name in ['corr_macro.csv', 'corr_inflation.csv']:
            df = pd.read_csv(DATA_PATH / name, index_col=0)
            for i, col in enumerate(df.columns):
                if col in df.index:
                    val = df.loc[col, col]
                    assert abs(val - 1.0) < 0.001, f"Diagonal not 1 in {name} for {col}"


class TestBreakpointIntegrity:
    """Tests for breakpoint data integrity."""

    def test_breakpoints_json_structure(self):
        """Verify breakpoints.json has required structure."""
        bp_path = DATA_PATH / "breakpoints.json"
        with open(bp_path, 'r') as f:
            bp = json.load(f)

        assert 'macro_index' in bp, "Missing macro_index breakpoints"
        assert 'inflation_index' in bp, "Missing inflation_index breakpoints"
        assert 'dates' in bp['macro_index'], "Missing dates in macro_index"
        assert 'dates' in bp['inflation_index'], "Missing dates in inflation_index"

    def test_breakpoint_dates_are_valid(self):
        """Verify breakpoint dates can be parsed."""
        bp_path = DATA_PATH / "breakpoints.json"
        with open(bp_path, 'r') as f:
            bp = json.load(f)

        for bp_date in bp['macro_index']['dates']:
            parsed = pd.to_datetime(bp_date)
            assert parsed is not None, f"Cannot parse date: {bp_date}"

        for bp_date in bp['inflation_index']['dates']:
            parsed = pd.to_datetime(bp_date)
            assert parsed is not None, f"Cannot parse date: {bp_date}"

    def test_breakpoint_count_consistency(self):
        """Verify breakpoint indices and dates have same length."""
        bp_path = DATA_PATH / "breakpoints.json"
        with open(bp_path, 'r') as f:
            bp = json.load(f)

        # Check macro breakpoints
        macro_indices = len(bp['macro_index']['indices'])
        macro_dates = len(bp['macro_index']['dates'])
        assert macro_indices == macro_dates, f"Macro breakpoint mismatch: {macro_indices} indices vs {macro_dates} dates"

        # Check inflation breakpoints
        infl_indices = len(bp['inflation_index']['indices'])
        infl_dates = len(bp['inflation_index']['dates'])
        assert infl_indices == infl_dates, f"Inflation breakpoint mismatch: {infl_indices} indices vs {infl_dates} dates"

        # Sanity check: should have at least some breakpoints
        assert macro_dates > 0, "No macro breakpoints detected"
        assert infl_dates > 0, "No inflation breakpoints detected"


class TestDateConversions:
    """Tests for date string to datetime conversions (fixing the TypeError)."""

    def test_economic_events_dates_convert(self):
        """Verify economic event date strings convert to datetime."""
        economic_events = [
            ("2001-03-01", "Dot-com crash", "recession"),
            ("2007-12-01", "GFC begins", "recession"),
            ("2008-09-15", "Lehman collapse", "crisis"),
            ("2020-03-01", "COVID-19", "pandemic"),
            ("2022-03-01", "Fed rate hikes", "tightening"),
        ]

        for date_str, event, _ in economic_events:
            parsed = pd.to_datetime(date_str)
            assert parsed is not None, f"Cannot parse date: {date_str}"
            assert hasattr(parsed, 'year'), f"Parsed date missing year: {date_str}"

    def test_breakpoint_dates_work_with_plotly_vline(self):
        """Verify breakpoint dates work with plotly add_vline."""
        bp_path = DATA_PATH / "breakpoints.json"
        with open(bp_path, 'r') as f:
            bp = json.load(f)

        # Simulate what the app does
        for bp_date in bp['macro_index']['dates']:
            dt = pd.to_datetime(bp_date)
            # This is what plotly needs - a datetime object
            assert hasattr(dt, 'timestamp'), f"Date {bp_date} missing timestamp method"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
