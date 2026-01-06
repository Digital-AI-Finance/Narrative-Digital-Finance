"""
Unit Tests for COST Action Network Map Data

Validates that the network map generator produces accurate statistics
by comparing against the source data files.

Author: Prof. Dr. Joerg Osterrieder
Project: Narrative Digital Finance (SNSF Grant IZCOZ0_213370)

Run with: python -m pytest test_network_map.py -v
Or: python test_network_map.py
"""

import unittest
import json
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generate_network_map import (
    load_source_data,
    COST_DATA_SOURCE,
    CODE_MAPPING,
    NAME_TO_CODE,
    ITC_COUNTRIES,
    COUNTRY_COORDS,
    COUNTRY_NAMES
)


class TestSourceDataExists(unittest.TestCase):
    """Test that source data files exist and are readable."""

    def test_cost_data_source_exists(self):
        """COST_Network data directory should exist."""
        self.assertTrue(
            COST_DATA_SOURCE.exists(),
            f"COST data source not found: {COST_DATA_SOURCE}"
        )

    def test_wg_members_file_exists(self):
        """wg_members.json should exist."""
        wg_file = COST_DATA_SOURCE / "wg_members.json"
        self.assertTrue(wg_file.exists(), f"Missing: {wg_file}")

    def test_country_statistics_file_exists(self):
        """country_statistics_full.json should exist."""
        fin_file = COST_DATA_SOURCE / "country_statistics_full.json"
        self.assertTrue(fin_file.exists(), f"Missing: {fin_file}")

    def test_summary_statistics_file_exists(self):
        """summary_statistics.json should exist."""
        sum_file = COST_DATA_SOURCE / "summary_statistics.json"
        self.assertTrue(sum_file.exists(), f"Missing: {sum_file}")


class TestDataLoading(unittest.TestCase):
    """Test that data loads correctly."""

    @classmethod
    def setUpClass(cls):
        """Load data once for all tests."""
        cls.stats = load_source_data()

    def test_stats_not_none(self):
        """Stats should be loaded."""
        self.assertIsNotNone(self.stats)

    def test_has_countries(self):
        """Should have country data."""
        self.assertGreater(len(self.stats.countries), 0)

    def test_total_wg_members_positive(self):
        """Total WG members should be positive."""
        self.assertGreater(self.stats.unique_wg_members, 0)

    def test_total_countries_positive(self):
        """Total countries should be positive."""
        self.assertGreater(self.stats.total_countries, 0)


class TestDataAccuracy(unittest.TestCase):
    """Test data accuracy against source files."""

    @classmethod
    def setUpClass(cls):
        """Load data and source files."""
        cls.stats = load_source_data()

        # Load source WG data
        wg_file = COST_DATA_SOURCE / "wg_members.json"
        with open(wg_file, 'r', encoding='utf-8') as f:
            cls.wg_source = json.load(f)

        # Load source financial data
        fin_file = COST_DATA_SOURCE / "country_statistics_full.json"
        with open(fin_file, 'r', encoding='utf-8') as f:
            cls.fin_source = json.load(f)

        # Load summary statistics
        sum_file = COST_DATA_SOURCE / "summary_statistics.json"
        with open(sum_file, 'r', encoding='utf-8') as f:
            cls.sum_source = json.load(f)

    def test_wg_member_count_matches_source(self):
        """WG member count should match source WG files."""
        # Count unique members from source
        wgs = self.wg_source.get('workingGroups', {})
        all_members = set()
        for wg_key, wg_info in wgs.items():
            members = wg_info.get('members', [])
            for member in members:
                if isinstance(member, dict):
                    name = member.get('name', '')
                    country = member.get('country', '')
                    if name and country not in ['Unknown', 'International Organisations']:
                        all_members.add(name)

        # Allow for small discrepancies due to country name mapping
        source_count = len(all_members)
        our_count = self.stats.unique_wg_members

        self.assertGreater(our_count, 0, "Should have WG members")
        self.assertLessEqual(
            abs(our_count - source_count) / source_count,
            0.05,  # Allow 5% difference due to unmapped countries
            f"WG member count mismatch: source={source_count}, ours={our_count}"
        )

    def test_country_count_reasonable(self):
        """Country count should be in expected range."""
        # Source summary says 36 countries for financial data
        # WG members span ~47 countries (excluding Unknown/Int'l Orgs)
        self.assertGreaterEqual(self.stats.total_countries, 30)
        self.assertLessEqual(self.stats.total_countries, 50)

    def test_total_funding_matches_source(self):
        """Total funding should match source country statistics (excluding unmapped)."""
        # Calculate source total excluding entries with no country code
        source_total_all = sum(c.get('total_amount', 0) for c in self.fin_source)
        unmapped_total = sum(
            c.get('total_amount', 0) for c in self.fin_source
            if not c.get('code')  # Entries without country code
        )
        source_total_mapped = source_total_all - unmapped_total
        our_total = self.stats.total_funding

        # Allow 1% difference due to rounding
        if source_total_mapped > 0:
            diff_pct = abs(our_total - source_total_mapped) / source_total_mapped
            self.assertLess(
                diff_pct, 0.01,
                f"Funding mismatch: source_mapped={source_total_mapped:.0f}, ours={our_total:.0f}"
            )

    def test_itc_classification_correct(self):
        """ITC countries should be correctly classified."""
        # Check a few known ITC countries
        known_itc = ['RO', 'PL', 'TR', 'AL', 'MK']
        known_non_itc = ['CH', 'DE', 'NL', 'GB', 'FR']

        for code in known_itc:
            if code in self.stats.countries:
                self.assertTrue(
                    self.stats.countries[code].is_itc,
                    f"{code} should be ITC"
                )

        for code in known_non_itc:
            if code in self.stats.countries:
                self.assertFalse(
                    self.stats.countries[code].is_itc,
                    f"{code} should be non-ITC"
                )

    def test_switzerland_is_hub(self):
        """Switzerland should be in the data."""
        self.assertIn('CH', self.stats.countries)
        ch = self.stats.countries['CH']
        self.assertGreater(ch.wg_members, 0, "Switzerland should have WG members")

    def test_romania_highest_financial_participation(self):
        """Romania should have highest financial participation (per source)."""
        # From source: RO has highest total_amount
        if 'RO' in self.stats.countries:
            ro_funding = self.stats.countries['RO'].total_funding
            for code, country in self.stats.countries.items():
                if code != 'RO':
                    self.assertLessEqual(
                        country.total_funding,
                        ro_funding * 1.01,  # Allow small margin
                        f"{code} funding ({country.total_funding}) should not exceed Romania ({ro_funding})"
                    )


class TestCodeMappings(unittest.TestCase):
    """Test country code mappings are complete."""

    def test_all_itc_countries_have_names(self):
        """All ITC countries should have names defined."""
        for code in ITC_COUNTRIES:
            self.assertIn(
                code, COUNTRY_NAMES,
                f"ITC country {code} missing from COUNTRY_NAMES"
            )

    def test_all_itc_countries_have_coords(self):
        """All ITC countries should have coordinates defined."""
        for code in ITC_COUNTRIES:
            if code not in ['MD', 'MT']:  # Some small/edge countries may be excluded
                self.assertIn(
                    code, COUNTRY_COORDS,
                    f"ITC country {code} missing from COUNTRY_COORDS"
                )

    def test_code_mapping_valid(self):
        """CODE_MAPPING should map to valid codes."""
        for old_code, new_code in CODE_MAPPING.items():
            self.assertIn(
                new_code, COUNTRY_NAMES,
                f"Mapped code {new_code} (from {old_code}) not in COUNTRY_NAMES"
            )


class TestGeneratedHTML(unittest.TestCase):
    """Test the generated HTML output."""

    @classmethod
    def setUpClass(cls):
        """Load stats and generate HTML."""
        from generate_network_map import generate_map_html
        cls.stats = load_source_data()
        cls.html = generate_map_html(cls.stats)

    def test_html_not_empty(self):
        """Generated HTML should not be empty."""
        self.assertGreater(len(self.html), 1000)

    def test_html_contains_svg(self):
        """HTML should contain SVG element."""
        self.assertIn('<svg', self.html)

    def test_html_contains_tooltip(self):
        """HTML should contain tooltip div."""
        self.assertIn('map-tooltip', self.html)

    def test_html_contains_countries(self):
        """HTML should contain country nodes."""
        self.assertIn('country-node', self.html)

    def test_html_contains_switzerland(self):
        """HTML should contain Switzerland (SNSF hub)."""
        self.assertIn('SNSF Hub', self.html)

    def test_itc_count_in_legend(self):
        """Legend should show correct ITC count."""
        itc_count = sum(
            1 for c in self.stats.countries.values()
            if c.is_itc and c.wg_members > 0 and c.code in COUNTRY_COORDS
        )
        self.assertIn(f'ITC Countries ({itc_count})', self.html)


def run_tests():
    """Run all tests and print summary."""
    print("=" * 70)
    print("COST Action Network Map - Data Validation Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSourceDataExists))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestDataAccuracy))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeMappings))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedHTML))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\nAll tests PASSED!")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
