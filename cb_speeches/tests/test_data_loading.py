"""Tests for data loading functionality."""

import json
import pytest
from pathlib import Path

# Base path for cb_speeches
BASE_PATH = Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "data"


class TestInventoryLoading:
    """Tests for inventory.json loading."""

    def test_inventory_exists(self):
        """Verify inventory.json file exists."""
        inventory_path = DATA_PATH / "inventory.json"
        assert inventory_path.exists(), f"inventory.json not found at {inventory_path}"

    def test_inventory_loads(self):
        """Verify inventory.json loads and is valid JSON."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)
        assert isinstance(inventory, dict), "inventory.json should be a dictionary"

    def test_inventory_has_required_keys(self):
        """Verify inventory.json has all required top-level keys."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        required_keys = [
            'metadata',
            'data_files',
            'summary_stats',
            'breakpoints',
            'eigenvalues',
            'variance_explained',
            'sentiment_summary',
            'correlations'
        ]

        for key in required_keys:
            assert key in inventory, f"Missing required key: {key}"

    def test_metadata_section(self):
        """Verify metadata section has expected fields."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)

        metadata = inventory.get('metadata', {})
        assert 'created' in metadata, "metadata missing created"
        assert 'parameters' in metadata, "metadata missing parameters"
        assert 'fred_series' in metadata, "metadata missing fred_series"


class TestCSVFilesExist:
    """Tests for CSV file existence."""

    @pytest.fixture
    def inventory(self):
        """Load inventory.json."""
        inventory_path = DATA_PATH / "inventory.json"
        with open(inventory_path, 'r') as f:
            return json.load(f)

    def test_raw_macro_csv_exists(self):
        """Verify raw_macro.csv exists."""
        csv_path = DATA_PATH / "raw_macro.csv"
        assert csv_path.exists(), f"raw_macro.csv not found at {csv_path}"

    def test_scaled_macro_csv_exists(self):
        """Verify scaled_macro.csv exists."""
        csv_path = DATA_PATH / "scaled_macro.csv"
        assert csv_path.exists(), f"scaled_macro.csv not found at {csv_path}"

    def test_pca_components_csv_exists(self):
        """Verify pca_components.csv exists."""
        csv_path = DATA_PATH / "pca_components.csv"
        assert csv_path.exists(), f"pca_components.csv not found at {csv_path}"

    def test_pca_loadings_csv_exists(self):
        """Verify pca_loadings.csv exists."""
        csv_path = DATA_PATH / "pca_loadings.csv"
        assert csv_path.exists(), f"pca_loadings.csv not found at {csv_path}"

    def test_sentiment_raw_csv_exists(self):
        """Verify sentiment_raw.csv exists."""
        csv_path = DATA_PATH / "sentiment_raw.csv"
        assert csv_path.exists(), f"sentiment_raw.csv not found at {csv_path}"

    def test_sentiment_standardized_csv_exists(self):
        """Verify sentiment_standardized.csv exists."""
        csv_path = DATA_PATH / "sentiment_standardized.csv"
        assert csv_path.exists(), f"sentiment_standardized.csv not found at {csv_path}"

    def test_correlation_csvs_exist(self):
        """Verify correlation CSV files exist."""
        for name in ['corr_macro.csv', 'corr_inflation.csv']:
            csv_path = DATA_PATH / name
            assert csv_path.exists(), f"{name} not found at {csv_path}"

    def test_breakpoints_json_exists(self):
        """Verify breakpoints.json exists."""
        json_path = DATA_PATH / "breakpoints.json"
        assert json_path.exists(), f"breakpoints.json not found at {json_path}"


class TestDataShapes:
    """Tests for data dimension validation."""

    def test_raw_macro_has_expected_columns(self):
        """Verify raw_macro.csv has 6 macro variables (with renamed columns)."""
        import pandas as pd
        df = pd.read_csv(DATA_PATH / "raw_macro.csv", index_col=0)
        expected_cols = ['FED Funds Rate', 'CPI', 'PPI', 'GDP', 'Unemployment', 'Nonfarm Payrolls']
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_pca_components_has_pc1_pc2(self):
        """Verify pca_components.csv has PC1 and PC2."""
        import pandas as pd
        df = pd.read_csv(DATA_PATH / "pca_components.csv", index_col=0)
        assert 'PC1' in df.columns, "Missing PC1 column"
        assert 'PC2' in df.columns, "Missing PC2 column"

    def test_sentiment_has_hawkish_dovish(self):
        """Verify sentiment data has hawkish and dovish columns."""
        import pandas as pd
        df = pd.read_csv(DATA_PATH / "sentiment_raw.csv", index_col=0)
        assert 'hawkish' in df.columns or 'Hawkish' in df.columns, "Missing hawkish column"
        assert 'dovish' in df.columns or 'Dovish' in df.columns, "Missing dovish column"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
