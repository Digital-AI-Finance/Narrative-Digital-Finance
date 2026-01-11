"""
Run all 12 chart scripts sequentially with error handling.
"""
import subprocess
import sys
from pathlib import Path
import time

CHARTS_DIR = Path(__file__).parent

CHART_FOLDERS = [
    "01_scaled_macro_timeseries",
    "02_principal_components",
    "03_macro_strength_breakpoints",
    "04_inflation_index_breakpoints",
    "05_speech_count_distribution",
    "06_inflation_sentiment_combined",
    "07_rolling_betas_macro",
    "08_rolling_r2_macro",
    "09_rolling_betas_inflation",
    "10_rolling_r2_inflation",
    "11_correlation_matrix",
    "12_pca_loadings_heatmap",
]


def run_chart(folder_name: str) -> bool:
    """Run a single chart script and return success status."""
    chart_path = CHARTS_DIR / folder_name / "chart.py"

    if not chart_path.exists():
        print(f"  [SKIP] {folder_name}: chart.py not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(chart_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(chart_path.parent)
        )

        if result.returncode == 0:
            pdf_path = chart_path.parent / "chart.pdf"
            if pdf_path.exists():
                print(f"  [OK] {folder_name}")
                return True
            else:
                print(f"  [WARN] {folder_name}: Script ran but no PDF generated")
                return False
        else:
            print(f"  [FAIL] {folder_name}: {result.stderr[:100]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {folder_name}")
        return False
    except Exception as e:
        print(f"  [ERROR] {folder_name}: {e}")
        return False


def main():
    """Run all charts and report results."""
    print("=" * 60)
    print("GENERATING ALL 12 CHARTS")
    print("=" * 60)

    start_time = time.time()
    results = {}

    for folder in CHART_FOLDERS:
        results[folder] = run_chart(folder)

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    success = sum(1 for v in results.values() if v)
    failed = len(results) - success

    print(f"Total: {len(results)} charts")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Time: {elapsed:.1f} seconds")

    if failed > 0:
        print()
        print("Failed charts:")
        for folder, ok in results.items():
            if not ok:
                print(f"  - {folder}")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
